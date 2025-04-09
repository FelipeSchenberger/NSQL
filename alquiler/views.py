import redis
import json
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import time
from django.shortcuts import redirect
from django.contrib import messages


def index(request):
    # Obtén todas las temporadas desde Redis
    temporadas_keys = redis_client.keys("temporada:*")
    temporadas = []

    for key in temporadas_keys:
        temporada_data = redis_client.hgetall(key)
        temporadas.append(temporada_data)

    # Ordenar las temporadas por el campo 'id' (asegúrate de que sea un número)
    temporadas.sort(key=lambda t: int(t['id']))

    # Renderiza la plantilla con los datos
    return render(request, 'index.html', {'temporadas': temporadas})

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def agregar_temporada(request):
    nueva_temporada = {
        "id": "1",
        "nombre": "Temporada 1",
        "imagen": "ruta/imagen1.jpg"
    }
    redis_client.hmset(f"temporada:{nueva_temporada['id']}", nueva_temporada)
    return JsonResponse({"message": "Temporada agregada a Redis"})

def agregar_episodio(request):
    nuevo_episodio = {
        "id": "1",
        "titulo": "Capítulo 1",
        "imagen": "ruta/imagen1.jpg",
        "temporada_id": "1",
        "estado": "disponible"  # <-- este es el estado inicial correcto
    }

    redis_client.hmset(f"episodio:{nuevo_episodio['temporada_id']}:{nuevo_episodio['id']}", nuevo_episodio)
    return JsonResponse({"message": "Episodio agregado a Redis"})

def list_episodios(request, temporada_id):
    # Obtén los datos de la temporada seleccionada
    temporada_key = f"temporada:{temporada_id}"
    temporada_data = redis_client.hgetall(temporada_key)

    if not temporada_data:
        return JsonResponse({"error": "Temporada no encontrada."}, status=404)

    # Obtén las claves de los episodios de la temporada seleccionada
    episodios_keys = redis_client.keys(f"episodio:{temporada_id}:*")
    episodios = []

    for key in episodios_keys:
        # Verifica si la clave es un hash antes de usar hgetall
        if redis_client.type(key) == "hash":
            episodio_data = redis_client.hgetall(key)
            episodios.append(episodio_data)

    episodios.sort(key=lambda e: int(e['id']))

    # Renderiza la plantilla con los datos de la temporada seleccionada
    return render(request, 'list_episodios.html', {'temporada': temporada_data, 'episodios': episodios})

def alq_episodio(request, episodio_id):
    # Busca la clave exacta del episodio en Redis
    episodio_key = redis_client.keys(f"episodio:*:{episodio_id}")
    if not episodio_key:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    # Obtiene los datos del episodio desde Redis
    episodio_data = redis_client.hgetall(episodio_key[0])

    # Verifica si el episodio ya está marcado como no disponible
    if episodio_data['estado'] != "disponible":
        return JsonResponse({"error": "El episodio no está disponible para alquilar."}, status=400)
    try:
        # Verifica si el episodio ya está reservado temporalmente
        if redis_client.get(f"episodio:{episodio_id}:reservado"):
            return JsonResponse({"error": "El episodio ya está reservado temporalmente."}, status=400)

        # Marca el episodio como reservado temporalmente por 4 minutos (240 segundos)
        redis_client.setex(f"episodio:{episodio_id}:reservado", 240, "true")
    except redis.ConnectionError:
        return JsonResponse({"error": "No se pudo conectar a Redis. Inténtalo más tarde."}, status=500)

    # Devuelve un mensaje de éxito con la información del episodio
    return JsonResponse({
        "message": f"Episodio {episodio_data['titulo']} reservado temporalmente. Tienes 4 minutos para confirmar el pago.",
        "imagen": episodio_data.get("imagen", None)  # Devuelve la URL de la imagen si existe
    })

def reservar_episodio(request, episodio_id):
    # Busca la clave exacta del episodio
    episodio_keys = redis_client.keys(f"episodio:*:{episodio_id}")
    
    if not episodio_keys:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    episodio_key = episodio_keys[0]  # Obtén la primera clave que coincide
    episodio_data = redis_client.hgetall(episodio_key)

    if not episodio_data:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    if episodio_data['estado'] != "disponible":
        return JsonResponse({"error": "El episodio no está disponible para reservar."}, status=400)

    # Reservar el episodio por 4 minutos
    redis_client.hset(episodio_key, "estado", "reservado")  # Actualiza el estado en Redis
    redis_client.setex(f"{episodio_key}:reservado", 240, "true")  # Expira en 4 minutos

    return JsonResponse({"message": f"Episodio {episodio_data['titulo']} reservado por 4 minutos."})

def confirm_pago(request, episodio_id, precio):
    # Busca la clave exacta del episodio
    episodio_keys = redis_client.keys(f"episodio:*:{episodio_id}")
    
    if not episodio_keys:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    episodio_key = episodio_keys[0]
    episodio_data = redis_client.hgetall(episodio_key)

    if not episodio_data:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    if episodio_data['estado'] != "reservado":
        return JsonResponse({"error": "El episodio no está reservado."}, status=400)

    # Confirmar el pago y cambiar el estado a 'alquilado'
    redis_client.hset(episodio_key, "estado", "alquilado")
    redis_client.delete(f"{episodio_key}:reservado")  # Eliminar la reserva

    # Agregar un mensaje de éxito
    messages.success(request, f"Pago confirmado. Episodio '{episodio_data['titulo']}' alquilado por 24 horas.")

    # Redirigir a la página de detalles del episodio
    return redirect('episodio_details', episodio_id=episodio_id)

def verificar_estado_reserva(episodio_key):
    if redis_client.get(f"{episodio_key}:reservado") is None:  # Reserva expirada
        estado_actual = redis_client.hget(episodio_key, "estado")
        if estado_actual == "reservado":
            redis_client.hset(episodio_key, "estado", "disponible")

def episodio_details(request, episodio_id):
    # Busca la clave exacta del episodio
    episodio_keys = redis_client.keys(f"episodio:*:{episodio_id}")
    
    if not episodio_keys:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    episodio_key = episodio_keys[0]  # Obtén la primera clave que coincide
    episodio_data = redis_client.hgetall(episodio_key)

    if not episodio_data:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    # Verificar si la reserva ha expirado
    tiempo_restante = redis_client.ttl(f"{episodio_key}:reservado")
    if tiempo_restante is None or tiempo_restante < 0:  # Reserva expirada
        if episodio_data['estado'] == "reservado":
            redis_client.hset(episodio_key, "estado", "disponible")
            tiempo_restante = 0  # No hay tiempo restante

    return render(request, 'episodio_details.html', {
        'episodio': episodio_data,
        'tiempo_restante': tiempo_restante
    })

def pago(request, episodio_id, precio):
    # Busca la clave exacta del episodio
    episodio_keys = redis_client.keys(f"episodio:*:{episodio_id}")
    
    if not episodio_keys:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    episodio_key = episodio_keys[0]
    episodio_data = redis_client.hgetall(episodio_key)

    if not episodio_data:
        return JsonResponse({"error": "Episodio no encontrado."}, status=404)

    # Verifica si el episodio está reservado
    if episodio_data['estado'] != "reservado":
        return JsonResponse({"error": "El episodio no está reservado."}, status=400)

    # Renderiza la plantilla de pago
    return render(request, 'pago.html', {
        'episodio': episodio_data,
        'precio': precio
    })

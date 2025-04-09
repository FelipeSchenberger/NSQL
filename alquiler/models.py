from django.db import models
import redis 
from django.conf import settings

# Configuración del cliente Redis
try:
    redis_client = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )
    redis_client.ping()  # Verifica la conexión al iniciar
except redis.ConnectionError:
    redis_client = None

class Temporada(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='temporadas/')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if redis_client:
            try:
                redis_client.hset(f"temporada:{self.id}", mapping={
                    "id": self.id,
                    "nombre": self.nombre,
                    "imagen": self.imagen.url if self.imagen else ""
                })
            except redis.ConnectionError:
                pass  # Opcional: podrías loggear el error

    def delete(self, *args, **kwargs):
        if redis_client:
            try:
                redis_client.delete(f"temporada:{self.id}")
            except redis.ConnectionError:
                pass
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Episodio(models.Model):
    titulo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='episodios/', blank=True, null=True)
    descripcion = models.TextField()
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if redis_client:
            try:
                redis_client.hset(f"episodio:{self.temporada.id}:{self.id}", mapping={
                    "id": self.id,
                    "titulo": self.titulo,
                    "imagen": self.imagen.url if self.imagen else "",
                    "descripcion": self.descripcion,
                    "temporada_id": self.temporada.id,
                    "estado": "disponible"
                })
            except redis.ConnectionError:
                pass

    def delete(self, *args, **kwargs):
        if redis_client:
            try:
                redis_client.delete(f"episodio:{self.temporada.id}:{self.id}")
            except redis.ConnectionError:
                pass
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.titulo

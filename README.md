# Para correr la aplicacion se necesita 

## Crear entorno virtual
python3 -m venv nombre 

source nombre/bin/activate

python manage.py createsuperuser

## Dentro del entorno virtual se debe instalar:
pip install django redis pillow

## Levantar los contenedores:
docker-compose up --build

 localhost:8000

Desde el panel de admin se ingresan los datos que se reconstruyen por django y la imagenes estan almacenadas en el proyecto.

Decidi crear dos contenedores, redis-db y django-app, el primero sirve para almacenar la 
informacion de las temporadas y episodios, y el segundo se utiliza para ejecutar el servidor 
en el puerto 8000 o los comando de migraciones, etc

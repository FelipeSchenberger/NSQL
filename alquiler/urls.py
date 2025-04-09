from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Página principal
    path('list/<str:temporada_id>/', views.list_episodios, name='list_episodios'),  # Lista de episodios por temporada
    path('alquiler/<str:episodio_id>/', views.alq_episodio, name='alq_episodio'),  # Alquilar un episodio
    path('confirm/<str:episodio_id>/', views.confirm_pago, name='confirm_pago'),  # Confirmar pago
    path('episodio/<str:episodio_id>/', views.episodio_details, name='episodio_details'),  # Detalles del episodio
    path('reservar/<str:episodio_id>/', views.reservar_episodio, name='reservar_episodio'),  # Reservar un episodio
    path('pago/<str:episodio_id>/<int:precio>/', views.pago, name='pago'),  # Vista de pago
    path('confirmar_pago/<str:episodio_id>/<int:precio>/', views.confirm_pago, name='confirm_pago'),
]
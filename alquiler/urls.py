from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/<str:temporada_id>/', views.list_episodios, name='list_episodios'),
    path('alquiler/<str:episodio_id>/', views.alq_episodio, name='alq_episodio'),
    path('confirm/<str:episodio_id>/', views.confirm_pago, name='confirm_pago'),
    path('episodio/<str:episodio_id>/', views.episodio_details, name='episodio_details'),
    path('reservar/<str:episodio_id>/', views.reservar_episodio, name='reservar_episodio'),
    path('pago/<str:episodio_id>/<int:precio>/', views.pago, name='pago'),
    path('confirmar_pago/<str:episodio_id>/<int:precio>/', views.confirm_pago, name='confirm_pago'),
]
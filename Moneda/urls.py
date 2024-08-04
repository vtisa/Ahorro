from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('registro/', views.registro, name='registro'),
    path('transaccion/', views.realizar_transaccion, name='realizar_transaccion'),
    path('generar_pdf/', views.generar_pdf, name='generar_pdf'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
]
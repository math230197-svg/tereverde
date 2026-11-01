from django.urls import path
from . import views

urlpatterns = [
    path('api/dados/', views.api_dados_publicos, name='dados_publicos'),
    path('api/login/', views.api_login_admin, name='login_admin'),
    path('api/admins/', views.api_gerenciar_admins, name='gerenciar_admins'),
    path('api/eventos/', views.api_gerenciar_eventos, name='gerenciar_eventos'),
    path('api/condicoes/', views.api_atualizar_condicoes, name='atualizar_condicoes'),
    path('api/atualizacoes/', views.api_gerenciar_atualizacoes, name='gerenciar_atualizacoes'),
]
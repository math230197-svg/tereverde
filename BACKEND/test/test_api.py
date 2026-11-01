import os
import sys
import json
from pathlib import Path

# Adiciona a pasta src/ ao caminho do Python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_tereverde.settings')

import django
django.setup()

from django.test import Client

client = Client()

def test_consulta_visitante_publica():
    """Testa se visitantes conseguem consultar condições e eventos."""
    response = client.get('/api/dados/')
    assert response.status_code == 200
    dados = response.json()
    assert 'condicoes' in dados
    assert 'eventos' in dados

def test_login_administrador_sucesso_e_falha():
    """Testa segurança do login para administradores."""
    # Senha incorreta deve retornar 401
    res_falha = client.post(
        '/api/login/',
        data=json.dumps({"username": "admin", "password": "123"}),
        content_type='application/json'
    )
    assert res_falha.status_code == 401

    # Senha correta deve retornar 200 e token
    res_sucesso = client.post(
        '/api/login/',
        data=json.dumps({"username": "admin", "password": "tereverde123"}),
        content_type='application/json'
    )
    assert res_sucesso.status_code == 200
    assert 'token' in res_sucesso.json()

def test_gestao_eventos_protegida():
    """Testa criação e exclusão de evento pelo administrador."""
    headers = {'HTTP_AUTHORIZATION': 'Bearer token-seguro-admin-tereverde-2026'}
    novo = {
        "parque": "PARNASO",
        "titulo": "Trilha Noturna Guiada",
        "data": "2026-12-10",
        "disponibilidade": "15 vagas"
    }
    res_criar = client.post(
        '/api/eventos/',
        data=json.dumps(novo),
        content_type='application/json',
        **headers
    )
    assert res_criar.status_code == 201
    evento_id = res_criar.json()['evento']['id']

    res_deletar = client.delete(
        '/api/eventos/',
        data=json.dumps({"id": evento_id}),
        content_type='application/json',
        **headers
    )
    assert res_deletar.status_code == 200
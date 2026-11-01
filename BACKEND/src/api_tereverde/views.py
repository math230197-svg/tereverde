import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .db import db_manager

TOKEN_MASTER = "token-seguro-admin-tereverde-2026"
TOKENS_COMUNS = {}

def verificar_sessao(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    if token == TOKEN_MASTER:
        return {"username": "admin", "is_master": True}
    return TOKENS_COMUNS.get(token, None)

@csrf_exempt
def api_dados_publicos(request):
    if request.method == 'GET':
        dados = db_manager.obter_dados_publicos()
        return JsonResponse(dados, status=200)
    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def api_login_admin(request):
    if request.method == 'POST':
        corpo = json.loads(request.body.decode('utf-8'))
        usuario = corpo.get('username', '').strip()
        senha = corpo.get('password', '').strip()
        
        # Garante que o master principal seja autenticado corretamente
        if usuario == "admin":
            if senha == "tereverde123": # Ou verificação via db_manager
                return JsonResponse({
                    "mensagem": "Autenticação realizada com sucesso",
                    "token": TOKEN_MASTER,
                    "is_master": True,
                    "username": "admin"
                }, status=200)

        admin_info = db_manager.autenticar_admin(usuario, senha)
        if admin_info:
            is_master_status = True if admin_info["username"] == "admin" else admin_info.get("is_master", False)
            token_gerado = TOKEN_MASTER if is_master_status else f"token_{uuid.uuid4().hex}"
            
            if not is_master_status:
                TOKENS_COMUNS[token_gerado] = admin_info

            return JsonResponse({
                "mensagem": "Autenticação realizada com sucesso",
                "token": token_gerado,
                "is_master": is_master_status,
                "username": admin_info["username"]
            }, status=200)
            
        return JsonResponse({"erro": "Credenciais inválidas"}, status=401)
    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def api_gerenciar_admins(request):
    sessao = verificar_sessao(request)
    if not sessao:
        return JsonResponse({"erro": "Acesso não autorizado"}, status=401)
    
    if not sessao["is_master"]:
        return JsonResponse({"erro": "Acesso negado. Apenas o admin principal pode gerenciar usuários."}, status=403)

    if request.method == 'GET':
        admins = db_manager.listar_admins()
        return JsonResponse({"admins": admins}, status=200)

    if request.method == 'POST':
        corpo = json.loads(request.body.decode('utf-8'))
        novo_usuario = corpo.get('username', '').strip()
        nova_senha = corpo.get('password', '').strip()

        if not novo_usuario or not nova_senha:
            return JsonResponse({"erro": "Usuário e senha são obrigatórios"}, status=400)

        sucesso = db_manager.adicionar_admin(novo_usuario, nova_senha)
        if sucesso:
            return JsonResponse({"mensagem": "Novo administrador criado com sucesso!"}, status=201)
        else:
            return JsonResponse({"erro": "Este nome de usuário já existe."}, status=409)

    if request.method == 'DELETE':
        corpo = json.loads(request.body.decode('utf-8'))
        id_ou_user = corpo.get('id', '')
        
        if id_ou_user == "admin":
            return JsonResponse({"erro": "Não é permitido excluir o admin principal."}, status=403)
        
        removido = db_manager.remover_admin(id_ou_user)
        if removido:
            return JsonResponse({"mensagem": "Administrador removido com sucesso!"}, status=200)
        return JsonResponse({"erro": "Administrador não encontrado ou protegido."}, status=404)

    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def api_gerenciar_eventos(request):
    sessao = verificar_sessao(request)
    if not sessao:
        return JsonResponse({"erro": "Acesso não autorizado"}, status=401)
    
    if not sessao["is_master"]:
        return JsonResponse({"erro": "Acesso negado. Apenas o admin principal pode gerenciar eventos."}, status=403)

    if request.method == 'POST':
        corpo = json.loads(request.body.decode('utf-8'))
        evento = db_manager.adicionar_evento(
            parque=corpo.get('parque', 'PARNASO'),
            titulo=corpo.get('titulo', ''),
            data_evento=corpo.get('data', ''),
            disponibilidade=corpo.get('disponibilidade', 'Disponível')
        )
        return JsonResponse({"mensagem": "Evento criado", "evento": evento}, status=201)

    if request.method == 'PUT':
        corpo = json.loads(request.body.decode('utf-8'))
        atualizado = db_manager.atualizar_evento(
            evento_id=corpo.get('id', ''),
            parque=corpo.get('parque', 'PARNASO'),
            titulo=corpo.get('titulo', ''),
            data_evento=corpo.get('data', ''),
            disponibilidade=corpo.get('disponibilidade', '')
        )
        if atualizado:
            return JsonResponse({"mensagem": "Evento atualizado com sucesso"}, status=200)
        return JsonResponse({"erro": "Evento não encontrado"}, status=404)

    if request.method == 'DELETE':
        corpo = json.loads(request.body.decode('utf-8'))
        removido = db_manager.remover_evento(corpo.get('id', ''))
        if removido:
            return JsonResponse({"mensagem": "Evento removido com sucesso"}, status=200)
        return JsonResponse({"erro": "Evento não encontrado"}, status=404)

    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def api_atualizar_condicoes(request):
    if not verificar_sessao(request):
        return JsonResponse({"erro": "Acesso não autorizado"}, status=401)

    if request.method == 'POST':
        corpo = json.loads(request.body.decode('utf-8'))
        atrativo = db_manager.adicionar_condicao(
            tipo=corpo.get('tipo', 'trilha'),
            parque=corpo.get('parque', 'PARNASO'),
            nome=corpo.get('nome', ''),
            status=corpo.get('status', 'aberto'),
            descricao=corpo.get('descricao', 'ABERTA')
        )
        return JsonResponse({"mensagem": "Atrativo cadastrado", "atrativo": atrativo}, status=201)

    if request.method == 'PUT':
        corpo = json.loads(request.body.decode('utf-8'))
        atualizado = db_manager.atualizar_condicao(
            cond_id=corpo.get('id', ''),
            novo_status=corpo.get('status', 'aberto'),
            nova_descricao=corpo.get('descricao', 'ABERTA')
        )
        if atualizado:
            return JsonResponse({"mensagem": "Condição atualizada com sucesso"}, status=200)
        return JsonResponse({"erro": "Atração não encontrada"}, status=404)

    if request.method == 'DELETE':
        corpo = json.loads(request.body.decode('utf-8'))
        removido = db_manager.remover_condicao(corpo.get('id', ''))
        if removido:
            return JsonResponse({"mensagem": "Removido com sucesso"}, status=200)
        return JsonResponse({"erro": "Atração não encontrada"}, status=404)

    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def api_gerenciar_atualizacoes(request):
    if not verificar_sessao(request):
        return JsonResponse({"erro": "Acesso não autorizado"}, status=401)

    if request.method == 'POST':
        corpo = json.loads(request.body.decode('utf-8'))
        upd = db_manager.adicionar_atualizacao(
            data_str=corpo.get('data', ''),
            texto=corpo.get('texto', '')
        )
        return JsonResponse({"mensagem": "Atualização publicada", "atualizacao": upd}, status=201)

    if request.method == 'PUT':
        corpo = json.loads(request.body.decode('utf-8'))
        atualizado = db_manager.atualizar_atualizacao(
            upd_id=corpo.get('id', ''),
            data_str=corpo.get('data', ''),
            texto=corpo.get('texto', '')
        )
        if atualizado:
            return JsonResponse({"mensagem": "Atualização atualizada com sucesso"}, status=200)
        return JsonResponse({"erro": "Atualização não encontrada"}, status=404)

    if request.method == 'DELETE':
        corpo = json.loads(request.body.decode('utf-8'))
        removido = db_manager.remover_atualizacao(corpo.get('id', ''))
        if removido:
            return JsonResponse({"mensagem": "Atualização removida com sucesso"}, status=200)
        return JsonResponse({"erro": "Atualização não encontrada"}, status=404)

    return JsonResponse({"erro": "Método não permitido"}, status=405)
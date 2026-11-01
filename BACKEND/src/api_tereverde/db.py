import json
import uuid
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

SEED_FILE = Path(settings.BASE_DIR).parent / 'data' / 'seed_data.json'

class DatabaseManager:
    def __init__(self):
        self.use_mongo = False
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping')
            self.db = self.client[settings.MONGO_DB_NAME]
            self.use_mongo = True
            self._seed_mongo()
        except PyMongoError:
            self.use_mongo = False

    def _load_seed_json(self):
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_seed_json(self, data):
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _seed_mongo(self):
        seed_data = self._load_seed_json()
        if self.db.condicoes.count_documents({}) == 0:
            self.db.condicoes.insert_many(seed_data['condicoes'])
        if self.db.eventos.count_documents({}) == 0:
            self.db.eventos.insert_many(seed_data['eventos'])
        if self.db.atualizacoes.count_documents({}) == 0:
            self.db.atualizacoes.insert_many(seed_data.get('atualizacoes', []))
        if self.db.admins.count_documents({}) == 0:
            self.db.admins.insert_one({
                "username": "admin",
                "password_hash": make_password("tereverde123"),
                "is_master": True
            })

    def autenticar_admin(self, username, password):
        if self.use_mongo:
            admin = self.db.admins.find_one({"username": username})
            if admin and check_password(password, admin["password_hash"]):
                return {"username": admin["username"], "is_master": admin.get("is_master", False)}
            return None
        
        dados = self._load_seed_json()
        admins = dados.get("admins", [{"username": "admin", "password_hash": make_password("tereverde123"), "is_master": True}])
        for a in admins:
            if a["username"] == username and check_password(password, a["password_hash"]):
                return {"username": a["username"], "is_master": a.get("is_master", False)}
        return None

    def adicionar_admin(self, username, password):
        if self.use_mongo:
            if self.db.admins.find_one({"username": username}):
                return False
        else:
            dados = self._load_seed_json()
            if "admins" not in dados:
                dados["admins"] = [{"username": "admin", "password_hash": make_password("tereverde123"), "is_master": True}]
            if any(a["username"] == username for a in dados["admins"]):
                return False

        novo_admin = {
            "id": f"adm_{uuid.uuid4().hex[:6]}",
            "username": username,
            "password_hash": make_password(password),
            "is_master": False
        }

        if self.use_mongo:
            self.db.admins.insert_one(novo_admin)
        else:
            dados["admins"].append(novo_admin)
            self._save_seed_json(dados)
        return True

    def listar_admins(self):
        if self.use_mongo:
            admins = list(self.db.admins.find({}, {"_id": 0, "password_hash": 0}))
            for a in admins:
                if "id" not in a:
                    a["id"] = a["username"]
            return admins
        
        dados = self._load_seed_json()
        admins = dados.get("admins", [])
        for a in admins:
            if "id" not in a:
                a["id"] = a["username"]
        return admins

    def remover_admin(self, admin_id_ou_user):
        if self.use_mongo:
            admin_alvo = self.db.admins.find_one({"$or": [{"id": admin_id_ou_user}, {"username": admin_id_ou_user}]})
            if admin_alvo and admin_alvo.get("is_master", False):
                return False
            
            res = self.db.admins.delete_one({"$or": [{"id": admin_id_ou_user}, {"username": admin_id_ou_user}]})
            return res.deleted_count > 0
        
        dados = self._load_seed_json()
        admins = dados.get("admins", [])
        
        novos_admins = []
        removido = False
        for a in admins:
            identificador = a.get("id", a.get("username"))
            if identificador == admin_id_ou_user or a.get("username") == admin_id_ou_user:
                if a.get("is_master", False):
                    novos_admins.append(a)
                else:
                    removido = True
            else:
                novos_admins.append(a)
                
        if removido:
            dados["admins"] = novos_admins
            self._save_seed_json(dados)
            return True
        return False

    def obter_dados_publicos(self):
        if self.use_mongo:
            condicoes = list(self.db.condicoes.find({}, {"_id": 0}))
            eventos = list(self.db.eventos.find({}, {"_id": 0}))
            atualizacoes = list(self.db.atualizacoes.find({}, {"_id": 0}))
            return {"condicoes": condicoes, "eventos": eventos, "atualizacoes": atualizacoes, "storage": "MongoDB"}
        dados = self._load_seed_json()
        dados["storage"] = "JSON Fallback (data/)"
        return dados

    # --- Eventos ---
    def adicionar_evento(self, parque, titulo, data_evento, disponibilidade):
        novo_evento = {
            "id": f"evt_{uuid.uuid4().hex[:6]}",
            "parque": parque,
            "titulo": titulo,
            "data": data_evento,
            "disponibilidade": disponibilidade
        }
        if self.use_mongo:
            self.db.eventos.insert_one(dict(novo_evento))
        else:
            dados = self._load_seed_json()
            dados["eventos"].append(novo_evento)
            self._save_seed_json(dados)
        return novo_evento

    def atualizar_evento(self, evento_id, parque, titulo, data_evento, disponibilidade):
        if self.use_mongo:
            res = self.db.eventos.update_one(
                {"id": evento_id},
                {"$set": {"parque": parque, "titulo": titulo, "data": data_evento, "disponibilidade": disponibilidade}}
            )
            return res.matched_count > 0
        dados = self._load_seed_json()
        for e in dados["eventos"]:
            if e["id"] == evento_id:
                e["parque"] = parque
                e["titulo"] = titulo
                e["data"] = data_evento
                e["disponibilidade"] = disponibilidade
                self._save_seed_json(dados)
                return True
        return False

    def remover_evento(self, evento_id):
        if self.use_mongo:
            res = self.db.eventos.delete_one({"id": evento_id})
            return res.deleted_count > 0
        dados = self._load_seed_json()
        inicial = len(dados["eventos"])
        dados["eventos"] = [e for e in dados["eventos"] if e["id"] != evento_id]
        self._save_seed_json(dados)
        return len(dados["eventos"]) < inicial

    # --- Condições / Atrativos ---
    def adicionar_condicao(self, tipo, parque, nome, status, descricao):
        novo_atrativo = {
            "id": f"cond_{uuid.uuid4().hex[:6]}",
            "tipo": tipo,
            "parque": parque,
            "nome": nome,
            "status": status,
            "descricao": descricao
        }
        if self.use_mongo:
            self.db.condicoes.insert_one(dict(novo_atrativo))
        else:
            dados = self._load_seed_json()
            dados["condicoes"].append(novo_atrativo)
            self._save_seed_json(dados)
        return novo_atrativo

    def atualizar_condicao(self, cond_id, novo_status, nova_descricao):
        if self.use_mongo:
            res = self.db.condicoes.update_one(
                {"id": cond_id},
                {"$set": {"status": novo_status, "descricao": nova_descricao}}
            )
            return res.matched_count > 0
        dados = self._load_seed_json()
        for c in dados["condicoes"]:
            if c["id"] == cond_id:
                c["status"] = novo_status
                c["descricao"] = nova_descricao
                self._save_seed_json(dados)
                return True
        return False

    def remover_condicao(self, cond_id):
        if self.use_mongo:
            res = self.db.condicoes.delete_one({"id": cond_id})
            return res.deleted_count > 0
        dados = self._load_seed_json()
        inicial = len(dados["condicoes"])
        dados["condicoes"] = [c for c in dados["condicoes"] if c["id"] != cond_id]
        self._save_seed_json(dados)
        return len(dados["condicoes"]) < inicial

    # --- Atualizações / Notícias ---
    def adicionar_atualizacao(self, data_str, texto):
        nova_upd = {
            "id": f"upd_{uuid.uuid4().hex[:6]}",
            "data": data_str,
            "texto": texto
        }
        if self.use_mongo:
            self.db.atualizacoes.insert_one(dict(nova_upd))
        else:
            dados = self._load_seed_json()
            if "atualizacoes" not in dados:
                dados["atualizacoes"] = []
            dados["atualizacoes"].insert(0, nova_upd)
            self._save_seed_json(dados)
        return nova_upd

    def atualizar_atualizacao(self, upd_id, data_str, texto):
        if self.use_mongo:
            res = self.db.atualizacoes.update_one(
                {"id": upd_id},
                {"$set": {"data": data_str, "texto": texto}}
            )
            return res.matched_count > 0
        dados = self._load_seed_json()
        for u in dados.get("atualizacoes", []):
            if u["id"] == upd_id:
                u["data"] = data_str
                u["texto"] = texto
                self._save_seed_json(dados)
                return True
        return False

    def remover_atualizacao(self, upd_id):
        if self.use_mongo:
            res = self.db.atualizacoes.delete_one({"id": upd_id})
            return res.deleted_count > 0
        dados = self._load_seed_json()
        if "atualizacoes" not in dados:
            return False
        inicial = len(dados["atualizacoes"])
        dados["atualizacoes"] = [u for u in dados["atualizacoes"] if u["id"] != upd_id]
        self._save_seed_json(dados)
        return len(dados["atualizacoes"]) < inicial

db_manager = DatabaseManager()
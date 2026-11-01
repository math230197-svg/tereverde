# Terê Verde Online - API (Back-end)

API desenvolvida em Python para gerenciar e fornecer dados dinâmicos para a plataforma de ecoturismo e conservação dos parques de Teresópolis (PARNASO, Três Picos e Montanhas de Teresópolis). Este repositório contém a lógica de negócios, gerenciamento do painel administrativo e os endpoints consumidos pelo front-end da aplicação.

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.12
* **Framework:** Django 5.0.6 e Django REST Framework 3.15.1
* **Banco de Dados:** SQLite
* **Integração:** CORS (django-cors-headers) habilitado para comunicação com o front-end.

## ⚙️ Pré-requisitos

Antes de começar, você precisará ter o [Python](https://www.python.org/) e o [Git](https://git-scm.com/) instalados na sua máquina.

## 🛠️ Como rodar o projeto localmente

1. Clone este repositório:
```bash
git clone [https://github.com/math230197-svg/tereverde.git](https://github.com/math230197-svg/tereverde.git)

```

2. Acesse a pasta do back-end do projeto:

```bash
cd tereverde/BACKEND

```

3. Crie e ative um ambiente virtual:

```bash
python -m venv venv

# Ativação no Windows:
venv\Scripts\activate

# Ativação no Linux/Mac:
source venv/bin/activate

```

4. Instale as dependências:

```bash
pip install -r requirements.txt

```

5. Aplique as migrações do banco de dados:

```bash
python src/manage.py migrate

```

6. Carregue os dados iniciais (opcional, se desejar popular o banco):

```bash
python src/manage.py loaddata data/seed_data.json

```

7. Execute o servidor localmente (porta 8000):

```bash
python src/manage.py runserver

```

A API estará disponível em: `http://127.0.0.1:8000`

## 🔗 Endpoints Principais

Abaixo estão as rotas principais utilizadas para a comunicação com a interface de usuário e o painel administrativo:

* **`GET /api/dados/`**: Retorna a lista de atualizações e notícias públicas dos parques.
* **`POST /api/dados/`**: Cadastra uma nova atualização no sistema (restrito a administradores).
* **`DELETE /api/dados/{id}`**: Exclui uma atualização específica.

## 🛡️ Notas de Segurança e CORS

O back-end está configurado para aceitar requisições de origens específicas (CORS). Se o front-end for hospedado no GitHub Pages, certifique-se de adicionar a URL pública do repositório front-end (`https://math230197-svg.github.io/tereverde`) na lista de origens permitidas (`ALLOWED_HOSTS` / `CORS_ALLOWED_ORIGINS`) nas configurações da API antes do deploy em produção.

## 👥 Desenvolvedor

**Matheus Correia da Silva**

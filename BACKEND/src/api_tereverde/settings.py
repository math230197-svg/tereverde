from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'mvp-tere-verde-chave-secreta-desenvolvimento'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'corsheaders',
] 

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

# Permite que o seu Front-End (HTML/JS) acesse a API sem bloqueio de CORS
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'api_tereverde.urls'

# Banco auxiliar mínimo para utilitários internos do Django; dados principais ficam no MongoDB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'data' / 'auth_meta.sqlite3',
    }
}

# Configuração do MongoDB
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "tere_verde_db"

USE_TZ = True
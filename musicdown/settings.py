import os
import dj_database_url  # ⬅️ AGREGADO: Necesario para leer la URL de PostgreSQL
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'cambia_en_produccion')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'downloader',
    'crispy_forms',  # ⬅️ AGREGADO: Para el manejo de formularios
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'musicdown.urls'

TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[BASE_DIR / 'downloader' / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'musicdown.wsgi.application'

# ⬇️ BASE DE DATOS: CONFIGURACIÓN DUAL (SQLite / PostgreSQL) ⬇️
if 'DATABASE_URL' in os.environ:
    # PRODUCCIÓN (Render): Usa PostgreSQL, lee la variable de entorno
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
    
    # 🌟 CORRECCIÓN CRÍTICA PARA RENDER/SSL:
    # Fuerza el parámetro 'sslmode' a través del diccionario OPTIONS de Django,
    # evitando que cause problemas de TypeError en el build.
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }

else:
    # DESARROLLO (Local): Usa SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# ⬆️ FIN DE LA CONFIGURACIÓN DUAL ⬆️

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'downloader' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ko-fi webhook configuration
KO_FI_WEBHOOK_SECRET = os.environ.get('KO_FI_WEBHOOK_SECRET', '')  # set in env for signature verification if available

# URL where the prepackaged EXE is hosted (user will receive link to this URL in email)
PREPACKAGED_EXE_URL = os.environ.get('PREPACKAGED_EXE_URL', 'https://ko-fi.com/downloaderplaylist')

# Stripe, Celery, Email envs are expected
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LICENSE_PRIVATE_KEY_PATH = os.environ.get('LICENSE_PRIVATE_KEY_PATH', '/run/secrets/license_private.pem')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URLs para redirección de autenticación
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# Configuración adicional de Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

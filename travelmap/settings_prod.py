from travelmap.settings import *
import os

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "travelregistration",
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASS'],
        'HOST': os.getenv('DATABASE_HOST', 'db'),
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE[1:]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',  # Capture everything from DEBUG up to ERROR
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # This catches all errors from Django framework itself
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        # This catches errors from your custom apps/code
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

import os
from mudev.settings import *

DEBUG = True
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'mutopiadb',
    'USER': 'muuser',
    'PASSWORD': 'mumusic',
    'HOST': '127.0.0.1',
    'PORT': '5432',
}

# Use "DEBUG" level to get DB query times (as well as expected
# exceptions that are caught and ignored in the template system.)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
        'mutopia': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
    },
}

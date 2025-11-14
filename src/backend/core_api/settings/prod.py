from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "bull-bear.app",
    "admin.bull-bear.app",
    "api.bull-bear.app",
]

CORS_ALLOWED_ORIGINS = [
    "https://bull-bear.app",
    "https://admin.bull-bear.app",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://bull-bear.app",
    "https://admin.bull-bear.app",
]

LOGIN_REDIRECT_URL = "https://bull-bear.app"
LOGOUT_REDIRECT_URL = "https://bull-bear.app"


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'

SESSION_COOKIE_DOMAIN = ".bull-bear.app"
CSRF_COOKIE_DOMAIN = ".bull-bear.app"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

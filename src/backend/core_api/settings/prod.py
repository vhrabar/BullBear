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
    "https://api.bull-bear.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://bull-bear.app",
    "https://admin.bull-bear.app",
    "https://api.bull-bear.app",
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


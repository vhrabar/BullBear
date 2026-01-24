from .base import *

DEBUG = True
SITE_ID = 5

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

LOGIN_REDIRECT_URL = "http://localhost:5173/explore"
LOGOUT_REDIRECT_URL = "http://localhost:5173"


print("Development settings loaded.")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

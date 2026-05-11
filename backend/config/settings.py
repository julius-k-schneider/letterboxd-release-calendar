from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-key")
DEBUG = env("DEBUG")

# Hosts:
#   - localhost / 127.0.0.1 for local dev
#   - any *.up.railway.app subdomain (leading dot = wildcard in Django)
#   - any *.railway.app for custom Railway domains
#   - whatever Railway sets as RAILWAY_PUBLIC_DOMAIN
#   - anything the user puts into ALLOWED_HOSTS env (comma-separated)
_base_hosts = ["localhost", "127.0.0.1", ".up.railway.app", ".railway.app"]
_env_hosts = [h.strip() for h in env("ALLOWED_HOSTS", default="").split(",") if h.strip()]
_railway_host = env("RAILWAY_PUBLIC_DOMAIN", default="").strip()
ALLOWED_HOSTS = _base_hosts + _env_hosts + ([_railway_host] if _railway_host else [])

# CSRF: trust HTTPS on every Railway subdomain + any explicit hosts.
CSRF_TRUSTED_ORIGINS = ["https://*.up.railway.app", "https://*.railway.app"]
for h in _env_hosts + ([_railway_host] if _railway_host else []):
    if h.startswith("."):
        CSRF_TRUSTED_ORIGINS.append(f"https://*{h}")
    else:
        CSRF_TRUSTED_ORIGINS.append(f"https://{h}")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

TMDB_API_KEY = env("TMDB_API_KEY", default="")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "calendar_app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Database — Railway sets a writable persistent path via volume mount (optional).
# DATABASE_PATH env points to the SQLite file location (default: project-local).
DATABASE_PATH = env("DATABASE_PATH", default=str(BASE_DIR / "db.sqlite3"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_PATH,
        "OPTIONS": {
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
    }
}

# CORS only matters in dev when Vite runs on a different origin.
CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNAUTHENTICATED_USER": None,
}

USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files served by WhiteNoise in production.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [FRONTEND_DIST] if FRONTEND_DIST.exists() else []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage" if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
WHITENOISE_INDEX_FILE = True

"""Django settings for cabinet_backend — Cabinet 2.0 MVP."""

from pathlib import Path

import sys
import os

try:
    from .local_settings import POSTGRES_PASSWORD as _local_postgres_password
except ImportError:
    _local_postgres_password = ""

if getattr(sys, 'frozen', False):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
    # The actual folder containing the .exe
    RUNTIME_BASE = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    RUNTIME_BASE = BASE_DIR
SECRET_KEY = "django-insecure-mvp-demo-change-before-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ---------- TENANT APPS ----------
SHARED_APPS = [
    "django_tenants",
    "customers",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
]

TENANT_APPS = [
    "api",
]

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

TENANT_MODEL = "customers.Client"
TENANT_DOMAIN_MODEL = "customers.Domain"
PUBLIC_SCHEMA_NAME = "public"
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

# ---------- MIDDLEWARE ----------
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------- CORS (dev only — allow everything) ----------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# ---------- URL CONFIG ----------
ROOT_URLCONF = "cabinet_backend.urls"

# ---------- TEMPLATES ----------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend_build"],     # Serve index.html from here
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cabinet_backend.wsgi.application"

# ---------- DATABASE (PostgreSQL with schema-based tenants) ----------
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.environ.get("POSTGRES_DB", "cabinet"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", _local_postgres_password),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# ---------- PASSWORD VALIDATORS ----------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- i18n ----------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Casablanca"
USE_I18N = True
USE_TZ = True

# ---------- STATIC FILES ----------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "frontend_build"]   # Frontend assets served here

# ---------- DRF ----------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",       # No auth for MVP demo
    ],
}

# ---------- DEFAULT PK ----------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

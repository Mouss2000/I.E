"""
Django settings for cabinet_backend — Cabinet 2.0 MVP.
SQLite for portability. CORS wide-open for local dev.
"""

from pathlib import Path

import sys
import os

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

# ---------- INSTALLED APPS ----------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local
    "api",
]

# ---------- MIDDLEWARE ----------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # MUST be first
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

# ---------- DATABASE (SQLite — zero config) ----------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": RUNTIME_BASE / "db.sqlite3",
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

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "development-only-change-me")
if not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY == "development-only-change-me"):
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a random secret of at least 50 characters")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
CSRF_TRUSTED_ORIGINS = list(filter(None, os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")))
INSTALLED_APPS = ["studio", "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "studio.middleware.UploadLimit", "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware", "studio.impersonation.ValidateAdministrator", "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware", "studio.middleware.SecurityHeaders"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages", "studio.access.context"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.environ.get("DATABASE_PATH", str(BASE_DIR / "data/db.sqlite3")), "OPTIONS": {"timeout": 20}}}
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation." + name} for name in ["UserAttributeSimilarityValidator", "MinimumLengthValidator", "CommonPasswordValidator", "NumericPasswordValidator"]]
LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, "staticfiles": {"BACKEND": "studio.storage.ModuleStaticStorage"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365
SESSION_SAVE_EVERY_REQUEST = True
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
DATA_UPLOAD_MAX_MEMORY_SIZE = 100_000

DATA_UPLOAD_MAX_NUMBER_FILES = 1

# The LAN development server runs with --noreload. Never retain template copies
# across requests, otherwise fresh JS can see an outdated HTML structure.
if DEBUG:
    TEMPLATES[0]["APP_DIRS"] = False
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

APP_VERSION = (BASE_DIR / "VERSION").read_text().strip()
UPDATE_MANIFEST_URL = os.environ.get("UPDATE_MANIFEST_URL", "https://github.com/BenAhrdt/RikasFarbenzauber/releases/latest/download/latest.json")
UPDATE_STATE_DIR = Path(os.environ.get("UPDATE_STATE_DIR", str(BASE_DIR / "data/updates")))
UPDATE_INSTALL_ENABLED = os.environ.get("UPDATE_INSTALL_ENABLED", "false").lower() == "true"

# Local HTTP plus explicitly permitted HTTPS origins through the user's proxy.
RIKA_LOCAL_ACCESS = os.environ.get('RIKA_LOCAL_ACCESS', 'false').lower() == 'true'
RIKA_HTTPS_ORIGINS = list(filter(None, os.environ.get('RIKA_HTTPS_ORIGINS', '').split(',')))
if RIKA_LOCAL_ACCESS:
    ALLOWED_HOSTS = ['*']  # Validated per request by LocalAndHttps against DB + actual interfaces.
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False  # HTTPS cookies are separately named and secured per request.
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    CSRF_TRUSTED_ORIGINS = []  # Same-origin checks remain enabled for every permitted host.
    MIDDLEWARE.insert(0, 'studio.site_access.LocalAndHttps')
    # HTTP is intentional on the local interface; HTTPS uses separate Secure cookies.
    SILENCED_SYSTEM_CHECKS = ['security.W004','security.W008','security.W012','security.W016']

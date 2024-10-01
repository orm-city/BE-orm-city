from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS 설정
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

ADMIN_ENABLED = True

INSTALLED_APPS += [  # noqa
    "drf_spectacular",  # drf_spectacular
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

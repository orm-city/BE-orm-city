from .base import *  # noqa
import os

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS 설정
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

ADMIN_ENABLED = True

# INSTALLED_APPS += [  # noqa
#     "drf_spectacular",  # drf_spectacular
# ]

TOKEN_TEST = {
    "DJANGO_SUPERUSER_USERNAME": env("DJANGO_SUPERUSER_USERNAME"),
    "DJANGO_SUPERUSER_PASSWORDenv": env("DJANGO_SUPERUSER_PASSWORD"),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",  # 디버그 레벨로 설정
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",  # 요청 관련 로그
            "propagate": True,
        },
    },
}


FRONTEND_HOST = "http://localhost:3000"

CERTIFICATE_SECRET_KEY = os.getenv(
    "CERTIFICATE_SECRET_KEY", "a_very_secret_32_byte_long_key!!"
)

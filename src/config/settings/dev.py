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


TOKEN_TEST = {
    "DJANGO_SUPERUSER_USERNAME" : env("DJANGO_SUPERUSER_USERNAME"),
    "DJANGO_SUPERUSER_PASSWORDenv": env("DJANGO_SUPERUSER_PASSWORD"),
}

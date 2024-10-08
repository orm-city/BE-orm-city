from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = ["*"]  # noqa

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CORS_ALLOW_CREDENTIALS = True

ADMIN_ENABLED = False

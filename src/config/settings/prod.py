from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])  # noqa

CORS_ALLOW_ALL_ORIGINS = True  # noqa

CORS_ALLOW_CREDENTIALS = True

ADMIN_ENABLED = False

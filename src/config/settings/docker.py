from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = ["*"]  # noqa

CORS_ALLOWED_ORIGINS = [
    "http://3.36.122.224",  # 브라우저에서 요청을 보낸 도메인
    "http://orm-city.site",
    "https://orm-city.site",
]

CORS_ALLOW_CREDENTIALS = True

ADMIN_ENABLED = False

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# 공식 Python 3.12-slim 이미지 사용
FROM python:3.12-slim
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=src.config.settings.docker
# PostgreSQL 개발 패키지와 gcc 설치 (최소 의존성 설치 후 캐시 정리)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# PDM 설치
RUN pip install --no-cache-dir pdm

# PDM 프로젝트 파일 복사 및 종속성 설치
COPY pyproject.toml pdm.lock /app/
RUN pdm install --prod --no-lock --no-editable --no-self

# 소스 코드 복사
COPY ./src /app/src
COPY .env /app/.env

# Django의 collectstatic 명령어 실행 (staticfiles 폴더가 자동 생성됨)
RUN pdm run python src/manage.py collectstatic --noinput

# Gunicorn을 사용해 Django 서버 실행
CMD ["pdm", "run", "gunicorn", "--chdir", "/app/src", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
# 컨테이너 시작 시 PDM의 가상 환경을 활성화하고 Django 서버 실행
# CMD ["pdm", "run", "python", "src/manage.py", "runserver", "0.0.0.0:8000"]

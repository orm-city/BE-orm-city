# 공식 Python 이미지를 사용
FROM python:3.12-slim

# PostgreSQL 개발 패키지 설치
RUN apt-get update && apt-get install -y libpq-dev gcc

# 작업 디렉토리 설정
WORKDIR /app

# PDM 설치
RUN pip install --no-cache-dir pdm

# PDM 프로젝트 파일 복사
COPY pyproject.toml pdm.lock /app/

# PDM을 사용하여 종속성 설치
RUN pdm install --prod --no-lock --no-editable

# 소스 코드 복사
COPY ./src /app/src
COPY .env /app

# PDM의 가상 환경을 활성화하고 장고 서버 실행
CMD ["pdm", "run", "python", "src/manage.py", "runserver", "0.0.0.0:8000"]

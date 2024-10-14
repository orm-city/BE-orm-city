## 날짜(24-10-00)

### 문제 상황

- 어떤 것을 하려다가 문제가 발생했는가?
- 발행한 환경, 프로그램, 경로
- 발생한 문제(에러)

### 원인

- 추정되는 원인
- 실제 원인

### 최종 해결

- 최종 해결을 위한 시행 착오(optional)
- 해결 방법

### 참고 자료

# 트러블 슈팅 목록
## 24-09-24
1. 도커에서 마이그레이션 명령어가 사용이 안되는 문제
원인 : pdm으로 의존성을 관리하였음.
해결 방법 : `python manage.py makemigrations`가 아닌 `pdm run manage.py makemigrations`로 실행시켜야 했음.

## 24-09-25
1. 터미널에서 `python manage.py makemigrations`가 작동하지 않는 문제 발생
원인 : 알 수 없음
해결 방법 : `python manage.py makemigrations {앱이름}`으로 각각 마이그레이션을 실행

##
npx supabase login
docker 키기
npx supabase start
npx supabase db reset --linked

## 날짜(24-10-01)

### 문제 상황

- 어떤 것을 하려다가 문제가 발생했는가?
    - 테스트 코드에서 `reverse`를 사용하여 url이 안불러와짐
- 발행한 환경, 프로그램, 경로
    - `src\videos\tests\test_views.py`
- 발생한 문제(에러)
    ```
    FAILED src/videos/tests/test_views.py::TestVideoViewSet::test_admin_can_create_video - django.urls.exceptions.NoReverseMatch: Reverse for 'video-list' not found. 'video-list' is not a valid view function or pa...
    FAILED src/videos/tests/test_views.py::TestVideoViewSet::test_normal_user_cannot_create_video - django.urls.exceptions.NoReverseMatch: Reverse for 'video-list' not found. 'video-list' is not a valid view function or pa...
    FAILED src/videos/tests/test_views.py::TestVideoViewSet::test_unauthenticated_user_cannot_create_video - django.urls.exceptions.NoReverseMatch: Reverse for 'video-list' not found. 'video-list' is not a valid view function or pa...
    FAILED src/videos/tests/test_views.py::TestVideoViewSet::test_s3_error_on_video_creation - django.urls.exceptions.NoReverseMatch: Reverse for 'video-list' not found. 'video-list' is not a valid view function or pa...
    FAILED src/videos/tests/test_views.py::TestVideoViewSet::test_admin_can_delete_video - django.urls.exceptions.NoReverseMatch: Reverse for 'video-detail' not found. 'video-detail' is not a valid view function o...
    ```
### 원인

- 추정되는 원인
    - name을 잘못작성
- 실제 원인
    - app_name이 중첩되어 있었음

### 최종 해결

- 최종 해결을 위한 시행 착오(optional)
- 해결 방법
    - `config.urls.py`에도 `app_name`이 있었음.
    - 이 내용을 포함해서 작성하기 위해서는 `"api:v1:videos:video-list"`가 되어야함
    - `config.urls.py`에서 `app_name`을 삭제하였음


## 날짜(24-10-00)

### 문제 상황

- 어떤 것을 하려다가 문제가 발생했는가? 멀티 업로드가 되지 않음
- 발행한 환경, 프로그램, 경로 src\videos\views.py
- 발생한 문제(에러) 500

### 원인

- 추정되는 원인 - 알 수 없음
- 실제 원인
    - aws에서 `"ExposeHeaders": ["ETag"],` cors에 추가하여야 했음
    -

### 최종 해결

- 최종 해결을 위한 시행 착오(optional)
- 해결 방법

### 참고 자료


## 날짜(24-10-00)

### 문제 상황

- 어떤 것을 하려다가 문제가 발생했는가?
    - 구니콘 없이 배포했을 경우 문제가 없었지만, 구니콘을 붙이니 실행이 되지 않았음
    - 아래는 그 코드들임
    - CMD ["pdm", "run", "gunicorn", "--bind", "0.0.0.0:8000", "src.config.wsgi:application"]
    - CMD ["pdm", "run", "python", "src/manage.py", "runserver", "0.0.0.0:8000"]
- 발행한 환경, 프로그램, 경로
    - Dockerfile

- 발생한 문제(에러)
    - docker 로그를 살펴보니 'accounts'모듈을 찾을 수 없다고 나옴

### 원인

- 추정되는 원인
    - 알 수 없음
- 실제 원인
    - 구니콘이 `config.wsgi`위치를 찾지 못해서 발생

### 최종 해결

- 최종 해결을 위한 시행 착오(optional)
    - 마이그레이션 새롭게 진행
- 해결 방법
    - CMD ["pdm", "run", "gunicorn", "--chdir", "/app/src", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
### 참고 자료

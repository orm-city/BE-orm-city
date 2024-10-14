# <img width="24" alt="orm-logo2" src="https://github.com/user-attachments/assets/4156185e-65eb-41e4-9ddd-a9935b4e1232"> 오름시티
<a href="#" target="_blank">
<img src="https://github.com/user-attachments/assets/6b99de1d-45c4-40f9-9c6d-5740c88a1fcf" alt="배너" width="100%"/>
</a>
*최종 작성 후 순서 및 목차인덱싱 예정

<br/>
<br/>

# 🚀 시작하기
```bash
명령어
```
[서비스 링크]()

<br/>
<br/>

# 🎯 프로젝트 개요
- 프로젝트 이름: 오름시티
- 프로젝트 설명: ICT(정보통신기술) 온라인 교육 플랫폼으로 각 과정은 체계적으로 정리된 커리큘럼을 바탕으로 미션과제를 통해 학습자가 이론과 실습을 균형 있도록 서비스를 제공합니다.
- 프로젝트 기간: **24.09.20 ~ 24.10.13**

<br/>
<br/>


# 👥 팀원 및 팀 소개
| 고경민 | 남민우 | 장지우 | 백승현 |
|:------:|:------:|:------:|:------:|
| <img src="https://github.com/user-attachments/assets/89308f54-9351-43ff-907c-53a0e2b2c7a1" alt="고경민" width="150"> | <img src="https://github.com/user-attachments/assets/f4cbe0d6-bf34-4e6f-8f88-5f4f200faea0" alt="남민우" width="150"> | <img src="https://github.com/user-attachments/assets/51695336-3dd3-4ea1-8939-37fe790652b3" alt="장지우" width="150"> | <img src="https://github.com/user-attachments/assets/599b7564-d265-4a42-9389-1043f4be6710" alt="백승현" width="150"> |
| PL<br/>(BE/FE) | BE | FE/BE | BE |
| [GitHub](https://github.com/cumulus308) | [GitHub](https://github.com/NamMinWoo91) | [GitHub](https://github.com/cheeou) | [GitHub](https://github.com/baccine) |

<br/>
<br/>

# 🤝 작업 및 역할 분담

| **이름** | 고경민 | 남민우 | 장지우 | 백승현 |
|-------------|--------|--------|--------|--------|
| **담당 역할** | ▪︎ 프로젝트 계획 및 관리<br>▪︎ 영상 컨텐츠 업로드 기능<br>▪︎ 수강증 인증 기능<br>▪︎ 미션 평가 기능<br>▪︎ 배포 환경 구축<br>▪︎ FE 구축 | ▪︎ 사용자 관리 기능<br>▪︎ 강의 과목 관리 기능 | ▪︎ 강의 결제 기능<br>▪︎ 학습 진행 관리 기능<br>▪︎ FE 구축 | |


<br/>
<br/>


# 🛠️ 기술 스택


### Frontend
<img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">


### Backend
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">


### Deploy
<img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"> ![Amazon S3](https://img.shields.io/badge/amazon%20S3-569A31?style=for-the-badge&logo=amazon%20S3&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)



### Cooperation
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![Notion](https://img.shields.io/badge/Notion-%23ffffff.svg?style=for-the-badge&logo=notion&logoColor=black) ![Jira](https://img.shields.io/badge/jira-%230A0FFF.svg?style=for-the-badge&logo=jira&logoColor=white) ![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

<br/>
<br/>


# ⏰ 개발일정(WBS)
``` mermaid
gantt
    dateFormat  YYYY-MM-DD
    title       오름시티 프로젝트 WBS
    excludes    weekends

    section 프로젝트 준비
    프로젝트 킥오프 미팅                     :2024-09-23, 1d
    요구사항 분석 및 기술 스택 결정            :2024-09-23, 1d
    ERD 작성                               :2024-09-24, 1d

    section 공통 작업
    일일 스크럼 미팅                         :2024-09-25, 15d

    section 모델 작성
    accounts 모델 작성                      :2024-09-25, 1d
    certificates 모델 작성                  :2024-09-25, 1d
    courses 모델 작성                       :2024-09-25, 1d
    dashboards 모델 작성                    :2024-09-25, 1d
    missions 모델 작성                      :2024-09-25, 1d
    payment 모델 작성                       :2024-09-25, 1d
    progress 모델 작성                      :2024-09-25, 1d
    videos 모델 작성                        :2024-09-25, 1d

    section accounts 앱 (민우)
    회원가입 기능 구현                       :2024-09-26, 1d
    로그인/로그아웃 기능 구현                 :2024-09-26, 1d
    사용자 프로필 CRUD 구현                  :2024-09-27, 1d
    권한 설정 구현                          :2024-09-27, 1d
    accounts 앱 단위 테스트                 :2024-09-30, 1d

    section courses 앱 (민우)
    과목 CRUD 기능 구현                     :2024-09-30, 1d
    과목 로드맵 UI 구현                     :2024-10-01, 1d
    과목 상세 페이지 구현                    :2024-10-01, 1d
    courses 앱 단위 테스트                  :2024-10-02, 1d

    section payment 앱 (지우)
    결제 기능 외부 API 연동                  :2024-09-26, 1d
    결제 프로세스 구현                       :2024-09-27, 1d
    결제 내역 조회 기능 구현                  :2024-09-27, 1d
    payment 앱 단위 테스트                  :2024-09-30, 1d

    section progress 앱 (지우)
    학습 진행 모델 구현                      :2024-09-30, 1d
    진행률 계산 로직 구현                    :2024-10-01, 1d
    학습 기간 관리 기능 구현                  :2024-10-01, 1d
    progress 앱 단위 테스트                 :2024-10-02, 1d

    section videos 앱 (경민)
    비디오 업로드 기능 구현                   :2024-09-26, 1d
    비디오 스트리밍 기능 구현                 :2024-09-26, 1d
    비디오 진행률 추적 기능 구현              :2024-09-27, 1d
    videos 앱 단위 테스트                   :2024-09-30, 1d

    section certificates 앱 (경민)
    수료증 모델 및 발급 조건 구현             :2024-09-30, 1d
    수료증 PDF 생성 기능 구현                :2024-10-01, 1d
    certificates 앱 단위 테스트             :2024-10-02, 1d

    section missions 앱 (승현)
    미션 모델 구현                          :2024-09-27, 1d
    미션 생성 및 관리 기본 기능 구현           :2024-09-27, 1d
    missions 앱 단위 테스트                 :2024-09-30, 1d

    section dashboards 앱 (승현)
    학습자 대시보드 기본 UI 구현              :2024-10-01, 1d
    dashboards 앱 단위 테스트               :2024-10-02, 1d

    section 통합 및 테스트
    앱 간 통합 작업                         :2024-10-03, 1d
    통합 테스트                             :2024-10-04, 1d
    사용자 시나리오 기반 전체 테스트           :2024-10-04, 1d
    성능 테스트                             :2024-10-07, 1d

    section 마무리
    발견된 버그 수정                        :2024-10-07, 1d
    최종 점검                              :2024-10-08, 1d
    1차 완성                             :2024-10-08, 1d

    section 프론트엔드 작업
    프론트엔드 설정                          :2024-10-09, 1d
    공통 컴포넌트 확인                       :2024-10-09, 1d
    메인 페이지 UI 구현                     :2024-10-10, 1d
    로그인/회원가입 페이지 UI 구현            :2024-10-10, 1d
    강의 목록 및 상세 페이지 UI 구현          :2024-10-11, 1d
    학습 진행 페이지 UI 구현                 :2024-10-11, 1d
    결제 페이지 UI 구현                     :2024-10-12, 1d
    대시보드 페이지 UI 구현                  :2024-10-12, 1d

    section 배포 준비
    서버 환경 구성                          :2024-10-09, 1d
    데이터베이스 마이그레이션                 :2024-10-10, 1d
    보안 설정 및 HTTPS 적용                 :2024-10-11, 1d
    로깅 및 모니터링 시스템 구축              :2024-10-12, 1d

    section 프로젝트 마무리
    최종 테스트 및 QA                       :2024-10-13, 1d
    사용자 매뉴얼 작성                       :2024-10-13, 1d
    프로젝트 문서화 완료                     :2024-10-13, 1d
    최종 발표 자료 준비                      :2024-10-13, 1d
```
<br/>

# 📁 데이터베이스 모델링(ERD)
``` mermaid
erDiagram

    CustomUser ||--o{ Enrollment : has
    CustomUser ||--o{ Payment : makes
    CustomUser ||--o{ UserProgress : tracks
    CustomUser ||--o{ UserActivity : logs
    CustomUser ||--o{ MultipleChoiceSubmission : submits
    CustomUser ||--o{ CodeSubmissionRecord : submits
    CustomUser ||--o{ Certificate : receives
    CustomUser ||--o{ UserLearningRecord : has
    CustomUser ||--o{ ExpirationNotification : receives
    
    MajorCategory ||--o{ MinorCategory : contains
    MajorCategory ||--o{ Enrollment : has
    MajorCategory ||--o{ Payment : for
    MajorCategory ||--o{ UserLearningRecord : tracks
    
    MinorCategory ||--o{ Video : contains
    MinorCategory ||--o{ Mission : has
    
    Video ||--o{ UserProgress : tracks
    
    Enrollment ||--o{ UserProgress : tracks
    Enrollment ||--|| Payment : has
    Enrollment ||--o{ ExpirationNotification : has
    
    Mission ||--o{ MultipleChoiceQuestion : contains
    Mission ||--o{ CodeSubmission : contains
    
    MultipleChoiceQuestion ||--o{ MultipleChoiceSubmission : has
    CodeSubmission ||--o{ CodeSubmissionRecord : has
    CodeSubmission ||--o{ TestCase : has
    
    Payment ||--o{ DailyPayment : records
    
    UserProgress ||--o{ UserVideoProgress : tracks

    Certificate }|--|| MajorCategory : "issues for"
    Certificate }|--|| MinorCategory : "issues for"

    UserActivity ||--o{ UserLearningRecord : logs

    CustomUser {
        int id PK
        string email UK
        string username
        string role
        string nickname
    }
    
    MajorCategory {
        int id PK
        string name
        int price
    }
    
    MinorCategory {
        int id PK
        int major_category_id FK
        string name
        text content
        int order
    }
    
    Video {
        int id PK
        int minor_category_id FK
        string name
        text description
        string video_url
        duration duration
        int order
        datetime created_at
    }
    
    Enrollment {
        int id PK
        int user_id FK
        int major_category_id FK
        datetime enrollment_date
        datetime expiry_date
        string status
    }
    
    Payment {
        int id PK
        int user_id FK
        int major_category_id FK
        int enrollment_id FK
        int total_amount
        datetime payment_date
        string payment_status
        int refund_amount
        string refund_status
        datetime refund_deadline
        string merchant_uid
        string imp_uid
        string receipt_url
    }
    
    UserProgress {
        int id PK
        int user_id FK
        int video_id FK
        int enrollment_id FK
        boolean is_completed
        datetime last_accessed
        float progress_percent
        duration time_spent
        int last_position
    }
    
    Mission {
        int id PK
        int minor_category_id FK
        string title
        text description
        string mission_type
        boolean is_midterm
        boolean is_final
    }
    
    MultipleChoiceQuestion {
        int id PK
        int mission_id FK
        text question
        string option_1
        string option_2
        string option_3
        string option_4
        string option_5
        int correct_option
    }
    
    CodeSubmission {
        int id PK
        int mission_id FK
        text problem_statement
        text example_input
        text example_output
        int time_limit
        int memory_limit
        string language
    }
    
    UserActivity {
        int id PK
        int user_id FK
        datetime login_time
        datetime logout_time
    }
    
    MultipleChoiceSubmission {
        int id PK
        int user_id FK
        int question_id FK
        int selected_option
        boolean is_correct
        datetime submitted_at
    }
    
    CodeSubmissionRecord {
        int id PK
        int user_id FK
        int code_submission_id FK
        text submitted_code
        datetime submission_time
        text test_results
        string result_summary
        boolean is_passed
        float execution_time
        int memory_usage
    }
    
    TestCase {
        int id PK
        int code_submission_id FK
        text input_data
        text expected_output
        boolean is_sample
    }
    
    Certificate {
        int id PK
        int user_id FK
        int content_type_id FK
        int object_id
        datetime issued_at
        uuid certificate_id
        text encrypted_data
    }
    
    DailyVisit {
        date date PK
        int student_unique_visitors
        int student_total_views
        text unique_ips
    }
    
    DailyPayment {
        int id PK
        int payment_id FK
        date date
        int amount
    }
    
    UserLearningRecord {
        int id PK
        int user_id FK
        int user_activity_id FK
        int major_category_id FK
        date date
        int total_study_seconds
    }
    
    UserVideoProgress {
        int id PK
        int user_progress_id FK
        date date
        int daily_watch_duration
        float progress_percent
    }
    
    ExpirationNotification {
        int id PK
        int user_id FK
        int enrollment_id FK
        date notification_date
        boolean is_sent
    }
```
<br/>


# 🏛️ 프로젝트 아키텍처

<br/>
<br/>

# ⭐ 메인 기능
- **사용자 관리**:
  - JWT와 리프레시 토큰을 통해 안전하고 효율적인 사용자 인증 및 권한 관리 기능을 구현했습니다.
  - 회원가입, 로그인, 로그아웃 기능을 제공합니다.
  - 사용자 역할은 관리자, 수강생으로 구분되며, 개인정보 수정 및 프로필 관리가 가능합니다.

- **강의 과목 관리**:
  - 대분류와 소분류 과목을 체계적으로 관리할 수 있습니다.
  - 수강신청 및 수강 기간을 관리하며, 과목별 진행률이 자동으로 계산됩니다.
 
- **동영상 학습 시스템**:
  - AWS S3의 멀티파트 업로드 기능을 사용하여 동영상을 효율적으로 업로드하고 관리하는 시스템을 구현하였습니다.

- **학습 진행 관리**:
  - 사용자는 자신의 학습 진행 상황을 확인하고, 동영상 시청 기록을 관리할 수 있습니다.

- **수강증 인증 시스템**:
  - 각 과목별로 디지털 수료증 PDF 추출 발급 및 수료증 진위 확인이 가능합니다.

- **대시보드**:
  - 관리자는 일별 접속자 수와 매출 통계를 확인할 수 있으며, 학습자는 자신의 학습 진행 상황과 남은 미션을 확인할 수 있습니다.

- **권한 관리**:
  - 관리자와 사용자 역할에 따른 권한을 설정하고 관리할 수 있습니다.

- **미션 평가 시스템**:
  - 각 과목별로 중간/기말 시험을 포함한 미션이 제공되며, 객관식 문제와 코드 제출 문제를 통해 학습자의 이해도를 평가할 수 있습니다.

- **결제 시스템**:
  - 아임포트 결제 시스템 연동으로 사용자는 과목을 결제하고 결제 내역을 조회할 수 있으며, 환불 요청도 가능합니다.
<br/>

# 🖥️ 화면구성

<br/>

# ❗트러블슈팅

<br/>

# 🔗 URL 구조(마이크로식)

 

### ☑︎ accounts
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| POST | /accounts/register/ | 새 사용자 등록 | - | - |
| POST | /accounts/login/ | 사용자 로그인 | ✅ | |
| POST | /accounts/logout/ | 사용자 로그아웃 | ✅ | |
| GET/PUT | /accounts/profile/ | 사용자 프로필 조회 및 수정 | ✅ | |
| GET | /accounts/activity/ | 사용자 활동 기록 조회 | ✅ | |
| DELETE | /accounts/delete/ | 계정 삭제 | ✅ | |
| POST | /accounts/create-manager/ | 관리자 계정 생성 | ✅ | ✅ |
| PATCH | /accounts/change-role/int:user_id/ | 사용자 역할 변경 | ✅ | ✅ |

<br/>

## ☑︎ certificates
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| GET | /certificates/ | 발급 가능한 수료증 목록 조회 | ✅ | |
| GET | /certificates/preview/str:course_type/int:course_id/ | 수료증 미리보기 | ✅ | ✅ |
| GET | /certificates/download/str:course_type/int:course_id/ | 수료증 다운로드 | ✅ | ✅ |
| GET | /certificates/verify/uuid:certificate_id/ | 수료증 검증 | - | - |

<br/>

## ☑︎ courses
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| GET/POST | /courses/major-categories/ | 대분류 목록 조회 및 생성 | GET - <br/>POST ✅ | GET - <br/>POST ✅ |
| GET/PUT/DELETE | /courses/major-categories/int:pk/ | 대분류 상세 조회, 수정, 삭제 | GET - <br/> PUT/DELETE ✅ | GET - <br/>PUT/DELETE ✅ |
| GET/POST | /courses/minor-categories/ | 소분류 목록 조회 및 생성 | GET - <br/>POST ✅ | GET - <br/>POST ✅ |
| GET/PUT/DELETE | /courses/minor-categories/int:pk/ | 소분류 상세 조회, 수정, 삭제 | GET - <br/>PUT/DELETE ✅ | GET - <br/>PUT/DELETE ✅ |
| GET/POST | /courses/enrollments/ | 수강 신청 목록 조회 및 생성 | ✅ | |
| GET/PUT/DELETE | /courses/enrollments/int:pk/ | 수강 신청 상세 조회, 수정, 삭제 | ✅ | ✅ |
| POST | /courses/enrollments/int:pk/complete/ | 수강 완료 처리 | ✅ | ✅ |
<br/>

## ☑︎ dashboards
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| GET | /dashboards/summary/ | 대시보드 요약 정보 | ✅ | ✅ |
| GET | /dashboards/daily-visits/ | 일일 방문자 통계 | ✅ | ✅ |
| GET | /dashboards/daily-payments/ | 일일 결제 통계 | ✅ | ✅ |
| GET | /dashboards/learning-records/ | 사용자 학습 기록 | ✅ | ✅ |
| GET | /dashboards/video-progress/ | 비디오 진행 상황 | ✅ | ✅ |
| GET | /dashboards/expiration-notifications/ | 만료 알림 목록 | ✅ | ✅ |
| GET | /dashboards/student-dashboard/ | 학생 대시보드 정보 | ✅ | ✅ |
<br/>

## ☑︎ missions

| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|------|-----------|------|
| GET/PUT/PATCH | /missions/{id}/ | 특정 미션의 세부 정보 조회,수정,업데이트 | ✅ | ✅ |
| GET/POST | /missions/<br/>code-submission-questions/ | 코드 제출 전체 문제 목록 조회,생성 | ✅ | ✅ |
| GET/PUT/PATCH/DELETE | /missions/<br/>code-submission-questions/{id}/ | 특정 코드 제출 CRUD | ✅ | ✅ |
| GET | /missions/code-submissions/ | 코드 제출 목록 조회,생성 | ✅ | ✅ |
| POST | /missions/code-submissions/<br/>{code_submission_id}/evaluate/ | 제출된 코드 평가 | ✅ | ✅ |
| GET/PUT/PATCH/DELETE | /missions/<br/>code-submissions/{id}/ | 특정 코드 제출 CRUD | ✅ | ✅ |
| GET | /missions/major/{major_id}/<br/>{minor_id}/{mid_or_final}/cs/ | 특정 분류의 코드 제출 문제 목록 조회 | ✅ | ✅ |
| GET | /missions/major/{major_id}/<br/>{minor_id}/{mid_or_final}/mcqs/ | 특정 분류의 객관식 문제 목록 조회 | ✅ | ✅ |
| GET/POST | /missions/multiple-choice-questions/ | 객관식 문제 목록 조회,생성 | ✅ | ✅ |
| GET/POST/PUT/PATCH/DELETE | /missions<br/>/multiple-choice-questions/{id}/ | 특정 객관식 문제 CRUD | ✅ | ✅ |
| GET | /missions/submissions/all/cs/ | 모든 사용자의 코드 제출 내역 조회 | ✅ | ✅ |
| GET | /missions/submissions/all/mcqs/ | 모든 사용자의 객관식 문제 제출 내역 조회 | ✅ | ✅ |
| GET | /missions/submissions/user/cs/ | 현재 사용자의 코드 제출 내역 조회 | ✅ | ✅ |
| GET | /missions/submissions/user/mcqs/ | 현재 사용자의 객관식 문제 제출 내역 조회 | ✅ | ✅ |


<br/>

## ☑︎ payment
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| GET | /payment/info/int:major_category_id/ | 결제 정보 조회 | ✅ | |
| POST | /payment/complete/ | 결제 완료 처리 | ✅ | |
| GET | /payment/user-payments/ | 사용자 결제 내역 조회 | ✅ | |
| GET | /payment/detail/int:payment_id/ | 특정 결제 상세 정보 조회 | ✅ | ✅ |
| POST | /payment/refund/int:payment_id/ | 환불 요청 처리 | ✅ | ✅ |


<br/>

## ☑︎ progress
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| GET | /progress/ | 사용자의 전체 학습 진행률 조회 | ✅ | |
| PATCH | /progress/update/int:pk/ | 특정 강의 학습 수강 상태 업데이트 | ✅ | |
| GET | /progress/overall/ | 사용자의 강의 카테고리별 수강 진행률 조회 | ✅ | |
| GET | /progress/video/int:video_id/ | 특정 강의 학습 진행률  조회 | ✅ | |

<br/>

## ☑︎ videos
| HTTP Method | URL Pattern | Description | Authentication | Permission |
|-------------|-------------|-------------|----------------|------------|
| GET/POST | /videos/ | 비디오 목록 조회 및 생성 | GET: - <br/>POST ✅ | GET - <br/>POST: ✅ |
| GET/PUT/DELETE | /videos/int:pk/ | 비디오 상세 조회, 수정, 삭제 | ✅ | ✅ |
| POST | /videos/complete-upload/ | 멀티파트 업로드 완료 처리 | ✅ | ✅ |
| POST | /videos/progress/ | 사용자 비디오 진행 상황 업데이트 | ✅ | ✅ |
<br/>


<br/>


# 🔮 브랜치 전략 (Branch Strategy)
우리의 브랜치 전략은 Git Flow를 기반으로 하며, 다음과 같은 브랜치를 사용합니다.

- Main Branch
  - 배포 가능한 상태의 코드를 유지합니다.
  - 모든 배포는 이 브랜치에서 이루어집니다.
  
- Dev Branch
  - 배포를 위한 개발 브랜치입니다.
  - 모든 기능 개발 취합이 해당 브랜치에서 이루어집니다.

- Issue Branch
  - GitHub 이슈 생성 시 Jira와 GitHub Actions 자동화를 통해 작업 브랜치가 자동 생성되어 개발을 작업을 진행합니다.

<br/>
<br/>



# 🧩 Coding Convention


## 커밋 이모지
```
== 기능
✨	새로운 기능 구현

== 버그
🐛	버그 리포트
🚑	버그를 고칠 때

== 기타
🚀	배포
```

<br/>

## 커밋 예시
```
== ex1
✨Feat: "회원 가입 기능 구현"

```

<br/>
<br/>


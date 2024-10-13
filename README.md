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
|  |  |  |
|-----------------|-----------------|-----------------|
| 고경민    | <img src="https://github.com/user-attachments/assets/89308f54-9351-43ff-907c-53a0e2b2c7a1" alt="고경민" width="100"> | <ul><li>프로젝트 계획 및 관리</li><li>팀 리딩 및 커뮤니케이션</li><li>영상 컨텐츠 업로드 기능</li><li>수강증 인증 기능</li><li>미션 평가 기능</li><li>배포 환경 구축</li><li>FE 구축</li></ul>     |
| 남민우   |  <img src="https://github.com/user-attachments/assets/f4cbe0d6-bf34-4e6f-8f88-5f4f200faea0" alt="남민우" width="100">| <ul><li>사용자 관리 기능</li><li>강의 과목 관리 기능</li></ul> |
| 장지우   |  <img src="https://github.com/user-attachments/assets/51695336-3dd3-4ea1-8939-37fe790652b3" alt="장지우" width="100">    |<ul><li>강의 결제 기능</li><li>학습 진행 관리 기능</li><li>FE 구축</li></ul>  |
| 백승현    | <img src="https://github.com/user-attachments/assets/599b7564-d265-4a42-9389-1043f4be6710" alt="백승현" width="100">    | <ul><li></li></ul>    |

<br/>
<br/>


# 🛠️ 기술 스택

<br/>

## Frontend
<img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">

<br/>

## Backend
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">

<br/>

## Deploy
<img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"> ![Amazon S3](https://img.shields.io/badge/amazon%20S3-569A31?style=for-the-badge&logo=amazon%20S3&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)


<br/>

## Cooperation
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white) ![Jira](https://img.shields.io/badge/jira-%230A0FFF.svg?style=for-the-badge&logo=jira&logoColor=white) ![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

<br/>
<br/>


# ⏰ 개발일정(WBS)

<br/>

# 📁 데이터베이스 모델링(ERD)

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
<br/>

## accounts

<br/>

## certificates

<br/>

## courses

<br/>

## dashboards

<br/>

## missions

<br/>

## payment

<br/>

## progress

<br/>

## videos

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


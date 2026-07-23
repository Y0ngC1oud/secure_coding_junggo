# Tiny Market (secure_coding_junggo)

Flask 기반 중고거래 플랫폼 과제. 회원가입/로그인, 상품 등록·조회·검색, 사용자 간 채팅(전체/1:1), 신고 및 자동 제재, 사용자 간 송금, 관리자 페이지를 제공한다.

## 기술 스택

- Python 3 + Flask
- SQLAlchemy (SQLite)
- Flask-Login (세션 인증), Flask-WTF (폼/CSRF), Flask-Limiter (요청 제한)
- Jinja2 서버사이드 템플릿

## 환경 설정

```bash
git clone https://github.com/Y0ngC1oud/secure_coding_junggo.git
cd secure_coding_junggo

python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# .env를 열어 SECRET_KEY를 임의의 랜덤 값으로 변경 (아래 명령으로 생성 가능)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

`.env` 예시:

```
SECRET_KEY=<위에서 생성한 랜덤 값>
SESSION_COOKIE_SECURE=false   # HTTPS 배포 시 true로 변경
FLASK_DEBUG=false             # 로컬 개발 중 자동 리로드가 필요하면 true
```

## 실행 방법

```bash
python run.py
```

기본적으로 `http://localhost:5000` 에서 실행된다. (`PORT` 환경변수로 포트 변경 가능)

최초 실행 시 `instance/app.db` SQLite 파일과 테이블이 자동으로 생성된다.

## 관리자 계정 만들기

1. 먼저 웹 화면에서 일반 회원가입을 진행한다.
2. 아래 CLI 명령으로 해당 계정을 관리자로 승격한다.

```bash
flask --app run create-admin <가입한 아이디>
```

관리자로 로그인하면 상단 네비게이션에 "관리자" 메뉴가 나타나며 `/admin`에서 회원/상품/신고를 관리할 수 있다.

## 주요 기능

| 기능 | 설명 |
|---|---|
| 회원가입/로그인/로그아웃 | 세션 기반 인증, 비밀번호 해시 저장, 로그인 브루트포스 방지 |
| 마이페이지 | 소개글 수정, 비밀번호 변경, 잔액/등록 상품 확인 |
| 상품 등록/조회/수정/삭제 | 이미지 업로드(확장자 검증 + 랜덤 파일명), 소유자만 수정/삭제 가능 |
| 상품 검색 | 키워드 + 카테고리 필터 |
| 채팅 | 전체 채팅, 사용자 간 1:1 채팅 |
| 신고 | 상품/사용자 신고, 사유 작성, 누적 시 자동 차단(상품)·휴면 처리(사용자) |
| 송금 | 사용자 간 잔액 기반 송금, 거래 내역 조회 |
| 관리자 | 회원 정지/활성화, 상품 활성화/차단/삭제, 신고 처리 |

## 보안 관련 문서

개발 중 고려한 보안 취약점과 대응 방식은 [SECURITY_LOG.md](SECURITY_LOG.md) 참고.

## 프로젝트 구조

```
app/
  admin/       관리자 기능
  auth/        회원가입/로그인/마이페이지
  chat/        전체/1:1 채팅
  main/        홈 페이지
  products/    상품 등록/조회/검색
  reports/     신고
  transfers/   송금
  templates/   Jinja2 템플릿
  static/      CSS, 업로드 이미지
  config.py    환경설정
  extensions.py Flask 확장 초기화
  models.py    DB 모델
run.py         앱 실행 진입점
requirements.txt
.env.example
SECURITY_LOG.md
```

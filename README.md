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

env 예시
SECRET_KEY=<위에서 생성한 랜덤 값>
SESSION_COOKIE_SECURE=false   # HTTPS 배포 시 true로 변경
FLASK_DEBUG=false             # 로컬 개발 중 자동 리로드가 필요하면 true
ADMIN_USERNAME=admin          # 아래 "관리자 계정 만들기" 참고 (선택 사항)
ADMIN_PASSWORD=change-me
ADMIN_NICKNAME=관리자


## 실행 방법
PORT=5050 python run.py
```

`http://localhost:5050` 접속. 종료는 터미널에서 `Ctrl + C`.

## 관리자 계정 만들기

**방법 1 (권장) — `.env`에 값 채우기**

`.env`에 `ADMIN_USERNAME`, `ADMIN_PASSWORD`를 채워두면, 서버를 시작할 때마다 해당 계정이 자동으로 생성되고 관리자 권한과 비밀번호가 `.env` 값 그대로 동기화된다(이미 다른 비밀번호로 가입되어 있던 계정이어도 `.env`의 값으로 덮어씀). 별도 명령 없이 그 아이디/비밀번호로 바로 로그인하면 된다.

**방법 2 — CLI 명령**

1. 먼저 웹 화면에서 일반 회원가입을 진행한다.
2. 아래 명령에서 `가입한아이디` 부분을 실제 아이디 문자열로 바꿔서 실행한다(꺾쇠괄호 `<`, `>`는 입력하지 않음). **반드시 프로젝트 폴더로 이동해 venv를 켠 상태**에서 실행해야 한다.

```bash
cd secure_coding_junggo
source .venv/bin/activate
flask --app run create-admin 가입한아이디
```

관리자로 로그인하면 상단 네비게이션에 "관리자" 메뉴가 나타나며 `/admin`에서 회원/상품/신고를 관리할 수 있다.

## 주요 기능

| 기능                     | 설명                                                                   |
| ------------------------ | ---------------------------------------------------------------------- |
| 회원가입/로그인/로그아웃 | 세션 기반 인증, 비밀번호 해시 저장, 로그인 브루트포스 방지             |
| 마이페이지               | 소개글 수정, 비밀번호 변경, 잔액/등록 상품 확인                        |
| 상품 등록/조회/수정/삭제 | 이미지 업로드(확장자 검증 + 랜덤 파일명), 소유자만 수정/삭제 가능      |
| 상품 구매                | 원클릭 구매(송금 + 판매완료 처리를 하나의 트랜잭션으로 원자적 처리)    |
| 상품 검색                | 별도 검색 페이지에서 키워드 + 카테고리 필터                            |
| 채팅                     | 전체 채팅, 사용자 간 1:1 채팅                                          |
| 신고                     | 상품/사용자 신고, 사유 작성, 누적 시 자동 차단(상품)·휴면 처리(사용자) |
| 송금                     | 사용자 간 잔액 기반 송금(아이디/닉네임 지정), 거래 내역 조회           |
| 공개 프로필              | 다른 사용자의 닉네임·소개글·등록 상품 열람                             |
| 관리자                   | 회원 정지/활성화/잔액 설정, 상품 활성화/차단/삭제, 신고 처리           |

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
.env
```

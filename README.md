# TOEIC 5단어 - 로그인/계정별 학습기록 버전

Flask + PostgreSQL(Supabase 등) 기반의 TOEIC 단어 학습 웹앱입니다.

## 추가된 기능
- 회원가입 / 로그인 / 로그아웃
- 계정별 학습 진도 저장
- 계정별 오답노트 저장
- 계정별 테스트 횟수/정답률 저장
- 다른 컴퓨터/브라우저에서 같은 계정으로 로그인하면 기록 동기화
- 기존 LEVEL 1 / LEVEL 2, 복습, 발음, 예문, 한국어↔중국어 전환 유지
- 비밀번호는 Werkzeug 안전 해시로 저장

## GitHub에 올릴 파일
저장소 최상위에 다음 구조가 있어야 합니다.

app.py
requirements.txt
render.yaml
README.md
.gitignore
data/words.json

## Supabase 데이터베이스 만들기
1. Supabase에서 프로젝트를 하나 만듭니다.
2. Project Settings → Database에서 PostgreSQL 연결 문자열(Connection string)을 확인합니다.
3. 비밀번호가 포함된 DATABASE_URL은 GitHub 코드에 절대 넣지 마세요.
4. Render 환경변수에 DATABASE_URL로 등록합니다.

예:
DATABASE_URL=postgresql://.../postgres?sslmode=require

앱을 처음 실행하면 users와 user_progress 테이블을 자동으로 생성합니다.

## Render 환경변수
Render → 서비스 → Environment에서 다음 3개를 설정하세요.

DATABASE_URL = Supabase PostgreSQL 연결 문자열
SECRET_KEY = 길고 임의의 비밀 문자열
COOKIE_SECURE = 1

SECRET_KEY 예시는 직접 새 값을 만들어 사용하세요. 실제 비밀번호나 키를 GitHub에 올리지 마세요.

## Render 설정
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

Health Check Path:
/health

## 중요
기존 localStorage 학습 기록은 계정 DB로 자동 이전되지 않습니다.
새 버전에서는 로그인한 계정의 서버 데이터가 학습 기록의 기준입니다.

처음 로그인/회원가입 후 공부하면 user_progress에 해당 계정의 기록이 저장됩니다.

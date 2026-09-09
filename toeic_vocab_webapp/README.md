# TOEIC 5단어 웹앱 — 인터넷 배포용

Python Flask로 만든 공개 배포용 TOEIC 단어 학습 웹앱입니다.

## 기능
- 2,109개 단어 데이터
- 한 번에 5단어 학습
- 5문제 객관식 테스트
- 5/5 정답 시 다음 세트 완료
- 틀린 단어 자동 오답노트
- 오답만 다시 테스트
- 학습 진도/정답률 저장
- 회원가입 없이 바로 사용

## 중요한 저장 방식
학습 진도와 오답노트는 **사용자의 브라우저 localStorage**에 저장됩니다.
따라서 서버에 개인정보나 학습기록을 저장하지 않으며, 여러 사용자가 동시에 이용할 수 있습니다.
단, 브라우저 데이터를 삭제하거나 다른 기기를 사용하면 기존 진도는 이어지지 않습니다.

## 로컬 실행
```bash
pip install -r requirements.txt
python app.py
```
브라우저에서 `http://127.0.0.1:8000` 접속.

## Render 배포
1. 이 폴더를 GitHub 저장소에 업로드합니다.
2. Render에서 New → Web Service를 선택합니다.
3. GitHub 저장소를 연결합니다.
4. Runtime: Python
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app`
7. Free 플랜으로 생성합니다.
8. 배포가 끝나면 `https://프로젝트명.onrender.com` 주소가 생성됩니다.

`render.yaml`이 있으므로 Render의 Blueprint 방식으로도 배포할 수 있습니다.

## 주의
Render 무료 웹 서비스는 15분간 요청이 없으면 sleep 상태가 되고, 다음 접속 때 다시 시작됩니다. 학습 데이터는 서버 파일에 저장하지 않으므로 Render 재배포/재시작으로 진도가 사라지지는 않습니다. 단, 사용자의 브라우저 데이터를 지우면 해당 사용자의 진도가 사라집니다.

# 1. 파이썬 3.10 버전의 기본 리눅스 환경에서 시작합니다.
FROM python:3.10-slim

# 2. 작업 폴더를 만듭니다.
WORKDIR /app

# 3. 리눅스 시스템을 업데이트하고, 크롬 브라우저와 드라이버를 직접 설치합니다.
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends

# 4. requirements.txt 파일을 먼저 복사하고, 파이썬 라이브러리를 설치합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 나머지 모든 코드(main.py 등)를 복사합니다.
COPY . .

# 6. 이 서버가 실행될 때 uvicorn을 시작하라고 명령합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

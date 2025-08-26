from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# FastAPI 앱 생성
app = FastAPI()

# 입력 데이터 모델
class ScrapeRequest(BaseModel):
    url: str
    table_index: int = 0

# Selenium 웹 드라이버 설정 (서버 환경에 최적화)
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # UI 없이 백그라운드에서 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    # Koyeb의 chromium-driver 경로를 직접 지정
    service = Service(executable_path="/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# 스크래핑 API 엔드포인트
@app.post("/scrape_table")
def get_table_from_url(request: ScrapeRequest):
    driver = None
    try:
        driver = get_driver()
        driver.get(request.url)
        
        # 페이지가 로드될 시간을 충분히 줍니다 (JavaScript 로딩 대기)
        time.sleep(3) # 3초 대기
        
        # 페이지의 HTML 소스를 가져옵니다
        html_content = driver.page_source
        
        # pandas를 사용하여 테이블을 읽습니다
        tables = pd.read_html(html_content)

        if not tables:
            raise IndexError("페이지에서 테이블을 찾을 수 없습니다.")

        if request.table_index >= len(tables):
            raise HTTPException(status_code=404, detail=f"테이블을 찾을 수 없습니다. 해당 페이지에는 {len(tables)}개의 테이블만 존재합니다.")

        df = tables[request.table_index]
        df = df.fillna('')
        df = df.astype(str)
        json_result = df.to_dict(orient='records')
        
        return {"table_data": json_result}

    except IndexError as e:
         raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류 발생: {e}")
    finally:
        # 드라이버가 생성되었다면 반드시 종료하여 자원을 반환합니다
        if driver:
            driver.quit()

@app.get("/")
def read_root():
    return {"message": "Selenium Scraper API is running."}

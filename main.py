from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # 길찾기 전문가를 불러옵니다
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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    # [수정된 부분] 주소를 하드코딩하는 대신, 전문가(webdriver-manager)가 알아서 드라이버를 찾아 설치하도록 합니다.
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# 스크래핑 API 엔드포인트
@app.post("/scrape_table")
def get_table_from_url(request: ScrapeRequest):
    driver = None
    try:
        driver = get_driver()
        driver.get(request.url)
        
        time.sleep(3)
        
        html_content = driver.page_source
        tables = pd.read_html(html_content)

        if not tables:
            raise IndexError("페이지에서 테이블을 찾을 수 없습니다.")

        if request.table_index >= len(tables):
            raise HTTPException(status_code=404, detail=f"테이블을 찾을 수 없습니다. 해당 페이지에는 {len(tables)}개의 테이블만 존재합니다.")

        df = tables[request.index]
        df = df.fillna('')
        df = df.astype(str)
        json_result = df.to_dict(orient='records')
        
        return {"table_data": json_result}

    except IndexError as e:
         raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류 발생: {e}")
    finally:
        if driver:
            driver.quit()

@app.get("/")
def read_root():
    return {"message": "Selenium Scraper API v2 is running."}

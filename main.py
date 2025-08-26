from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import requests

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    table_index: int = 0

@app.post("/scrape_table")
def get_table_from_url(request: ScrapeRequest):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(request.url, headers=headers, timeout=10)
        response.raise_for_status()

        try:
            html_content = response.content.decode('euc-kr')
        except UnicodeDecodeError:
            html_content = response.content.decode('utf-8', 'ignore')

        tables = pd.read_html(html_content)

        if request.table_index >= len(tables):
            raise HTTPException(status_code=404, detail=f"Table not found. Only {len(tables)} tables exist on the page.")

        df = tables[request.table_index]
        df = df.fillna('')
        df = df.astype(str)
        json_result = df.to_dict(orient='records')

        return {"table_data": json_result}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Cannot access URL: {e}")
    except IndexError:
         raise HTTPException(status_code=404, detail="No tables found on the page.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "Scraper API is running."}

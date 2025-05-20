from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import sqlalchemy
import os
import logging

# 設定 logging
logging.basicConfig(level=logging.INFO)

# 環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URL = os.getenv("DB_URL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 環境變數未設定")
if not DB_URL:
    raise ValueError("DB_URL 環境變數未設定")

# 初始化
openai.api_key = OPENAI_API_KEY
engine = sqlalchemy.create_engine(DB_URL)
app = FastAPI()

# CORS 設定（給前端用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    question = req.question

    prompt = f"""
你是一位 SQL 專家，幫我針對 PostgreSQL 資料庫產生查詢語法。
問題：{question}
請只回傳 SQL 語句，不要加註解或說明。
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        sql = response["choices"][0]["message"]["content"].strip().strip("```sql").strip("```")

        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(sql))
            rows = [dict(row) for row in result]

        return {"sql": sql, "data": rows}

    except Exception as e:
        logging.exception("查詢過程錯誤")
        return {"error": str(e)}

from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import sqlalchemy
import os
import json

# 從環境變數取得設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
DB_URL = os.getenv("DB_URL")

openai.api_key = OPENAI_API_KEY
engine = sqlalchemy.create_engine(DB_URL)

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    question = req.question

    # 提示詞：讓 GPT 產生 SQL
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
        return {"error": str(e)}

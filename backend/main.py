from fastapi import FastAPI
from pydantic import BaseModel
import sqlalchemy
import os

# 模擬問答對
EXAMPLE_SQLS = {
    "列出所有API呼叫量": "SELECT * FROM API_DAILY;",
    "有幾筆資料": "SELECT COUNT(*) FROM API_DAILY;",
    "查詢 clmExt-prod-MphoneToRocid 呼叫成功數": "SELECT success FROM API_DAILY WHERE API_NAME = 'clmExt-prod-MphoneToRocid';"
}

# 從環境變數取得資料庫連線
DB_URL = os.getenv("DB_URL")
engine = sqlalchemy.create_engine(DB_URL)

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    question = req.question.strip()
    sql = EXAMPLE_SQLS.get(question)

    if not sql:
        return {
            "sql": None,
            "data": [],
            "note": "這是 demo 模式，目前僅支援：\n" + "\n".join(EXAMPLE_SQLS.keys())
        }

    try:
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(sql))
            rows = [dict(row) for row in result.mappings()]

        return {"sql": sql, "data": rows}

    except Exception as e:
        return {"error": str(e)}

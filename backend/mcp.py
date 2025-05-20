from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.chains import SQLDatabaseChain
from langchain.sql_database import SQLDatabase
import os

# 環境變數：DB_URL / OPENAI_API_KEY
DB_URL = os.getenv("DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 初始化 FastAPI
app = FastAPI()

# MCP
# 初始化 LangChain 元件
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
db = SQLDatabase.from_uri(DB_URL)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

# 輸入模型
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    try:
        result = db_chain.run(req.question)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

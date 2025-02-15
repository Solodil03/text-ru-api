from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging
import os

app = FastAPI()

TEXT_RU_API_KEY = "3c957569f16140b682c791af6ec3176d"
TEXT_RU_API_URL = "https://text.ru/antiplagiat/"
TEXT_RU_GET_URL = "https://text.ru/antiplagiat/"

logging.basicConfig(level=logging.INFO)

class TextRequest(BaseModel):
    text: str

@app.post("/check_text")
def check_text(request: TextRequest):
    payload = {
        "text": request.text,
        "userkey": TEXT_RU_API_KEY
    }
    logging.info(f"Отправляем текст в Text.ru: {payload}")
    
    response = requests.post(TEXT_RU_API_URL, data=payload)
    logging.info(f"Ответ от Text.ru: {response.text}")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ошибка API Text.ru: {response.text}")

    try:
        result = response.json()
    except Exception as e:
        logging.error(f"Ошибка парсинга JSON: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга JSON: {response.text}")

    if "error_code" in result:
        logging.error(f"Ошибка API Text.ru: {result}")
        raise HTTPException(status_code=500, detail=f"Ошибка Text.ru: {result.get('error_desc', 'Неизвестная ошибка')}")

    text_uid = result.get("text_uid") or result.get("order")
    if not text_uid:
        raise HTTPException(status_code=500, detail="Text.ru не вернул UID.")

    return {"text_uid": text_uid}

@app.get("/get_result")
def get_result(uid: str):
    payload = {
        "uid": uid,
        "userkey": TEXT_RU_API_KEY,
        "jsonvisible": "detail"
    }
    logging.info(f"Запрос на получение результата: {payload}")
    
    response = requests.post(f"{TEXT_RU_GET_URL}{uid}", data=payload)
    logging.info(f"Ответ от Text.ru: {response.text}")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ошибка получения результата: {response.text}")

    try:
        result = response.json()
    except Exception as e:
        logging.error(f"Ошибка парсинга JSON: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга JSON: {response.text}")

    if "error_code" in result:
        raise HTTPException(status_code=500, detail=f"Ошибка Text.ru: {result.get('error_desc', 'Неизвестная ошибка')}")

    return {"full_response": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))








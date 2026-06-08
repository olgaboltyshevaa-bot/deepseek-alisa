from fastapi import FastAPI, Request
import requests
import os
import uvicorn

app = FastAPI()

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.post("/")
async def main(request: Request):
    try:
        data = await request.json()
        user_message = data.get("request", {}).get("command", "")
    except Exception as e:
        return {"response": {"text": f"Ошибка чтения запроса: {str(e)}", "end_session": False}, "version": "1.0"}

    if not user_message:
        return {"response": {"text": "Вы ничего не сказали. Повторите, пожалуйста.", "end_session": False}, "version": "1.0"}}

    # Формируем запрос к DeepSeek
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": 500
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=10)
        result = response.json()

        # Проверяем, есть ли ключ 'choices'
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
        else:
            # Если пришла ошибка от DeepSeek
            error_msg = result.get("error", {}).get("message", "Неизвестная ошибка API")
            answer = f"Извините, DeepSeek вернул ошибку: {error_msg}. Проверьте API-ключ или повторите позже."

    except requests.exceptions.Timeout:
        answer = "Превышено время ожидания ответа от DeepSeek. Попробуйте спросить короче."
    except Exception as e:
        answer = f"Техническая ошибка при обращении к DeepSeek: {str(e)}"

    return {"response": {"text": answer, "end_session": False}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)

import os
import json
import requests
import streamlit as st


def ask_yandex_gpt(system_prompt: str, user_message: str):
    api_key = st.secrets.get("YANDEX_API_KEY") or os.getenv("YANDEX_API_KEY")
    folder_id = st.secrets.get("YANDEX_FOLDER_ID") or os.getenv("YANDEX_FOLDER_ID")

    if not api_key or not folder_id:
        st.error("❌ Не найдены YANDEX_API_KEY или YANDEX_FOLDER_ID в файле .env")
        return

    try:
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "modelUri": f"gpt://{folder_id}/yandexgpt",
                "completionOptions": {
                    "stream": True,
                    "temperature": 0.5,
                    "maxTokens": 2000,
                },
                "messages": [
                    {"role": "system", "text": system_prompt},
                    {"role": "user",   "text": user_message},
                ],
            },
            stream=True,
            timeout=60,
        )
        response.raise_for_status()

        prev_text = ""

        for line in response.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line.decode("utf-8"))
                full_text = chunk["result"]["alternatives"][0]["message"]["text"]


                if full_text and len(full_text) > len(prev_text):
                    delta = full_text[len(prev_text):]
                    prev_text = full_text
                    yield delta

            except (json.JSONDecodeError, KeyError):
                continue

    except requests.exceptions.Timeout:
        st.error("⏱ Превышено время ожидания. Попробуйте ещё раз.")
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            st.error("❌ Ошибка 401: неверный API-ключ. Проверьте YANDEX_API_KEY в .env")
        elif code == 403:
            st.error("❌ Ошибка 403: нет доступа. Проверьте роль ai.languageModels.user у сервисного аккаунта.")
        else:
            st.error(f"❌ Ошибка API {code}: {e.response.text}")
    except Exception as e:
        st.error(f"❌ Неожиданная ошибка: {e}")

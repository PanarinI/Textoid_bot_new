import requests
import os
from dotenv import load_dotenv

load_dotenv()  # загружаем переменные окружения

TOKEN = os.getenv("BOT_TOKEN")
USERNAME = "@tiraniia"

url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={USERNAME}"
response = requests.get(url).json()

if response.get("ok"):
    print("ID канала:", response["result"]["id"])
else:
    print("Ошибка:", response.get("description"))

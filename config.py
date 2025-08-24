from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "False").lower() in ("1", "true", "yes")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))

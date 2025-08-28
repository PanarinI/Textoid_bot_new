import os
import sys
import logging
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Добавляем корень проекта в sys.path, чтобы 'app' был виден
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Импорты из пакета app ---
from loader import bot, dp
from app.handlers.textoid_handlers import router as textoid_router
from logging_config import setup_logging

# Настройка логирования
setup_logging()
logging.info("🚀 Старт приложения")

# Подключаем роутеры
dp.include_router(textoid_router)

# --- Переменные окружения ---
BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/textoid")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 80))


# --- Функции запуска ---
async def start_polling():
    logging.info("Запуск в режиме polling")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def start_webhook():
    logging.info("Запуск в режиме webhook")
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    async def on_startup(app):
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook установлен: {WEBHOOK_URL}")

    app.on_startup.append(on_startup)

    logging.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


# --- Точка входа ---
if __name__ == "__main__":
    if BOT_MODE.lower() == "webhook":
        asyncio.run(start_webhook())
    else:
        asyncio.run(start_polling())

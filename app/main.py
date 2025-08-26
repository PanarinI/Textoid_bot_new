import os
import logging
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from logging_config import setup_logging
from loader import bot, dp
from handlers.textoid_handlers import router as textoid_router

# Настройка логирования сразу
setup_logging()

logging.info("🚀 Старт приложения")

# Подключаем маршруты обработчиков
dp.include_router(textoid_router)

# Чтение переменных окружения
BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8080))


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


if __name__ == "__main__":
    if BOT_MODE == "webhook":
        asyncio.run(start_webhook())
    else:
        asyncio.run(start_polling())

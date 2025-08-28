import os
import sys
import logging
import asyncio
from aiohttp import web

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loader import bot, dp
from app.handlers.textoid_handlers import router as textoid_router
from logging_config import setup_logging

setup_logging()
logging.info("🚀 Старт приложения")

dp.include_router(textoid_router)

BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/textoid")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 80))


async def handle_update(request):
    """Обработчик Webhook"""
    import json
    from aiogram.types import Update
    try:
        data = await request.text()
        update = Update(**json.loads(data))
        await dp.feed_update(bot, update)
        return web.Response()
    except Exception as e:
        logging.error(f"Ошибка обработки update: {e}")
        return web.Response(status=500)


async def main():
    if BOT_MODE.lower() == "polling":
        logging.info("Запуск в режиме polling")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    else:
        logging.info("Запуск в режиме webhook")
        app = web.Application()
        app.add_routes([
            web.post(WEBHOOK_PATH, handle_update),
            web.get("/", lambda request: web.Response(text="✅ Бот работает!"))
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
        await site.start()
        logging.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")

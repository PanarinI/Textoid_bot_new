import os
import logging
from dotenv import load_dotenv
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from loader import bot, dp
from handlers.textoid_handlers import router as textoid_router

load_dotenv()

dp.include_router(textoid_router)

BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8080))

if BOT_MODE == "webhook":
    logging.info("🚀 Запуск в режиме webhook")

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    async def on_startup():
        await bot.set_webhook(WEBHOOK_URL)

    app.on_startup.append(lambda app: on_startup())
    logging.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

else:
    logging.info("🚀 Запуск в режиме polling")
    import asyncio
    async def polling():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    asyncio.run(polling())

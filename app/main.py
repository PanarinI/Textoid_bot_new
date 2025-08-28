import os
import sys
import logging
import asyncio
from aiohttp import web
from aiogram.types import Update

# --- Добавляем корень проекта в sys.path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Импорты ---
from loader import bot, dp
from app.handlers.textoid_handlers import router as textoid_router
from logging_config import setup_logging

# --- Логирование ---
setup_logging()
logging.info("🚀 Старт приложения")

# --- Роутеры ---
dp.include_router(textoid_router)

# --- Переменные окружения ---
BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/textoid")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 80))


# --- Хендлеры webhook ---
async def handle_update(request):
    try:
        data = await request.json()
        update = Update(**data)
        # ⚡️ feed_update в Amvera-среде
        await dp.feed_update(bot=bot, update=update)
        return web.Response()
    except Exception as e:
        logging.error(f"Ошибка обработки update: {e}", exc_info=True)
        return web.Response(status=500)


async def handle_root(request):
    return web.Response(text="✅ Бот работает!", content_type="text/plain")


# --- Запуск polling ---
async def start_polling():
    logging.info("Запуск polling")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# --- Запуск webhook ---
async def start_webhook():
    logging.info("Запуск webhook")
    app = web.Application()
    app.add_routes([
        web.post(WEBHOOK_PATH, handle_update),
        web.get("/", handle_root)
    ])

    async def on_startup(app):
        if WEBHOOK_URL:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"Webhook установлен: {WEBHOOK_URL}")

    app.on_startup.append(on_startup)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()
    logging.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")

    # ⚡️ Если Amvera уже держит loop, используем asyncio.Event().wait()
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logging.info("🛑 Webhook остановлен.")


# --- Точка входа ---
if __name__ == "__main__":
    try:
        # 🔹 Для Amvera лучше напрямую использовать loop
        if BOT_MODE.lower() == "webhook":
            loop = asyncio.get_event_loop()
            loop.create_task(start_webhook())
            loop.run_forever()
        else:
            asyncio.run(start_polling())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}", exc_info=True)

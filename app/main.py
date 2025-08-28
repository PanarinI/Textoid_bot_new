import os
import sys
import json
import logging
import asyncio
import time
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

# --- Пути для импорта ---
sys.path.append("/app")
sys.path.append("/app/bot")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loader import bot, dp
from app.handlers.textoid_handlers import router as textoid_router
from logging_config import setup_logging

# --- Настройка логирования и окружения ---
setup_logging()
load_dotenv()
dp.include_router(textoid_router)

# --- Настройки ---
IS_LOCAL = os.getenv("LOCAL_RUN", "false").lower() == "true"
WEBHOOK_HOST = os.getenv("WEBHOOK_URL", "https://textoid-panarini.amvera.io").strip()
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("WEBHOOK_PORT", 80))

# --- Хендлер корневого пути ---
async def handle_root(request):
    logging.info("✅ Обработан GET-запрос на /")
    return web.Response(text="✅ Бот работает!", content_type="text/plain")

# --- Хендлер для Webhook ---
async def handle_update(request):
    start_time = time.time()
    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot=bot, update=update)
        logging.info(f"⏳ Обработка запроса заняла {time.time() - start_time:.4f} сек")
        return web.Response()
    except Exception as e:
        logging.error(f"❌ Ошибка обработки Webhook: {e}", exc_info=True)
        return web.Response(status=500)

# --- Startup: установка webhook ---
async def on_startup():
    if IS_LOCAL:
        logging.info("🛑 Локальный запуск. Webhook НЕ устанавливается.")
        await bot.delete_webhook(drop_pending_updates=True)
    else:
        logging.info(f"🔗 Устанавливаем Webhook: {WEBHOOK_URL}")
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")
            sys.exit(1)

# --- Shutdown: закрытие сессии бота ---
async def on_shutdown(_):
    logging.info("🚨 Закрываем сессию бота...")
    try:
        await bot.session.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при закрытии сессии: {e}")
    logging.info("✅ Сессия закрыта.")

# --- Главная функция ---
async def start_server():
    await on_startup()

    if IS_LOCAL:
        logging.info("🚀 Запуск бота в режиме Polling...")
        await dp.start_polling(bot)
        return

    app = web.Application()
    app.add_routes([
        web.get("/", handle_root),
        web.post(WEBHOOK_PATH, handle_update)
    ])
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()
    logging.info(f"✅ Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")

    # держим процесс живым
    await asyncio.Event().wait()

# --- Точка входа ---
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}", exc_info=True)

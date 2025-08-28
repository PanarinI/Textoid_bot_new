import os
import sys
import logging
import asyncio
from aiohttp import web

# --- Добавляем корень проекта в sys.path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Импорты из твоего проекта ---
from loader import bot, dp
from app.handlers.textoid_handlers import router as textoid_router
from logging_config import setup_logging

# --- Настройка логирования ---
setup_logging()
logging.info("🚀 Старт приложения")

# --- Подключаем роутеры ---
dp.include_router(textoid_router)

# --- Переменные окружения ---
BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/textoid")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 80))


# --- Хендлеры для вебхука ---
async def handle_update(request):
    """Обработчик входящих запросов от Telegram"""
    try:
        data = await request.json()
        from aiogram.types import Update
        update = Update(**data)
        await dp.feed_update(bot=bot, update=update)
        return web.Response()
    except Exception as e:
        logging.error(f"Ошибка обработки update: {e}", exc_info=True)
        return web.Response(status=500)


async def handle_root(request):
    """Простейший GET для проверки работы сервера"""
    return web.Response(text="✅ Бот работает!", content_type="text/plain")


# --- Запуск polling ---
async def start_polling():
    logging.info("Запуск в режиме polling")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# --- Запуск webhook через AppRunner ---
async def start_webhook():
    logging.info("Запуск в режиме webhook")
    app = web.Application()
    app.add_routes([
        web.post(WEBHOOK_PATH, handle_update),
        web.get("/", handle_root)
    ])

    async def on_startup(app):
        if WEBHOOK_URL:
            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"Webhook установлен: {WEBHOOK_URL}")

    app.on_startup.append(on_startup)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()
    logging.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")

    # Держим процесс живым
    await asyncio.Event().wait()


# --- Точка входа ---
if __name__ == "__main__":
    try:
        if BOT_MODE.lower() == "webhook":
            asyncio.run(start_webhook())
        else:
            asyncio.run(start_polling())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}", exc_info=True)

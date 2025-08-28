import os
import sys
import logging
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# 📌 Настраиваем пути для модулей (для Amvera)
sys.path.append("/app")
sys.path.append("/app/app")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logging_config import setup_logging
from loader import bot, dp
from handlers.textoid_handlers import router as textoid_router  # абсолютный импорт из корня

# Настройка логирования
setup_logging()
logging.info("🚀 Старт приложения")

# Подключаем маршруты обработчиков
dp.include_router(textoid_router)

# Переменные окружения
BOT_MODE = os.getenv("BOT_MODE", "polling")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/textoid")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 80))


async def on_startup():
    """Действия при запуске бота"""
    if BOT_MODE == "webhook":
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(_):
    """Закрытие сессии перед остановкой"""
    logging.info("🚨 Бот остановлен! Закрываю сессию...")
    await bot.session.close()
    logging.info("✅ Сессия закрыта.")


async def start_server():
    """Запуск сервера или Polling"""
    if BOT_MODE == "polling":
        logging.info("Запуск в режиме Polling")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        return

    # Webhook режим через AppRunner
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(lambda app: on_startup())
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()
    logging.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBAPP_PORT}")

    # Держим loop живым
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"🔥 Критическая ошибка: {e}", exc_info=True)

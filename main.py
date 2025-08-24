import asyncio
import logging
from config import USE_WEBHOOK, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from loader import bot, dp

from handlers.textoid_handlers import router as textoid_router

dp.include_router(textoid_router)

async def main():
    if USE_WEBHOOK and WEBHOOK_URL:
        logging.info("Запуск в режиме webhook")
        await bot.delete_webhook(drop_pending_updates=True)
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
        from aiohttp import web

        async def on_startup():
            await bot.set_webhook(WEBHOOK_URL)

        router = dp  # Dispatcher содержит маршруты
        app = web.Application()
        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        await on_startup()
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    else:
        logging.info("Запуск в режиме polling")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from logging_config import setup_logging

setup_logging()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    setup_logging()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем обработчики
    register_textoid_handlers(dp)

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

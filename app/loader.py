import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from logging_config import setup_logging

from dotenv import load_dotenv
load_dotenv()  # Подгрузка переменных из .env

# Настройка логирования
setup_logging()

# Основные объекты бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

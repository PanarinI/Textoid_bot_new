Логика бота и её реализация в коде

1. Загрузка конфига из .env
Через python-dotenv в config.py получаем BOT_TOKEN, флаг USE_WEBHOOK, WEBHOOK_URL и другие настройки.

2. Инициализация бота и диспетчера
В bot.py создаём Bot и Dispatcher с MemoryStorage, а также задаём базовое логирование (уровень, формат).

3. Обработчики — навигация по меню + FSM
В handlers/textoid_handlers.py:

/start: отправляет главное меню с inline-кнопками ("Создать текстоид", "Библиотека", "О проекте").

Callback-query: если "Создать текстоид", показываем второй уровень — кнопки "По названию", "На любую тему", "Назад".

Пользователь вводит соответствующий текст: сохраняем состояние TextoidStates.waiting_for_input, обрабатываем ввод.

Генерация: вызываем мок-функцию generate_textoid(prompt) из generator.py.

После ответа — выводим текст с кнопками "Повторить", "Сменить тему", "Поделиться" и соответствующей логикой.

4. FSM
Задача — отслеживать, что бот ожидает ввода темы/названия. Используем aiogram.fsm.state.State и StatesGroup.

5. Генерация (мок)
В generator.py функция generate_textoid(prompt: str), для начала просто возвращает "Mock-ответ: Как дела?".

6. Переключатель polling / webhook
В main.py: флаг USE_WEBHOOK выбирает режим.

Если polling: dp.start_polling(bot) с очисткой webhook (через delete_webhook) 

Если webhook: например, используем aiohttp (встроенную поддержку aiogram) 

7. Логирование
В logging_config.py базовая настройка logging.basicConfig(level, format…).
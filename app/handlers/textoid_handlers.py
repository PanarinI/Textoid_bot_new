from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..states import TextoidStates
from ..generator import generate_textoid
from aiogram import Bot

router = Router()  # <-- глобальный роутер, который импортируем в main.py

CHANNEL_ID = "@tiraniia" # для импорта в канал

# Главное меню
menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать текстоид", callback_data="create")],
        [InlineKeyboardButton(text="Библиотека", callback_data="library")],
        [InlineKeyboardButton(text="О проекте", callback_data="about")]
    ]
)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Главное меню:", reply_markup=menu_kb)



# Меню выбора метода создания
@router.callback_query(lambda c: c.data == "create")
async def choose_method(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="По названию", callback_data="by_title")],
        [InlineKeyboardButton(text="На тему", callback_data="by_topic")],
        [InlineKeyboardButton(text="Назад", callback_data="start")]
    ])
    await call.message.edit_text(text="Выберите способ:", reply_markup=kb)
    await call.answer()

@router.callback_query(lambda c: c.data == "start")
async def back_to_start(call: CallbackQuery):
    await cmd_start(call.message)
    await call.answer()

# Запрос ввода
@router.callback_query(lambda c: c.data in ("by_title", "by_topic"))
async def ask_input(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите тему или название:")
    await state.set_state(TextoidStates.waiting_for_input)
    await state.update_data(choice=call.data)
    await call.answer()

@router.message(TextoidStates.waiting_for_input)
async def got_input(message: Message, state: FSMContext):
    user_input = message.text

    # Сохраняем user_input в state, чтобы потом повторить
    await state.update_data(user_input=user_input)

    # Сообщение о начале генерации
    status_msg = await message.answer("Создаю текстоид… ⏳ Это время, но что такое время?")

    # Генерация
    result = await generate_textoid(user_input)

    await state.update_data(generated_text=result) # сохраняем текст в state для кнопки "Поделиться в канале

    # Кнопки
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Повторить", callback_data="repeat")],
        [InlineKeyboardButton(text="Сменить тему", callback_data="change")],
        [InlineKeyboardButton(text="Поделиться в канале", callback_data="share")]
    ])

    await status_msg.edit_text(result, reply_markup=kb)
    await state.set_state(TextoidStates.generated)  # Новое состояние после генерации


# Кнопка «Повторить»
@router.callback_query(lambda c: c.data == "repeat")
async def repeat(call: CallbackQuery, state: FSMContext):
    # Получаем прошлый user_input
    data = await state.get_data()
    user_input = data.get("user_input")

    if not user_input:
        await call.answer("Нет предыдущего запроса для повторения.", show_alert=True)
        return

    # Сообщение о начале генерации
    status_msg = await call.message.answer("Создаю новый текстоид… ⏳")

    # Генерация
    result = await generate_textoid(user_input)

    await state.update_data(generated_text=result)

    # Кнопки
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Повторить", callback_data="repeat")],
        [InlineKeyboardButton(text="Сменить тему", callback_data="change")],
        [InlineKeyboardButton(text="Поделиться в канале", callback_data="share")]
    ])

    await status_msg.edit_text(result, reply_markup=kb)
    await call.answer()



# Кнопка «Сменить тему»
@router.callback_query(lambda c: c.data == "change")
async def change(call: CallbackQuery):
    await choose_method(call)

# Кнопка «Поделиться в канале»
@router.callback_query(lambda c: c.data == "share")
async def share(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    generated_text = data.get("generated_text")

    if not generated_text:
        await call.answer("Нет текста для публикации.", show_alert=True)
        return

    try:
        await bot.send_message(CHANNEL_ID, generated_text)

        channel_url = "https://t.me/tiraniia"  # ссылка на твой канал
        await call.message.answer(
            f'Текст был успешно опубликован <a href="{channel_url}">в канале</a>.',
            parse_mode="HTML"
        )

    except Exception as e:
        await call.message.answer(f"Ошибка при публикации: {e}")

    await call.answer()

# Кнопки «Библиотека» и «О проекте»
@router.callback_query(lambda c: c.data == "library")
async def library(call: CallbackQuery):
    await call.message.edit_text("Библиотека (пока пусто)")
    await call.answer()

@router.callback_query(lambda c: c.data == "about")
async def about(call: CallbackQuery):
    await call.message.edit_text("Текстоид-бот. Сгенерировано с помощью AI.")
    await call.answer()
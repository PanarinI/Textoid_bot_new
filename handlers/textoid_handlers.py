from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import TextoidStates
from generator import generate_textoid

router = Router()  # <-- глобальный роутер, который импортируем в main.py

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
        [InlineKeyboardButton(text="На любую тему", callback_data="by_topic")],
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
    data = await state.get_data()
    user_input = message.text
    result = await generate_textoid(user_input)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Повторить", callback_data="repeat")],
        [InlineKeyboardButton(text="Сменить тему", callback_data="change")],
        [InlineKeyboardButton(text="Поделиться в канале", callback_data="share")]
    ])
    await message.answer(result, reply_markup=kb)
    await state.clear()

# Кнопки повтор/смена/поделиться
@router.callback_query(lambda c: c.data == "repeat")
async def repeat(call: CallbackQuery, state: FSMContext):
    await call.answer("Повторяем...")
    # TODO: сохранить тему в state и повторить

@router.callback_query(lambda c: c.data == "change")
async def change(call: CallbackQuery):
    await choose_method(call)

@router.callback_query(lambda c: c.data == "library")
async def library(call: CallbackQuery):
    await call.message.edit_text("Библиотека (пока пусто)")
    await call.answer()

@router.callback_query(lambda c: c.data == "about")
async def about(call: CallbackQuery):
    await call.message.edit_text("Текстоид-бот. Сгенерировано с помощью AI.")
    await call.answer()

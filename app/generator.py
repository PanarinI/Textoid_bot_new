import os
import logging

import anthropic
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

import prompt as prompt_module

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY не задан!")

MODEL = os.getenv("MODEL", "claude-opus-5")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "8000"))
EFFORT = os.getenv("EFFORT", "high")  # low | medium | high | xhigh | max

client = AsyncAnthropic(api_key=API_KEY)


class GenerationError(Exception):
    """Генерация не удалась. Текст исключения уже готов для показа пользователю."""


async def generate_textoid(user_input: str) -> str:
    try:
        response = await client.beta.messages.create(
            model=MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            # Правила текстоида — статичный системный промпт: он одинаков для всех
            # запросов, поэтому кэшируется и не оплачивается повторно.
            system=[{
                "type": "text",
                "text": prompt_module.PROMPT_1,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user_input}],
            thinking={"type": "adaptive"},
            output_config={"effort": EFFORT},
            # Если модель откажется от темы — запрос дорабатывает запасная модель
            # внутри того же вызова, а не обрывается.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        logging.error("❌ ANTHROPIC_API_KEY неверен или отозван")
        raise GenerationError("Ключ доступа к модели не работает. Нужно проверить настройки бота.")
    except anthropic.RateLimitError:
        logging.warning("⚠️ Лимит запросов к Anthropic")
        raise GenerationError("Слишком много запросов подряд. Подожди минуту и повтори.")
    except anthropic.APIStatusError as e:
        logging.error(f"❌ Ошибка Anthropic API ({e.status_code}): {e.message}")
        raise GenerationError("Модель сейчас недоступна. Попробуй ещё раз через минуту.")
    except anthropic.APIConnectionError as e:
        logging.error(f"❌ Нет связи с Anthropic API: {e}")
        raise GenerationError("Нет связи с моделью. Попробуй ещё раз.")

    if response.stop_reason == "refusal":
        logging.info(f"🚫 Отказ модели на теме: {user_input!r}")
        raise GenerationError("Модель не взялась за эту тему. Попробуй сформулировать иначе.")

    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if not text:
        logging.error(f"❌ Пустой ответ модели, stop_reason={response.stop_reason}")
        raise GenerationError("Модель вернула пустой ответ. Попробуй ещё раз.")

    logging.info(
        f"✅ Текстоид готов: {response.usage.input_tokens} вход / "
        f"{response.usage.output_tokens} выход, модель {response.model}"
    )
    return text

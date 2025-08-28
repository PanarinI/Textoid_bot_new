import os
from dotenv import load_dotenv
from openai import OpenAI
import prompt as prompt_module

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAIAPI"))

async def generate_textoid(user_input: str) -> str:
    # Подставляем user_input в шаблон
    instructions = prompt_module.PROMPT_1.format(user_input=user_input)

    response = client.responses.create(
        model=os.getenv("MODEL"),
        instructions=instructions,
        input=user_input,  # можно оставить, модель тоже получит raw input
       # temperature=0.8,
        max_output_tokens=int(os.getenv("MAX_OUTPUT_TOKENS"))
    )
    return response.output_text

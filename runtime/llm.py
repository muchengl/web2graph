import os

import openai
from loguru import logger

global_token_usage = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
}

def update_token_usage(usage):
    global global_token_usage
    global_token_usage["prompt_tokens"] += usage.prompt_tokens
    global_token_usage["completion_tokens"] += usage.completion_tokens
    global_token_usage["total_tokens"] += usage.total_tokens


def invoke_llm_by_prompt(prompt: str) -> str:
    openai.api_key = os.getenv('OPENAI_API_KEY')

    client = openai.OpenAI(
        api_key=openai.api_key,
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o"
        )

        output = response.choices[0].message.content
    except Exception as e:
        output = f"Exception: {e}"

    return output

def invoke_llm_by_chat(msg) -> str:
    openai.api_key = os.getenv('OPENAI_API_KEY')

    client = openai.OpenAI(
        api_key=openai.api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=msg,
        model='gpt-4o',
        temperature=0
    )

    # logger.info(f"prompt_tokens: {chat_completion.usage.prompt_tokens}")
    # logger.info(f"prompt_tokens: {chat_completion.usage.completion_tokens}")
    # logger.info(f"total_tokens: {chat_completion.usage.total_tokens}")

    update_token_usage(chat_completion.usage)

    # return chat_completion
    return chat_completion.choices[0].message.content

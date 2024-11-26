import os

import openai

def invoke_llm(prompt: str) -> str:
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
            model="gpt-4o",
            max_tokens=3000,
        )

        output = response.choices[0].message.content
    except Exception as e:
        output = f"Exception: {e}"

    return output

def invoke_llm_(msg: list) -> str:
    openai.api_key = os.getenv('OPENAI_API_KEY')

    client = openai.OpenAI(
        api_key=openai.api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=msg,
        model='gpt-4o',
        temperature=0
    )

    # return chat_completion
    return chat_completion.choices[0].message.content

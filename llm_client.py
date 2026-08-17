import os

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

load_dotenv()

def call_deepseek(prompt: str) -> str:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")

    if not api_key:
        raise RuntimeError("缺少LLM_API_KEY")

    if not base_url:
        raise RuntimeError("缺少LLM_BASE_URL")

    if not model:
        raise RuntimeError("缺少LLM_MODEL")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一名严谨的学习教练。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            stream=False,
            extra_body={
                "thinking": {
                    "type": "disabled",
                }
            },
        )
    except (
        APIConnectionError,
        APITimeoutError,
        APIStatusError,
    ) as exc:
        raise RuntimeError(
            "模型服务调用失败"
        ) from exc

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("模型没有返回内容")

    return content
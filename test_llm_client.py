from unittest.mock import Mock

import httpx
import pytest
from openai import APITimeoutError

import llm_client

def test_call_deepseek_converts_timeout_to_runtime_error(
    monkeypatch
):
    # 它会临时修改当前Python测试进程的环境变量
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    fake_client = Mock()  # Mock()会创建一个可控制行为的假对象

    fake_client.chat.completions.create.side_effect = (
        APITimeoutError(
            request=httpx.Request(
                method="POST",
                url="https://example.com/v1/chat/completions",
            ),
        )
    )

    def fake_openai(**kwargs):
        return fake_client

    monkeypatch.setattr(
        llm_client,
        "OpenAI",
        fake_openai
    )

    with pytest.raises(
        RuntimeError,
        match="模型服务调用失败"
    ):
        llm_client.call_deepseek("测试Prompt")


def test_call_deepseek_returns_model_content(
    monkeypatch
):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    fake_client = Mock()

    # 先创建content所在的message
    # → 再创建包含message的choice
    # → 再创建包含choice列表的response

    fake_message = Mock()
    fake_message.content = "模拟模型回答"

    fake_choice = Mock()
    fake_choice.message = fake_message

    fake_response = Mock()
    fake_response.choices = [fake_choice]  #content = response.choices[0].message.content

    fake_create = fake_client.chat.completions.create
    fake_create.return_value = fake_response

    def fake_openai(**kwargs):
        return fake_client

    monkeypatch.setattr(
        llm_client,
        "OpenAI",
        fake_openai
    )

    result = llm_client.call_deepseek("测试Prompt")

    assert result == "模拟模型回答"

def test_call_deepseek_rejects_empty_content(
    monkeypatch
):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    fake_client = Mock()

    fake_message = Mock()
    fake_message.content = None

    fake_choice = Mock()
    fake_choice.message = fake_message

    fake_response = Mock()
    fake_response.choices = [fake_choice]

    fake_client.chat.completions.create.return_value = fake_response

    def fake_openai(**kwargs):
        return fake_client
    monkeypatch.setattr(
        llm_client,
        "OpenAI",
        fake_openai
    )

    with pytest.raises(
        RuntimeError,
        match="模型没有返回内容"
    ):
        llm_client.call_deepseek("测试Prompt")

import pytest
from ai_service import build_summary_prompt
import ai_service

def test_build_summary_prompt_contains_records():
    prompt = build_summary_prompt([
        " 学习FastAPI ",
        "",
        "学习SQLite",
    ])

    assert "1. 学习FastAPI" in prompt
    assert "2. 学习SQLite" in prompt
    assert "学习辅导专家" in prompt
    assert "下一步建议" in prompt

def test_build_summary_prompt_rejects_blank_records():
    with pytest.raises(ValueError, match="学习记录不能为空"):
        build_summary_prompt(["", "   "])

def test_generate_summary_uses_mock_deepseek(monkeypatch):
    def fake_call_deepseek(prompt):
        assert "1. 学习FastAPI" in prompt
        return "模拟AI学习总结"

    monkeypatch.setattr(
        ai_service,
        "call_deepseek",
        fake_call_deepseek,
    )

    summary = ai_service.generate_summary(
        [
            "学习FastAPI",
        ]
    )

    assert summary == "模拟AI学习总结"
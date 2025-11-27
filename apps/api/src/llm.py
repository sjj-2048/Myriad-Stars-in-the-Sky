"""LLM 抽象层：让每个智星具备基础对话能力。

当前实现为占位实现：
- 根据星名与星域，对用户消息做简单风格化改写；
- 未来可以在此接入本地 llama.cpp、vLLM 或云端大模型。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from models import Star


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


def generate_reply(star: Star, messages: Iterable[ChatMessage]) -> str:
    """基础对话能力：给任意智星生成一条回复。

    参数:
        star: 当前对话对应的智星，便于做人格/口吻控制。
        messages: 历史消息（简单起见，这里只看最后一条用户消息）。
    """

    last_user = next((m for m in reversed(list(messages)) if m.role == "user"), None)
    question = last_user.content if last_user else "你好，星主。"  # type: ignore[union-attr]

    # 这里是非常简化的“人格化”输出逻辑，后续可替换为真实 LLM 调用。
    header = f"【{star.name} · {star.domain} 智星】"
    body = (
        f"我已经收到你的问题：{question}\n\n"
        "当前仍处于 PoC 阶段，回答由占位模型生成。"
        "后续会替换为真实大语言模型，并结合你的星尘知识与强化学习反馈，"
        "逐步进化为更专业、更稳定的智星。"
    )
    return f"{header}\n{body}"



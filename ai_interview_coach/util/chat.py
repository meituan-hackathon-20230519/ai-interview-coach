from enum import Enum

from langchain.schema import LLMResult


class Role(int, Enum):
    Human = 1
    AI = 2


def format_history(history: list[list[str]], rounds: int = 4) -> str:
    if not history:
        return "None"
    messages = []
    for message_round in history[-rounds:]:
        if message_round[0]:
            messages.append(Role.Human.name + ": " + message_round[0])
        if message_round[1]:
            messages.append(Role.AI.name + ": " + message_round[1])
    return "\n".join(messages)


def get_text_from_llm_result(result: LLMResult) -> str:
    return result.generations[0][0].text

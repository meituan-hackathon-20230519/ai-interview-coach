from enum import Enum

from humps import camelize
from langchain.schema import LLMResult
from pydantic import BaseModel


def to_camel(string):
    return camelize(string)


class CamelCaseModel(BaseModel):
    """Converts snake_case fields to camelCase when deserializing."""

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class Role(int, Enum):
    Human = 1
    AI = 2


class ChatMessage(CamelCaseModel):
    role: Role
    content: str


def format_history(history: list[list[str] | ChatMessage], rounds: int = 4) -> str:
    if not history:
        return "None"
    messages = []
    if isinstance(history[0], ChatMessage):
        for chat_message in history[-(rounds * 2 - 1):]:
            messages.append(chat_message.role.name + ": " + chat_message.content)
    else:
        for message_round in history[-rounds:]:
            messages.append(Role.Human.name + ": " + message_round[0])
            if message_round[1]:
                messages.append(Role.AI.name + ": " + message_round[1])
    return "\n".join(messages)


def get_text_from_llm_result(result: LLMResult) -> str:
    return result.generations[0][0].text

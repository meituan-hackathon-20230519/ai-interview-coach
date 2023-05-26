import logging
from typing import Any

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.chat_models.base import BaseChatModel
from langchain.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate, \
    ChatPromptTemplate

from question_generator.follow_up_prompt import FOLLOW_QUESTION_GENERATE_TEMPLATE
from question_generator.question_prompt import QUESTION_GENERATE_TEMPLATE, SYSTEM
from utils import StreamingCallbackHandler

logger = logging.getLogger(__name__)


class QuestionCallbackHandler(AsyncCallbackHandler):

    def __init__(self, chained_callback: StreamingCallbackHandler):
        self._chained_callback = chained_callback

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self._chained_callback.on_new_token(token)


class FollowUpGenerator:
    """
    Use the resume and a question set for this stage to generate a question for the interviewee
    """
    llm: BaseChatModel
    template: ChatPromptTemplate

    def __init__(self, llm: BaseChatModel, template: ChatPromptTemplate):
        self.llm = llm
        self.template = template

    @classmethod
    def build(cls, llm: BaseChatModel) -> "FollowUpGenerator":
        messages = [
            SystemMessagePromptTemplate.from_template(SYSTEM),
            HumanMessagePromptTemplate.from_template(FOLLOW_QUESTION_GENERATE_TEMPLATE)
        ]
        template = ChatPromptTemplate(
            input_variables=["question", "requirements", "history"], messages=messages
        )
        return cls(llm, template)

    async def arun(self, question: str, requirements: str, history: list[list[str]],
                   callback: StreamingCallbackHandler) -> str:
        question_callback = QuestionCallbackHandler(callback)
        messages = self.template.format_messages(question=question,
                                                 requirements=requirements,
                                                 history=history)
        result = await self.llm.agenerate(messages=[messages], callbacks=[question_callback])
        return result.generations[0][0].text

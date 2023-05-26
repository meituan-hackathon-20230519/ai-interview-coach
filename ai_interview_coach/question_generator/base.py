import logging

from langchain.chat_models.base import BaseChatModel
from langchain.prompts.chat import BaseMessagePromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, \
    ChatPromptTemplate

from question_generator.prompt import QUESTION_GENERATE_TEMPLATE, SYSTEM
from util.chat import ChatMessage

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Use the resume and a question set for this stage to generate a question for the interviewee
    """
    llm: BaseChatModel
    template: ChatPromptTemplate

    def __init__(self, llm: BaseChatModel, template: ChatPromptTemplate):
        self.llm = llm
        self.template = template

    @classmethod
    def build(cls, llm: BaseChatModel) -> "QuestionGenerator":
        messages = [
            SystemMessagePromptTemplate.from_template(SYSTEM),
            HumanMessagePromptTemplate.from_template(QUESTION_GENERATE_TEMPLATE)
        ]
        template = ChatPromptTemplate(
            input_variables=["question", "requirements", "resume", "history"], messages=messages
        )
        return cls(llm, template)

    async def arun(self, question: str, requirements: str, resume: str, history: list[list[str] | ChatMessage]) -> str:
        messages = self.template.format_messages(question=question,
                                                 requirements=requirements,
                                                 resume=resume,
                                                 history=history)
        result = await self.llm.agenerate(messages=[messages])
        return result.generations[0][0].text

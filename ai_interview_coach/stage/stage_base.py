import json
import logging
from typing import Any

from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import LLMResult

from stage.prompt import JUDGE_STAGE_TEMPLATE, SYSTEM
from util.chat import ChatMessage, format_history, get_text_from_llm_result
from util.perf import start_timer

logger = logging.getLogger(__name__)


class StageJudge:
    llm: BaseChatModel
    template: ChatPromptTemplate

    def __init__(self, llm: BaseChatModel, template: ChatPromptTemplate):
        self.llm = llm
        self.template = template

    @classmethod
    def build(cls, llm: BaseChatModel) -> "StageJudge":
        messages = [
            SystemMessagePromptTemplate.from_template(SYSTEM),
            HumanMessagePromptTemplate.from_template(JUDGE_STAGE_TEMPLATE)
        ]
        template = ChatPromptTemplate(
            input_variables=["original_question", "question_description", "history", "input"], messages=messages
        )
        return cls(llm, template)

    def __parse_result(self, result: LLMResult) -> str:
        text = get_text_from_llm_result(result)
        return text

    def __format_stage_result(self, result: str) -> bool:
        if result:
            judge_result = json.loads(result)
            return judge_result and judge_result["judgement_result"]
        return False

    async def arun(self, question: str,
                   question_description: str,
                   history: list[list[str] | ChatMessage],
                   **kwargs: Any) -> bool:
        messages = self.template.format_messages(
            original_question=question,
            question_description=question_description,
            history=format_history(history),
        )
        logger.info(f"=== StageJudge input === :\n {messages}")
        timer = start_timer()
        llm_result = await self.llm.agenerate(messages=[messages])

        logger.info(f"=== StageJudge output ==== : \n{llm_result} \n time cost: {timer()} ")
        result = self.__parse_result(llm_result)
        return self.__format_stage_result(result)

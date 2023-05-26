import json
import logging
from typing import Any

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import LLMResult, BaseMessage

from evaluation_generator.prompt import EVALUATE_TEMPLATE
from stage.stages import InterviewStage
from util.chat import get_text_from_llm_result
from utils import StreamingCallbackHandler

logger = logging.getLogger(__name__)


class Evaluation:
    response: str

    def __init__(self, response: str):
        self.response = response


class EvaluateCallbackHandler(AsyncCallbackHandler):

    def __init__(self, chained_callback: StreamingCallbackHandler):
        self._chained_callback = chained_callback

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self._chained_callback.on_new_token(token)


class EvaluationGenerator:
    """
    Use the resume and a question set for this stage to generate a question for the interviewee
    """
    llm: BaseChatModel
    template: ChatPromptTemplate
    stage_cache: dict[str, list[InterviewStage]] = {}
    evaluation_cache: dict[str, dict[str, Evaluation]] = {}

    def __init__(self, llm: BaseChatModel, template: ChatPromptTemplate):
        self.llm = llm
        self.template = template

    @classmethod
    def build(cls, llm: BaseChatModel) -> "EvaluationGenerator":
        messages = [
            HumanMessagePromptTemplate.from_template(EVALUATE_TEMPLATE)
        ]
        evaluation_template = ChatPromptTemplate(
            input_variables=["requirements", "history"], messages=messages
        )
        return cls(llm, evaluation_template)

    @classmethod
    def parse_result(cls, result: LLMResult) -> Evaluation | None:
        text = get_text_from_llm_result(result)
        if text:
            try:
                evaluation = Evaluation(text)
                return evaluation
            except Exception:
                logger.exception("Failed to parse evaluation result")
        return None

    @classmethod
    def format_eval_question_description(cls, stages: InterviewStage | list[InterviewStage]) -> str:
        if isinstance(stages, list):
            return str([stage.questions[0].eval_requirements for stage in stages])
        return stages.questions[0].eval_requirements

    async def __generate(self, messages: list[BaseMessage], callback: StreamingCallbackHandler = None):
        if callback:
            evaluate_callback = EvaluateCallbackHandler(callback)
            result = await self.llm.agenerate(messages=[messages], callbacks=[evaluate_callback])
        else:
            result = await self.llm.agenerate(messages=[messages])
        evaluation = self.parse_result(result)
        return evaluation

    async def update_cache(self, session_id: str, stages: list[InterviewStage]):
        self.stage_cache[session_id] = stages

    async def arun(self, stage: InterviewStage,
                   session_id: str,
                   history: list[list[str]],
                   total_evaluation: bool,
                   callback: StreamingCallbackHandler = None) -> Evaluation | None:
        """
            Generate a evaluation for one stage or total
        """
        if total_evaluation:
            if session_id in self.stage_cache:
                messages = self.template.format_messages(
                    requirements=self.format_eval_question_description(self.stage_cache[session_id]),
                    history=history)
            else:
                return Evaluation("## 面试评价\n暂无，请先进行面试吧~")
        else:
            if session_id in self.stage_cache:
                self.stage_cache[session_id].append(stage)
            else:
                self.stage_cache[session_id] = [stage]
            messages = self.template.format_messages(requirements=self.format_eval_question_description(stage),
                                                     history=history)

        evaluation = await self.__generate(messages, callback)

        if total_evaluation:
            stage_name = "total_evaluation"
        else:
            stage_name = stage.stage_name

        if session_id in self.evaluation_cache:
            self.evaluation_cache[session_id][stage_name] = evaluation
        else:
            self.evaluation_cache[session_id] = {stage_name: evaluation}

        logger.info(f"generate {stage_name} evaluation: \n{evaluation.response}")
        return evaluation

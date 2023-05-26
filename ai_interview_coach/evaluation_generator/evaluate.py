import json
import logging

from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import LLMResult

from evaluation_generator.prompt import EVALUATE_TEMPLATE
from stage.stages import InterviewStage
from util.chat import get_text_from_llm_result

logger = logging.getLogger(__name__)


class Evaluation:
    high_lights: str
    low_lights: str
    explanation: str

    def __init__(self, high_lights: str, low_lights: str, explanation: str):
        self.high_lights = high_lights
        self.low_lights = low_lights
        self.explanation = explanation


class EvaluationGenerator:
    """
    Use the resume and a question set for this stage to generate a question for the interviewee
    """
    llm: BaseChatModel
    template: ChatPromptTemplate

    def __init__(self, llm: BaseChatModel, template: ChatPromptTemplate):
        self.llm = llm
        self.template = template

    @classmethod
    def build(cls, llm: BaseChatModel) -> "EvaluationGenerator":
        messages = [
            HumanMessagePromptTemplate.from_template(EVALUATE_TEMPLATE)
        ]
        evaluation_template = ChatPromptTemplate(
            input_variables=["question_descriptions", "history"], messages=messages
        )
        return cls(llm, evaluation_template)

    @classmethod
    def parse_result(cls, result: LLMResult) -> Evaluation | None:
        text = get_text_from_llm_result(result)
        if text:
            try:
                evaluation_str = json.loads(text)
                evaluation = Evaluation(evaluation_str["high_lights"],
                                        evaluation_str["low_lights"],
                                        evaluation_str["explanation"])
                return evaluation
            except Exception:
                logger.exception("Failed to parse evaluation result")
        return None

    @classmethod
    def format_eval_question_description(cls, stages: InterviewStage | list[InterviewStage]) -> str:
        if isinstance(stages, list):
            return str([stage.questions[0].eval_requirements for stage in stages])
        return stages.questions[0].eval_requirements

    async def __generate(self, messages):
        result = await self.llm.agenerate(messages=[messages])
        evaluation = self.parse_result(result)
        return evaluation

    async def arun(self, stage: InterviewStage | list[InterviewStage], history: list[list[str]]) -> Evaluation:
        """
            Generate a evaluation for one stage or total
        """
        messages = self.template.format_messages(question_description=self.format_eval_question_description(stage),
                                                 history=history)
        return await self.__generate(messages)

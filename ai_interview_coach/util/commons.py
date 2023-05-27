from langchain.chat_models import ChatOpenAI

from evaluation_generator.evaluate import EvaluationGenerator
from question_generator.follow_up_base import FollowUpGenerator
from question_generator.question_base import QuestionGenerator
from stage.stage_judge import StageJudge

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.0,
    streaming=True,
)
llm_4 = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.0,
    streaming=True,
)
stage_judge = StageJudge.build(llm=llm)
question_generator = QuestionGenerator.build(llm=llm_4)
follow_up_generator = FollowUpGenerator.build(llm=llm_4)
evaluation_generator = EvaluationGenerator.build(llm=llm_4)

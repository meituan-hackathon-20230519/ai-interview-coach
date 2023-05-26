import random
from typing import cast

from langchain.chat_models import ChatOpenAI

from question_generator.question_base import QuestionGenerator
from stage.stage_base import StageJudge
from stage.stages import InterviewStage, INTERVIEW_STAGES, InterviewQuestion
from utils import StreamingCallbackHandler

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.0,
    streaming=True,
)
stage_judge = StageJudge.build(llm=llm)
question_generator = QuestionGenerator.build(llm=llm)
max_rounds = 3


class Resume:
    def __init__(self, self_intro: str = "", experience: str = ""):
        self.self_intro = self_intro
        self.experience = experience

    def format(self):
        return f"""
        =====自我介绍=====
        {self.self_intro}
        =====项目经历=====
        {self.experience}
        """


class InterviewCoach:
    async def agenerate_output(
            self,
            history: list[list[str | None]],
            resume: Resume,
            stage_index: int,
            callback: StreamingCallbackHandler,
    ) -> tuple[int, str]:
        current_stage = INTERVIEW_STAGES[stage_index]
        # Call LLM to determine whether to stay at the current stage (and reason why so)
        question = cast(InterviewQuestion, random.sample(current_stage.questions, 1))
        status = await stage_judge.arun(question=question.question,
                                        question_description=question.follow_up_requirements, history=history)
        # If yes, check if we have reached maximum rounds. If reached max, go to next stage and generate the question.
        if status:
            if len(history) >= max_rounds:
                stage_index = stage_index + 1
                # generate next stage question
                generate_question = await question_generator.arun(question=question.question,
                                                                  requirements=question.follow_up_requirements,
                                                                  resume=resume.format(),
                                                                  history=history)
                return stage_index + 1, generate_question
        # If staying, call LLM to generate follow-up question;
        # Otherwise, call LLM to generate feedback and generate question in the next stage in parallel
        await callback.on_new_token("That's cool")
        return stage_index, ""

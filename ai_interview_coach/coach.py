import copy
import random
from typing import cast

from langchain.chat_models import ChatOpenAI

from question_generator.follow_up_base import FollowUpGenerator
from question_generator.question_base import QuestionGenerator
from stage.stage_judge import StageJudge
from stage.stages import INTERVIEW_STAGES, InterviewQuestion
from utils import StreamingCallbackHandler

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.0,
    streaming=True,
)
stage_judge = StageJudge.build(llm=llm)
question_generator = QuestionGenerator.build(llm=llm)
follow_up_generator = FollowUpGenerator.build(llm=llm)
max_rounds = 4


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
    history_index = 0

    async def agenerate_output(
            self,
            history: list[list[str | None]],
            resume: Resume,
            stage_index: tuple[int, int],
            callback: StreamingCallbackHandler,
    ) -> tuple[tuple[int, int], str]:
        current_stage = INTERVIEW_STAGES[stage_index[0]]
        # Call LLM to determine whether to stay at the current stage (and reason why so)
        question = cast(InterviewQuestion, current_stage.questions[stage_index[1]])
        copy_history = copy.deepcopy(history)
        pass_history = copy_history[self.history_index:]
        pass_history[0][0] = ""  # 去掉用户上一轮的输入
        if len(pass_history) < max_rounds:
            satisfy = await stage_judge.arun(question=question.question,
                                             question_description=question.follow_up_requirements, history=pass_history)
        else:
            satisfy = True
        # If stayed, check if we have reached maximum rounds.
        # If reached max, go to next stage and generate the question.
        if not satisfy:
            # If staying, call LLM to generate follow-up question;
            if len(history) < max_rounds:  # 追问
                follow_up_question = await follow_up_generator.arun(question=question.question,
                                                                    requirements=question.follow_up_requirements,
                                                                    history=pass_history,
                                                                    callback=callback)
                return stage_index, follow_up_question
        # Otherwise, call LLM to generate feedback and generate question in the next stage in parallel
        else:
            # 使用下一阶段问题模板进行问题生成
            self.history_index = len(history) - 1
            new_stage_index = stage_index[0] + 1
            if new_stage_index < len(INTERVIEW_STAGES):
                new_stage = INTERVIEW_STAGES[new_stage_index]
                question_index = random.randint(0, len(new_stage.questions) - 1)
                stage_index = (new_stage_index, question_index)
                question = INTERVIEW_STAGES[new_stage_index].questions[question_index]
                # 生成下阶段问题，只用到简历和问题模板
                generate_question = await question_generator.arun(question=question.question,
                                                                  resume=resume.format(),
                                                                  callback=callback)
                # TODO 需要调用当前阶段总结
            else:
                # TODO 需要调用所有阶段总结
                return (0, 0), "summary"
            return stage_index, generate_question

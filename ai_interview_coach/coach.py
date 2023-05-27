import asyncio
import copy
import logging
import random
from typing import cast

from stage.stages import INTERVIEW_STAGES, InterviewQuestion
from util.commons import stage_judge, follow_up_generator, question_generator, evaluation_generator
from utils import StreamingCallbackHandler

logger = logging.getLogger(__name__)

max_rounds = 4

SELF_INTRO = """
我叫李冲，毕业于北京邮电大学。拥有2年的产品工作经验，曾在饿了么任职，负责饿了么履约链路相关产品设计工作，熟悉后台产品架构。我擅长进行产品可行性分析、需求梳理与规划，以及项目管理。有一定的同理心，具备积极主动、自驱的工作态度。
"""

SELF_EXPERIENCE = """
饿了么 - 产品经理（2021.7-至今）

1.饿了么商超取餐时效优化项目（2021.10-2021.12）
 * 负责需求梳理，与销售业务合作，结合商超实际业务场景考察，梳理业务需求。
 * 通过对取餐时效数据进行深度挖掘，识别关键问题，提出解决方案
 * 协调各部门资源，推动项目落地，使取餐时效提升8%

2.饿了么智能调度系统升级（2022.02 - 2022.05）
 * 负责可行性分析，评估升级智能调度系统的必要性和可行性
 * 设计调度系统升级方案，并与技术团队合作，完成需求文档编写
 * 跟进项目进度，确保项目按时上线，配送效率提升了12%

3.饿了么骑手接单范围优化项目（2022.07 - 2022.09）
 * 分析骑手接单范围与送餐效率的关系，提出优化建议
 * 与数据团队合作，对接单范围进行精细化调整，优化骑手接单体验
 * 项目实施后，有效降低骑手因接单范围过大导致的无效接单率，提升了整体配送效率
"""


class Resume:
    def __init__(self, self_intro: str = SELF_INTRO, experience: str = SELF_EXPERIENCE):
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
    interview_stage_list = []
    evaluation_list = []

    async def agenerate_output(
            self,
            history: list[list[str | None]],
            resume: Resume,
            stage_index: tuple[int, int],
            session_id: str,
            callback: StreamingCallbackHandler,
    ) -> tuple[tuple[int, int], str]:
        if stage_index[0] >= len(INTERVIEW_STAGES):
            await callback.on_new_token("面试结束！请点击下一步获取面试评价")
            return stage_index, ""
        current_stage = INTERVIEW_STAGES[stage_index[0]]
        self.evaluation_list.append(current_stage)
        # Call LLM to determine whether to stay at the current stage (and reason why so)
        question = cast(InterviewQuestion, current_stage.questions[stage_index[1]])
        copy_history = copy.deepcopy(history)
        pass_history = copy_history[self.history_index:]
        pass_history[0][0] = ""  # 去掉用户上一轮的输入
        if len(pass_history) < max_rounds:
            satisfy = await stage_judge.arun(question=question.question,
                                             requirements=question.follow_up_requirements, history=pass_history)
        else:
            satisfy = True
        # If stayed, check if we have reached maximum rounds.
        # If reached max, go to next stage and generate the question.
        if not satisfy and len(pass_history) < max_rounds:  # 追问
            # If staying, call LLM to generate follow-up question;
            if stage_index[0] == 3:  # 拓展问题阶段和倒数第二个阶段不用连贯，传入历史修改
                follow_up_question = await follow_up_generator.arun(question=question.question,
                                                                    requirements=question.follow_up_requirements,
                                                                    history=pass_history,
                                                                    callback=callback)
            else:
                follow_up_question = await follow_up_generator.arun(question=question.question,
                                                                    requirements=question.follow_up_requirements,
                                                                    history=history[-4:],
                                                                    callback=callback)
            logger.info(f"follow up question:{follow_up_question}, stage index:{stage_index}")
            return stage_index, follow_up_question

        # Otherwise, call LLM to generate feedback and generate question in the next stage in parallel
        else:
            # 使用下一阶段问题模板进行问题生成
            self.history_index = len(history) - 1
            new_stage_index = stage_index[0] + 1
            copy_history = copy.deepcopy(history)
            pass_history = copy_history[self.history_index:]
            pass_history[0][0] = ""  # 去掉用户上一轮的输入
            logger.info(f"round now:{len(pass_history)}")
            if new_stage_index < len(INTERVIEW_STAGES):
                new_stage = INTERVIEW_STAGES[new_stage_index]
                question_index = random.randint(0, len(new_stage.questions) - 1)
                stage_index = (new_stage_index, question_index)
                question = INTERVIEW_STAGES[new_stage_index].questions[question_index]
                # 生成下阶段问题，只用到简历和问题模板
                # 当前阶段总结，使用current_stage
                if stage_index[0] == 3:  # 拓展问题阶段和倒数第二个阶段不用连贯，传入历史修改
                    generate_question = await question_generator.arun(question=question.question,
                                                                      resume=resume.format(), callback=callback,
                                                                      history=pass_history)
                else:
                    generate_question = await question_generator.arun(question=question.question,
                                                                      resume=resume.format(),
                                                                      callback=callback,
                                                                      history=history[-4:])
                # update stage cache
                evaluation_generator.update_stage_cache(session_id, current_stage)
                logger.info(f"generate new question:{generate_question}, stage index:{stage_index}")
            else:
                await callback.on_new_token("面试结束！请点击下一步获取面试评价")
                return stage_index, ""
            return stage_index, generate_question

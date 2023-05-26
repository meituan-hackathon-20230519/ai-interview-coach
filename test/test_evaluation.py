import asyncio
import json
import unittest
import uuid

from langchain.chat_models import ChatOpenAI

from evaluation_generator.evaluate import EvaluationGenerator
from stage.stages import INTERVIEW_STAGES


class EvaluationGenerateTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            streaming=True,
        )
        self.generator = EvaluationGenerator.build(self.llm)

    # @unittest.skip("skip")
    def test_generate_work_experience(self):
        stage = INTERVIEW_STAGES[1]

        # history = [[
        #     "我对您之前在饿了么的取餐时效优化项目比较感兴趣，可以介绍一下吗？",
        #     """
        #     【背景】在商超场景下，配送现有流程：商家线上发单→配送调度派单→线下商家拣货出餐→骑手到店取餐。
        #     【存在问题】在疫情、门店大促等门店单量密度非常高的场景下，存在两个问题：1、商家拣货出餐时长变长，骑手到店后商家还未出餐。2、外卖堆积骑手很难快速找到属于自己的货品。会导致：骑手取货效率变低，从而导致订单超时，影响用户体验。
        #     【措施】因此通过搭建扫码取货功能，不直接分配任务给骑手，而是改由骑手扫码的方式获取配送任务。来解决此问题。
        #         """
        # ], [
        #     "你在这个项目中担任了什么角色？",
        #     "是产品主R/主负责人"
        # ], [
        #     "这个项目中还涉及到哪些团队和角色？",
        #     "BU外部主要涉及到闪购商家端、闪购开放平台、订单中心、打印云协同4个部门，配送内部涉及运单、调度、ETA、客户运营、POI、活动、管控、骑手端共8个方向。"
        # ]]

        history = [[
            "我对您之前在饿了么的取餐时效优化项目比较感兴趣，可以介绍一下吗？",
            """
            【背景】在商超场景下，配送现有流程：商家线上发单→配送调度派单→线下商家拣货出餐→骑手到店取餐。
            【存在问题】在疫情、门店大促等门店单量密度非常高的场景下，存在两个问题：1、商家拣货出餐时长变长，骑手到店后商家还未出餐。2、外卖堆积骑手很难快速找到属于自己的货品。会导致：骑手取货效率变低，从而导致订单超时，影响用户体验。
            【措施】因此通过搭建扫码取货功能，不直接分配任务给骑手，而是改由骑手扫码的方式获取配送任务。来解决此问题。
            【团队成员】我作为产品主要负责人，协同部门内外12个不同方向的团队保证产品功能陆地。
            【结果】最终取得提升骑手取货效率8pp的结果。大促场景订单取货完成率从88%提升至96%。提升结果符合业务预期，并因此能力成功助力业务签下山姆等客户。
            """
        ]]

        session_id = str(uuid.uuid4())
        asyncio.run(self.generator.update_cache(session_id, [stage]))
        result = asyncio.run(self.generator.arun(stage, str(uuid.uuid4()), history, False))

        print(result.response)

    def test_generate_total_interview(self):
        stages = INTERVIEW_STAGES

        history = [[
            "您好，我是本次的面试官，我姓王，是美团的产品经理，现在开始面试。请先自我介绍一下。",
            """
            您好，我叫李冲，毕业于天津大学，目前工作5年，现在在美团，任职3年，负责配送履约方向运单中心的相关产品工作，之前在瓜子二手车，主要负责供应链方向。
            """
        ], [
            "我对您之前在饿了么的取餐时效优化项目比较感兴趣，可以介绍一下吗？",
            """
            【背景】在商超场景下，配送现有流程：商家线上发单→配送调度派单→线下商家拣货出餐→骑手到店取餐。
            【存在问题】在疫情、门店大促等门店单量密度非常高的场景下，存在两个问题：1、商家拣货出餐时长变长，骑手到店后商家还未出餐。2、外卖堆积骑手很难快速找到属于自己的货品。会导致：骑手取货效率变低，从而导致订单超时，影响用户体验。
            【措施】因此通过搭建扫码取货功能，不直接分配任务给骑手，而是改由骑手扫码的方式获取配送任务。来解决此问题。
            【团队成员】我作为产品主要负责人，协同部门内外12个不同方向的团队保证产品功能陆地。
            【结果】最终取得提升骑手取货效率8pp的结果。大促场景订单取货完成率从88%提升至96%。提升结果符合业务预期，并因此能力成功助力业务签下山姆等客户。
            """
        ], [
            "项目中遇到的最大的挑战是什么？",
            """
            该项目涉及到公司的核心产品功能，并且有一定的广度和复杂性，需要协调不同团队和部门的合作，同时在时间上又很紧迫。我作为该项目的主要负责人，除了负责整体产品方案的输出外，还需要负责项目的进度管理、协调不同团队的工作。
            在项目执行的过程中，我们面临了一些技术问题和人力问题。其中一个主要的问题是相关人员的分配和管理，在一段时间内，由于其他项目同时也在艰难进行中，导致我们缺乏核心人员。此外，由于技术方案的调整和优化，导致项目延期风险不断增加。
            我采取了一系列的行动方案，来解决这些问题。首先，及时向上反馈暴露风险。其次，我与不同团队中的技术负责人协调开发和管理流程。
            最终我们顺利完成了项目，达到了设定的目标。我从中获得了危机处理中的灵活应对能力和沉着决策能力。
            """
        ], [
            "可以说下你对自己未来3-5年的规划吗？",
            """
            我的未来3-5年的规划包括两个方面。首先是不断提升自己的技能水平和工作经验，从而在产品经理这个职业领域中更加专业和有竞争力。我会持续关注行业动态和趋势，不断学习和掌握新的技能和知识，如人工智能、大数据、用户研究等，以便更好地服务用户和推动公司业务发展。
            其次是拥有自己的团队和管理经验。我希望能够成为一名优秀的团队管理者，能够领导并激励团队成员，实现团队和自己的共同目标。我相信这也是我未来发展的一个重要方向。
            """
        ]
        ]

        session_id = str(uuid.uuid4())
        asyncio.run(self.generator.update_cache(session_id, stages))
        result = asyncio.run(self.generator.arun(stages, session_id, history, True))

        print(result.response)

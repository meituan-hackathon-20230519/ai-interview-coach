import asyncio
import unittest

from langchain.chat_models import ChatOpenAI

from stage.stage_judge import StageJudge


class StageJudgeTestCase(unittest.TestCase):

    def setUp(self) -> None:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            streaming=True,
        )
        self.stage = StageJudge.build(llm=llm)

    def test_self_introduction(self):
        question = "您好，我是本次的面试官，我姓王，是美团的产品经理，现在开始面试。请先自我介绍一下"
        question_description = """
            职业经历介绍
            1.工作年限
            2.历史任职公司
            3.负责工作内容
            """
        # NO
        # answer = """
        #     您好，我叫小王，毕业于北京邮电大学，目前在拼多多工作。
        # """

        # YES
        answer = """
            您好，我叫李冲，毕业于天津大学，目前工作5年，现在在美团，任职3年，负责配送履约方向运单中心的相关产品工作，之前在瓜子二手车，主要负责供应链方向
        """
        history = [[question, answer]]

        result = asyncio.run(self.stage.arun(question, question_description, history))
        print(result)

    def test_work_introduction(self):
        question = "我对您之前在饿了么的取餐时效优化项目比较感兴趣，可以介绍一下吗？"
        question_description = """
            项目的背景
            项目的任务/要解决的问题
            采取的措施/动作
            项目有多少人
            你担任什么角色
            你达成的结果
            整个团队达成的结果
            结果是否符合预期
            包含数据支持
            """
        # NO
        answer = """
            只是简单的流程实现，包含了商家线上发单→配送调度派单→线下商家拣货出餐→骑手到店取餐
        """

        # YES
        # answer = """
        #     【背景】在商超场景下，配送现有流程：商家线上发单→配送调度派单→线下商家拣货出餐→骑手到店取餐。
        #     【存在问题】在疫情、门店大促等门店单量密度非常高的场景下，存在两个问题：1、商家拣货出餐时长变长，骑手到店后商家还未出餐。 \
        #     2、外卖堆积骑手很难快速找到属于自己的货品。会导致：骑手取货效率变低，从而导致订单超时，影响用户体验。
        #     【措施】因此通过搭建扫码取货功能，不直接分配任务给骑手，而是改由骑手扫码的方式获取配送任务。来解决此问题。
        # """
        history = [[question, answer]]

        result = asyncio.run(self.stage.arun(question, question_description, history))
        print(result)

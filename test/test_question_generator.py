import asyncio

from langchain.chat_models import ChatOpenAI
from question_generator.base import QuestionGenerator

test_llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.0,
    streaming=True,
)

question_generator = QuestionGenerator.build(test_llm)

resume = """
自我介绍：

我叫小王，毕业于北京邮电大学。拥有2年的产品工作经验，曾在饿了么任职，负责饿了么履约链路相关产品设计工作，熟悉后台产品架构。我擅长进行产品可行性分析、需求梳理与规划，以及项目管理。有一定的同理心，具备积极主动、自驱的工作态度。

项目经历：
饿了么 - 产品经理（2021.7-至今）

1.饿了么商超取餐时效优化项目（2021.10-2021.12）
    a.负责需求梳理，与销售业务合作，结合商超实际业务场景考察，梳理业务需求。
    b.通过对取餐时效数据进行深度挖掘，识别关键问题，提出解决方案
    c.协调各部门资源，推动项目落地，使取餐时效提升8%

2.饿了么智能调度系统升级（2022.02 - 2022.05）
    a.负责可行性分析，评估升级智能调度系统的必要性和可行性
    b.设计调度系统升级方案，并与技术团队合作，完成需求文档编写
    c.跟进项目进度，确保项目按时上线，配送效率提升了12%

3.饿了么骑手接单范围优化项目（2022.07 - 2022.09）
    a.分析骑手接单范围与送餐效率的关系，提出优化建议
    b.与数据团队合作，对接单范围进行精细化调整，优化骑手接单体验
    c.项目实施后，有效降低骑手因接单范围过大导致的无效接单率，提升了整体配送效率
"""
questions = ["请描述一下你在上一家公司的某段经历?", "你印象最深刻的一个项目是什么？", "项目中遇到最大的挑战是什么？", "项目中你做的好的点是什么?"]
for question in questions:
    print(asyncio.run(question_generator.arun(question=question,
                                              requirements="""""",
                                              resume=resume,
                                              history=[[]])))

questions = ["对自己未来3-5年的规划？", "总结一下自己的优劣势", "是否了解我们公司？"]
for question in questions:
    print(asyncio.run(question_generator.arun(question=question,
                                              requirements="""""",
                                              resume="""""",
                                              history=[[]])))

print(asyncio.run(question_generator.arun(question="",
                                          requirements="""
1.项目背景
2.解决的问题
3.采取的措施
4.项目规模
5.担任的角色
6.达成的结果
7.团队达成的结果
8.结果是否符合预期
9.数据支持
                                          """,
                                          resume="""""",
                                          history=[[None, "我对您之前在饿了么的取餐时效优化项目比较感兴趣，可以介绍一下吗？"],
                                                   ["""\
背景是在商超场景下，配送现有流程：商家线上发单→配送调度派单→线下商家拣货出餐→骑手到店取餐。
主要存在的问题是在疫情、门店大促等门店单量密度非常高的场景下，存在两个问题：1、商家拣货出餐时长变长，骑手到店后商家还未出餐。2、外卖堆积骑手很难快速找到属于自己的货品。会导致：骑手取货效率变低，从而导致订单超时，影响用户体验。
我在其中担任的角色是产品经理，采取的措施是通过搭建扫码取货功能，不直接分配任务给骑手，而是改由骑手扫码的方式获取配送任务。来解决此问题。
                                                   """, None]])))

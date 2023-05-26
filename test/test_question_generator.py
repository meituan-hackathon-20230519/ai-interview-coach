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
自我介绍：我叫小王，毕业于北京邮电大学。拥有2年的产品工作经验，曾在拼多多任职，负责多多买菜相关产品设计工作。我擅长进行产品可行性分析、需求梳理与规划，以及项目管理。有一定的同理心，具备积极主动、自驱的工作态度。

项目经历：
拼多多 - 产品经理（多多买菜） (2021.5-2023.5)
在拼多多任职期间，主要负责多多买菜相关产品设计工作，参与了多个重要项目的规划与实施。以下为部分项目经历：

1.多多买菜需求梳理与优化
负责对多多买菜业务需求进行梳理，分析各功能模块的优先级和可行性
制定详细的产品需求文档，并与技术团队进行沟通，确保产品设计和实现符合需求
通过对用户反馈的收集与分析，对产品进行迭代优化，提高用户体验和满意度

2.多多买菜供应链优化项目 
a.分析现有供应链系统的痛点和挑战，制定针对性的改进措施
b.负责与技术团队、运营团队、供应商等合作伙伴沟通，推动项目实施
c.通过项目管理，确保项目按计划进行，实现供应链效率提升，降低成本，提高用户满意度

3.多多买菜数据分析与运营优化 
a.利用SQL等工具分析多多买菜的运营数据，挖掘潜在的业务机会和改进方向
b.根据数据分析结果，提出具体的运营策略和产品优化建议
c.协助运营团队实施优化措施，跟踪效果，实现业绩提升
"""
print(asyncio.run(question_generator.arun(question="项目中遇到最大的挑战是什么？",
                                          requirements="""
                                          1.STAR法则
                                          2.发生了什么问题
                                          3.发生问题的原因
                                          4.针对原因的解决方式
                                          5.解决的结果
                                          6.总结经验
                                          """,
                                          resume=resume,
                                          history=[[]])))

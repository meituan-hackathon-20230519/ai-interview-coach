from typing import NamedTuple


class InterviewQuestion(NamedTuple):
    question: str
    follow_up_requirements: str
    eval_requirements: str


class InterviewStage(NamedTuple):
    stage_name: str
    questions: list[InterviewQuestion]


_SELF_INTRO_FOLLOW_UP_REQS = '''
个人基本情况介绍
- 姓名
- 毕业院校
- 专业方向
职业经历介绍
- 工作年限
- 历史任职公司
- 负责工作内容
'''

_PROJECT_QUESTION_FOLLOW_UP_REQS = '''
- 项目的背景
- 项目的任务/要解决的问题
- 采取的措施/动作
- 项目有多少人
- 你担任什么角色
- 你达成的结果
- 整个团队达成的结果
- 结果是否符合预期
- 包含数据支持
'''

_PROJECT_QUESTION_2_FOLLOW_UP_REQS = '''
- 发生了什么问题
- 发生问题的原因
- 针对原因的解决方式
- 解决的结果
- 总结经验
'''

_PROJECT_QUESTION_2_EVAL_REQS = '''
- STAR法则描述项目
- 总结经验
'''

INTERVIEW_STAGES = [
    InterviewStage("自我介绍", [
        InterviewQuestion(
            "你好，我是面试官，请介绍一下你自己",
            _SELF_INTRO_FOLLOW_UP_REQS,
            _SELF_INTRO_FOLLOW_UP_REQS
        )
    ]),
    InterviewStage("项目提问", [
        InterviewQuestion(
            "你印象最深刻的一个项目是什么？",
            _PROJECT_QUESTION_FOLLOW_UP_REQS,
            _PROJECT_QUESTION_FOLLOW_UP_REQS
        ),
    ]),
    InterviewStage("项目提问2", [
        InterviewQuestion(
            "在你提到的印象最深刻的项目中遇到最大的挑战是什么？",
            _PROJECT_QUESTION_2_FOLLOW_UP_REQS,
            _PROJECT_QUESTION_2_EVAL_REQS
        ),
    ]),
    InterviewStage("扩展问题", [
        InterviewQuestion(
            "对自己未来3-5年的规划？",
            '''TODO''',
            '''TODO'''
        ),
        InterviewQuestion(
            "总结一下自己的优劣势",
            '''TODO''',
            '''TODO'''
        ),
        InterviewQuestion(
            "是否了解我们公司？",
            '''TODO''',
            '''TODO'''
        ),
    ]),
]

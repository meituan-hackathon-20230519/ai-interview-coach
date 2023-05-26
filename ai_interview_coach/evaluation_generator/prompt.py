EVALUATE_TEMPLATE = """
Given a question template, bullet points about what interviewee's answer should cover, and chat history, you will \
evaluate the interviewee's answers. Follow the instructions below to generate a summary:
1. First summarized human's input.
2. Then think what bullet points the summary has and has not covered.
3. Summarize what bullet points the summary has and has not covered, and avoid merely listing your summary. Then \
generate a final professional evaluation of the interviewee's performance.

REMEMBER: 
The output MUST be in Chinese.
If you need to refer to the "interviewer" when summarizing, please use "你" instead.
DO NOT make up facts!

<< BULLET POINTS >>
{requirements}

<< CHAT HISTORY >>
{history}

<< OUTPUT >>
"""

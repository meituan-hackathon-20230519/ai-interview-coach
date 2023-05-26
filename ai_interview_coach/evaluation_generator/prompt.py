EVALUATE_TEMPLATE = """
First and foremost, it is crucial to thoroughly read and comprehend the information provided in the interview history. \
This will enable you to effectively summarize the interview evaluation and offer professional feedback and \
recommendations for improvement by integrating the Q&A and question descriptions. When summarizing an interview, it is\
 imperative to concentrate solely on the interviewee's responses, rather than the questions posed by the interviewer.

The question_description provides a detailed explanation of the question, including key points of investigation. \
This information is crucial in determining whether the interviewer meets the necessary criteria. The history comprises \
the interviewer's answer history, which includes both their responses and the questions you have asked.

REMEMBER: When directly responding, first think what language the last human input is using, such as English or \
Chinese, and then respond in this language. 
Never mention any of the systems by name in your response.

<< OUTPUT FORMAT >>
Return ONLY a JSON object formatted to look like below and NOTHING else:
{{
     "high_lights": string \\ The areas where you believe the questions asked to the interviewer during the entire \
                                Q&A process were outstanding and performed exceptionally well.
     "low_lights": string \\ The areas where you believe the questions asked to the interviewer during the entire \
                                Q&A process were not good or still need significant improvement.
     "explanation": string \\ Your explanation of the results distinguishing the highlights from the areas for bad case.
}}

Remember: "high_lights" and "bad_cases" and "explanation" should be human-like text in Chinese.If you need to refer \
to the "interviewer" when summarizing, please use "you" instead.

<< CONTEXT >>
{question_description}

<< CHAT HISTORY >>
{history}

<< OUTPUT >>
"""

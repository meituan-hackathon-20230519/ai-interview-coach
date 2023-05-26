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

You should return response like this: 
high lights: The areas where you believe the questions asked to the interviewer during the entire Q&A process were outstanding \
and performed exceptionally well.
bad case: The areas where you believe the questions asked to the interviewer during the entire Q&A process were not good or \
still need significant improvement.
explanation: Your explanation of the results distinguishing the highlights from the areas for bad case.

REMEMBER: response should be human-like text in Chinese.If you need to refer to the "interviewer" when summarizing, \
please use "you" instead.Each section of content is separated by a line break.

<< CONTEXT >>
{question_description}

<< CHAT HISTORY >>
{history}

<< OUTPUT >>
"""

FOLLOW_QUESTION_GENERATE_TEMPLATE = """
Given a question template, bullet points about what interviewee's answer should cover, and chat history, you will \
ask a follow-up question to the last human input. Follow the instructions below to generate a question:
1. First think if last human input is clear and complete. If not, ask for clarification.
2. Otherwise, use your reasoning and pick bullet points that the interviewee did not cover in his/her answer.
3. Generate a concise question based on the question template, the picked bullet points from step 2 and the chat history.

<< QUESTION TEMPLATE >>
{question}

<< BULLET POINTS >>
{requirements}

<< CHAT HISTORY >>
{history}

<< OUTPUT >>
"""
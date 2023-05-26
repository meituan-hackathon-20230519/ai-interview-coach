from stage import InterviewStage, INTERVIEW_STAGES
from utils import StreamingCallbackHandler


class Resume:
    def __init__(self, self_intro: str = "", experience: str = ""):
        self.self_intro = self_intro
        self.experience = experience


class InterviewCoach:
    async def agenerate_output(
            self,
            history: list[list[str | None]],
            resume: Resume,
            current_stage: InterviewStage,
            callback: StreamingCallbackHandler,
    ) -> InterviewStage:
        # Call LLM to determine whether to stay at the current stage (and reason why so)
        # If no, check if we have reached maximum rounds
        # If staying, call LLM to generate follow-up question;
        # Otherwise, call LLM to generate feedback and generate question in the next stage in parallel
        await callback.on_new_token("That's cool")
        return INTERVIEW_STAGES[1]

from queue import Queue


class StreamingCallbackHandler:
    """Callback handler for streaming LLM responses to a queue."""

    def __init__(self, q: Queue):
        self.q = q

    async def on_new_token(self, token: str) -> None:
        self.q.put(token)

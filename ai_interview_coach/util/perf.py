import time
from typing import Callable, Any

from langchain.schema import LLMResult


def start_timer() -> Callable[[], float]:
    start = time.perf_counter()

    def elapsed():
        return time.perf_counter() - start

    return elapsed


def get_token_usage(llm_result: LLMResult) -> Any:
    return llm_result.llm_output['token_usage']

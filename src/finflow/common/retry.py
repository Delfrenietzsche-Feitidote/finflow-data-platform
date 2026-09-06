import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def retry(
    operation: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    last_exception = None

    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as exc:
            last_exception = exc

            if attempt == max_attempts - 1:
                raise

            delay = base_delay * (2 ** attempt)
            time.sleep(delay)

    raise last_exception
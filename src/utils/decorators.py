"""Utility decorators for outlier-x."""

import functools
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def timer(func: F) -> F:
    """
    Decorator to measure function execution time.

    Args:
        func: Function to be timed

    Returns:
        Wrapped function that logs execution time
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} executed in {elapsed:.2f} seconds")
        return result

    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator

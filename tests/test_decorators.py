"""Tests for the decorators module."""

import time
from unittest.mock import patch

import pytest

from src.utils.decorators import timer, retry


class TestTimerDecorator:
    """Test the timer decorator."""

    def test_timer_basic_functionality(self, capsys):
        """Test timer decorator prints execution time."""
        @timer
        def sample_function():
            time.sleep(0.1)
            return "done"

        result = sample_function()

        assert result == "done"

        # Check output
        captured = capsys.readouterr()
        assert "sample_function executed in" in captured.out
        assert "seconds" in captured.out

    def test_timer_with_arguments(self, capsys):
        """Test timer decorator with function arguments."""
        @timer
        def add_numbers(a, b):
            return a + b

        result = add_numbers(5, 3)

        assert result == 8
        captured = capsys.readouterr()
        assert "add_numbers executed in" in captured.out

    def test_timer_with_keyword_arguments(self, capsys):
        """Test timer decorator with keyword arguments."""
        @timer
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("Alice", greeting="Hi")

        assert result == "Hi, Alice!"
        captured = capsys.readouterr()
        assert "greet executed in" in captured.out

    def test_timer_measures_time_accurately(self, capsys):
        """Test timer measures execution time with reasonable accuracy."""
        @timer
        def sleep_function():
            time.sleep(0.2)

        sleep_function()

        captured = capsys.readouterr()
        # Should show approximately 0.2 seconds (allow some tolerance)
        assert "0.2" in captured.out or "0.1" in captured.out

    def test_timer_with_exception(self, capsys):
        """Test timer decorator when function raises exception."""
        @timer
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

        # Timer should still print (before exception propagates)
        # Note: This behavior depends on decorator implementation

    def test_timer_preserves_function_name(self):
        """Test timer decorator preserves function metadata."""
        @timer
        def my_function():
            """My function docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring."

    def test_timer_with_return_values(self, capsys):
        """Test timer decorator preserves return values."""
        @timer
        def calculate():
            return 42

        result = calculate()
        assert result == 42

        @timer
        def return_multiple():
            return 1, 2, 3

        result = return_multiple()
        assert result == (1, 2, 3)

    def test_timer_with_zero_duration(self, capsys):
        """Test timer with very fast function."""
        @timer
        def instant_function():
            return "instant"

        result = instant_function()

        assert result == "instant"
        captured = capsys.readouterr()
        assert "executed in" in captured.out


class TestRetryDecorator:
    """Test the retry decorator."""

    def test_retry_success_on_first_attempt(self):
        """Test retry decorator when function succeeds on first try."""
        @retry(max_attempts=3, delay=0.01)
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_retry_success_on_second_attempt(self):
        """Test retry decorator succeeds after one failure."""
        call_count = {"count": 0}

        @retry(max_attempts=3, delay=0.01)
        def function_fails_once():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("First attempt fails")
            return "success"

        result = function_fails_once()
        assert result == "success"
        assert call_count["count"] == 2

    def test_retry_success_on_last_attempt(self):
        """Test retry decorator succeeds on final attempt."""
        call_count = {"count": 0}

        @retry(max_attempts=3, delay=0.01)
        def function_fails_twice():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise ValueError("Not yet")
            return "success"

        result = function_fails_twice()
        assert result == "success"
        assert call_count["count"] == 3

    def test_retry_all_attempts_fail(self):
        """Test retry decorator when all attempts fail."""
        call_count = {"count": 0}

        @retry(max_attempts=3, delay=0.01)
        def always_fails():
            call_count["count"] += 1
            raise ValueError(f"Attempt {call_count['count']} failed")

        with pytest.raises(ValueError, match="Attempt 3 failed"):
            always_fails()

        assert call_count["count"] == 3

    def test_retry_with_custom_attempts(self):
        """Test retry decorator with custom max attempts."""
        call_count = {"count": 0}

        @retry(max_attempts=5, delay=0.01)
        def function_needs_five_attempts():
            call_count["count"] += 1
            if call_count["count"] < 5:
                raise ValueError("Not yet")
            return "success"

        result = function_needs_five_attempts()
        assert result == "success"
        assert call_count["count"] == 5

    def test_retry_exponential_backoff(self):
        """Test retry decorator uses exponential backoff."""
        call_times = []

        @retry(max_attempts=3, delay=0.1, backoff=2.0)
        def function_with_backoff():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Not yet")
            return "success"

        result = function_with_backoff()
        assert result == "success"

        # Check delays between attempts
        # First retry: ~0.1s, Second retry: ~0.2s
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert delay1 >= 0.08  # Allow some tolerance

        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert delay2 >= 0.18  # Should be ~2x first delay

    def test_retry_with_different_exceptions(self):
        """Test retry decorator handles different exception types."""
        call_count = {"count": 0}

        @retry(max_attempts=4, delay=0.01)
        def mixed_exceptions():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("First error")
            elif call_count["count"] == 2:
                raise TypeError("Second error")
            elif call_count["count"] == 3:
                raise RuntimeError("Third error")
            return "success"

        result = mixed_exceptions()
        assert result == "success"

    def test_retry_with_arguments(self):
        """Test retry decorator with function arguments."""
        call_count = {"count": 0}

        @retry(max_attempts=2, delay=0.01)
        def add_with_retry(a, b):
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("First attempt")
            return a + b

        result = add_with_retry(3, 5)
        assert result == 8

    def test_retry_with_keyword_arguments(self):
        """Test retry decorator with keyword arguments."""
        call_count = {"count": 0}

        @retry(max_attempts=2, delay=0.01)
        def greet_with_retry(name, greeting="Hello"):
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("First attempt")
            return f"{greeting}, {name}!"

        result = greet_with_retry("Bob", greeting="Hi")
        assert result == "Hi, Bob!"

    def test_retry_preserves_function_name(self):
        """Test retry decorator preserves function metadata."""
        @retry(max_attempts=3)
        def my_function():
            """My function docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring."

    def test_retry_with_zero_delay(self):
        """Test retry decorator with zero delay."""
        call_count = {"count": 0}

        @retry(max_attempts=3, delay=0.0)
        def instant_retry():
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise ValueError("Retry")
            return "success"

        start_time = time.time()
        result = instant_retry()
        elapsed_time = time.time() - start_time

        assert result == "success"
        # Should complete quickly with no delay
        assert elapsed_time < 0.1

    def test_retry_single_attempt(self):
        """Test retry decorator with max_attempts=1 (no retry)."""
        call_count = {"count": 0}

        @retry(max_attempts=1, delay=0.01)
        def no_retry_function():
            call_count["count"] += 1
            raise ValueError("Error")

        with pytest.raises(ValueError):
            no_retry_function()

        assert call_count["count"] == 1


class TestDecoratorCombinations:
    """Test combining decorators."""

    def test_timer_and_retry_together(self, capsys):
        """Test using timer and retry decorators together."""
        call_count = {"count": 0}

        @timer
        @retry(max_attempts=2, delay=0.01)
        def combined_function():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("First attempt")
            return "success"

        result = combined_function()
        assert result == "success"

        captured = capsys.readouterr()
        assert "combined_function executed in" in captured.out

    def test_retry_and_timer_order(self, capsys):
        """Test decorator order matters."""
        call_count = {"count": 0}

        @retry(max_attempts=2, delay=0.01)
        @timer
        def reverse_order():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise ValueError("First attempt")
            return "success"

        result = reverse_order()
        assert result == "success"

        # Timer should measure each attempt separately
        captured = capsys.readouterr()
        # Output may differ based on decorator order


class TestDecoratorEdgeCases:
    """Test edge cases for decorators."""

    def test_timer_with_recursive_function(self, capsys):
        """Test timer decorator with recursive function."""
        @timer
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        result = fibonacci(5)
        assert result == 5

        captured = capsys.readouterr()
        # Should time each recursive call
        assert "fibonacci executed in" in captured.out

    def test_retry_preserves_original_exception(self):
        """Test retry decorator preserves the last exception."""
        @retry(max_attempts=2, delay=0.01)
        def custom_exception_function():
            raise CustomError("Custom error message")

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError, match="Custom error message"):
            custom_exception_function()


# TODO: Add tests for:
# - Performance impact of decorators
# - Thread safety of decorators
# - Decorator with async functions (if applicable)
# - Memory usage with many retries
# - Interaction with mocking/patching

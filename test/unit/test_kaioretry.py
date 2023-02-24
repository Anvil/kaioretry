"""KaioRetry main functions unit tests"""

import random
import logging

import pytest

import kaioretry


@pytest.mark.parametrize("func", (kaioretry.retry, kaioretry.aioretry))
def test_docstings(func):
    """Test that main functions have correct docstrings"""
    assert kaioretry.RETRY_PARAMS_DOCSTRING in func.__doc__


def randint():
    """Return a random integer"""
    return random.randint(1, 10000)


@pytest.mark.parametrize("attribute", ("retry", "aioretry"))
def test_retry(exception, mocker, attribute):
    """Test kaioretry.retry/aioretry delegation-to-Retry process"""
    retry_cls = mocker.patch("kaioretry.Retry", spec=kaioretry.Retry)
    context_cls = mocker.patch("kaioretry.Context")
    logger = mocker.MagicMock(spec=logging.Logger)

    context_params = ("tries", "delay", "max_delay", "min_delay", "logger")
    non_context_params = ("backoff", "jitter")
    params = {param: randint()
              for param in context_params + non_context_params}
    params["logger"] = logger

    func = getattr(kaioretry, attribute)
    result = func(exception, **params)

    context_cls.assert_called_once()
    for param in context_params:
        assert param in context_cls.call_args[1]
        assert params[param] == context_cls.call_args[1][param]
    assert "update_delay" in context_cls.call_args[1]
    assert callable(context_cls.call_args[1]["update_delay"])

    retry_cls.assert_called_once_with(
        exceptions=exception, context=context_cls.return_value, logger=logger)
    assert result == getattr(retry_cls.return_value, attribute)

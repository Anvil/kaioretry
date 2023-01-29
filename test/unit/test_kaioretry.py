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
    params = {param: randint()
              for param in ("tries", "delay", "backoff", "jitter",
                            "max_delay", "min_delay")}
    params["logger"] = logger

    func = getattr(kaioretry, attribute)
    result = func(exception, **params)

    context_cls.assert_called_once_with(**params)
    retry_cls.assert_called_once_with(
        exceptions=exception, context=context_cls.return_value, logger=logger)
    assert result == getattr(retry_cls.return_value, attribute)

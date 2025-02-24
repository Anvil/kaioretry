"""KaioRetry main functions unit tests"""

import random
import logging
from contextlib import nullcontext as does_not_raise

import pytest

import kaioretry
from kaioretry.types import FuncRetVal


@pytest.mark.parametrize("func", (kaioretry.retry, kaioretry.aioretry))
def test_docstings(func):
    """Test that main functions have correct docstrings"""
    assert kaioretry.RETRY_PARAMS_DOCSTRING in func.__doc__


def randint():
    """Return a random integer"""
    return random.randint(1, 10000)


for_each_module_attribute = pytest.mark.parametrize(
    "attribute", ("retry", "aioretry")
)


@for_each_module_attribute
def test_retry(exception, mocker, attribute):
    """Test kaioretry.retry/aioretry delegation-to-Retry process"""
    retry_cls = mocker.patch("kaioretry.Retry", spec=kaioretry.Retry)
    context_cls = mocker.patch("kaioretry.Context")
    logger = mocker.MagicMock(spec=logging.Logger)

    context_params = ("tries", "delay", "max_delay", "min_delay", "logger")
    non_context_params = ("backoff", "jitter")
    params = {
        param: randint() for param in context_params + non_context_params
    }
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
        exceptions=exception, context=context_cls.return_value, logger=logger
    )
    assert result == getattr(retry_cls.return_value, attribute)


@for_each_module_attribute
@pytest.mark.parametrize(
    "jitter, expectation",
    (
        (1, does_not_raise()),
        ((1, 2), does_not_raise()),
        ("abc", pytest.raises(TypeError)),
    ),
)
def test_retry_jitter_values(exception, attribute, jitter, expectation):
    """Test validation of jitter values"""
    func = getattr(kaioretry, attribute)
    with expectation:
        func(exception, jitter=jitter)


@for_each_module_attribute
def test_metadata(attribute):
    """Test that retry and aioretry have the correct metadata. They are
    decorated by kaioretry._make_decorator and we want to be sure that
    documentation will be correctly generated.
    """
    func = getattr(kaioretry, attribute)
    assert func.__name__ == attribute
    assert func.__qualname__ == attribute
    assert "retry_obj" not in func.__annotations__
    assert func.__annotations__["return"] != FuncRetVal

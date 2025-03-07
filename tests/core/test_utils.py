from unittest.mock import Mock

import pytest

import regress_stack.core.utils


@pytest.fixture
def mock_cpu_count(monkeypatch):
    cpu_count = Mock(return_value=42 * 3)

    monkeypatch.setattr("regress_stack.core.utils.multiprocessing.cpu_count", cpu_count)
    yield cpu_count


def test_concurrency_cb(mock_cpu_count):
    assert type(regress_stack.core.utils.concurrency_cb("auto")) is int
    assert regress_stack.core.utils.concurrency_cb("auto") == 42
    assert type(regress_stack.core.utils.concurrency_cb("51")) is int
    assert regress_stack.core.utils.concurrency_cb("51") == 51
    with pytest.raises(ValueError):
        regress_stack.core.utils.concurrency_cb("NotInt")

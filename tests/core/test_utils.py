import unittest.mock as mock

import pytest

import regress_stack.core.utils


@pytest.fixture
def mock_cpu_count(monkeypatch):
    cpu_count = mock.Mock(return_value=42 * 3)

    monkeypatch.setattr("regress_stack.core.utils.multiprocessing.cpu_count", cpu_count)
    yield cpu_count


@pytest.fixture
def mock_os(monkeypatch):
    os = mock.Mock()

    os.environ = {}

    monkeypatch.setattr("regress_stack.core.utils.os", os)
    yield os


def test_concurrency_cb(mock_cpu_count):
    assert type(regress_stack.core.utils.concurrency_cb("auto")) is int
    assert regress_stack.core.utils.concurrency_cb("auto") == 42
    assert type(regress_stack.core.utils.concurrency_cb("51")) is int
    assert regress_stack.core.utils.concurrency_cb("51") == 51
    with pytest.raises(ValueError):
        regress_stack.core.utils.concurrency_cb("NotInt")


def test_system(mock_os):
    mock_os.waitstatus_to_exitcode.return_value = 42
    assert regress_stack.core.utils.system("abc") == 42
    mock_os.system.assert_called_once_with("abc")
    mock_os.chdir.assert_not_called()
    assert mock_os.environ == {}
    mock_os.reset()
    regress_stack.core.utils.system("abc", {"a": "A"})
    mock_os.system.assert_called_with("abc")
    mock_os.chdir.assert_not_called()
    assert "a" in mock_os.environ
    mock_os.reset()
    regress_stack.core.utils.system("abc", {"b": "B"}, "/non-existent")
    mock_os.system.assert_called_with("abc")
    assert "b" in mock_os.environ
    mock_os.chdir.assert_has_calls(
        [
            mock.call("/non-existent"),
            mock.call(mock_os.getcwd()),
        ]
    )
    mock_os.reset()

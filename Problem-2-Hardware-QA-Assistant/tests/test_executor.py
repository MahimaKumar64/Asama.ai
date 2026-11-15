
import subprocess
from unittest.mock import patch
from backend.executor import execute_command


def test_lscpu_execution():
    result = execute_command("lscpu")

    assert result["success"] is True
    assert "Architecture" in result["stdout"]


def test_disallowed_command():
    result = execute_command("rm")

    assert result["success"] is False
    assert "not allowed" in result["error"]


def test_invalid_timeout():
    result = execute_command("lscpu", timeout=100)

    assert result["success"] is False


def test_invalid_timeout_type():
    result = execute_command("lscpu", timeout=True)

    assert result["success"] is False


def test_malicious_command_is_rejected():

    result = execute_command("rm -rf /")

    assert result["success"] is False
    assert "not allowed" in result["error"]


@patch(
    "backend.executor.subprocess.run",
    side_effect=subprocess.TimeoutExpired(
        cmd=["/usr/bin/lscpu"],
        timeout=1
    )
)
def test_command_timeout_is_handled(mock_run):

    result = execute_command("lscpu", timeout=1)

    assert result["success"] is False
    assert result["error"] == "Command execution timed out."


@patch(
    "backend.executor.subprocess.run",
    side_effect=FileNotFoundError
)
def test_missing_utility_is_handled(mock_run):

    result = execute_command("lscpu")

    assert result["success"] is False
    assert result["error"] == "Required hardware utility is unavailable."


@patch("backend.executor.subprocess.run")
def test_shell_execution_is_disabled(mock_run):

    mock_run.return_value = subprocess.CompletedProcess(
        args=["/usr/bin/lscpu"],
        returncode=0,
        stdout="CPU information",
        stderr=""
    )

    result = execute_command("lscpu")

    assert result["success"] is True

    mock_run.assert_called_once()

    call_arguments = mock_run.call_args

    assert call_arguments.kwargs["shell"] is False
    assert call_arguments.args[0] == ["/usr/bin/lscpu"]


@patch(
    "backend.executor.subprocess.run",
    side_effect=PermissionError("Permission denied")
)
def test_permission_error_is_handled(mock_run):

    result = execute_command("lscpu")

    assert result["success"] is False
    assert "System execution error" in result["error"]

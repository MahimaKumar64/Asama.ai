
import subprocess
from typing import Any


# Only these predefined commands can be executed.
COMMAND_ALLOWLIST = {
    "lscpu": ["/usr/bin/lscpu"],
    "free": ["/usr/bin/free", "-b"],
    "lsblk": [
        "/usr/bin/lsblk",
        "-J",
        "-o",
        "NAME,SIZE,TYPE,MOUNTPOINTS,MODEL,ROTA,TRAN"
    ],
    "lspci": ["/usr/bin/lspci"],
    "dmidecode": ["/usr/sbin/dmidecode", "-t", "memory"],
    "nvidia-smi": ["/usr/lib/wsl/lib/nvidia-smi"],
}


def execute_command(
    command_name: str,
    timeout: int = 10
) -> dict[str, Any]:
    """
    Execute a predefined hardware inspection command.

    Arbitrary commands and shell input are not accepted.
    """

    if command_name not in COMMAND_ALLOWLIST:
        return {
            "success": False,
            "error": f"Command '{command_name}' is not allowed.",
            "stdout": "",
            "stderr": "",
        }

    if not isinstance(timeout, int) or isinstance(timeout, bool):
        return {
            "success": False,
            "error": "Invalid timeout value.",
            "stdout": "",
            "stderr": "",
        }

    if timeout < 1 or timeout > 30:
        return {
            "success": False,
            "error": "Timeout must be between 1 and 30 seconds.",
            "stdout": "",
            "stderr": "",
        }

    command = COMMAND_ALLOWLIST[command_name]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "error": None if result.returncode == 0
            else "Command execution failed.",
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command execution timed out.",
            "stdout": "",
            "stderr": "",
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "Required hardware utility is unavailable.",
            "stdout": "",
            "stderr": "",
        }

    except OSError as exc:
        return {
            "success": False,
            "error": f"System execution error: {exc}",
            "stdout": "",
            "stderr": "",
        }

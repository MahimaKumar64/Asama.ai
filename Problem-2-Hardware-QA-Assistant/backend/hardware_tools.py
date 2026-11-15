
from backend.executor import execute_command
from backend.parsers import (
    parse_lscpu,
    parse_memory,
    parse_storage,
    parse_gpu,
    parse_memory_topology,
)
from backend.system_discovery import get_system_capabilities


def run_hardware_command(command, parser=None):
    """Execute a hardware command and optionally parse its output."""

    result = execute_command(command)

    if not result["success"]:
        return {
            "available": False,
            "error": result["error"],
            "details": result.get("stderr", ""),
        }

    if parser:
        return {
            "available": True,
            "data": parser(result["stdout"]),
        }

    return {
        "available": True,
        "data": result["stdout"],
    }


def get_cpu_info():
    return run_hardware_command("lscpu", parse_lscpu)


def get_memory_summary():
    return run_hardware_command("free", parse_memory)


def get_memory_topology():
    return run_hardware_command(
        "dmidecode",
        parse_memory_topology
    )


def get_storage_info():
    return run_hardware_command("lsblk", parse_storage)


def get_gpu_info():
    return run_hardware_command("lspci", parse_gpu)


def get_system_info():
    return get_system_capabilities()


# Central collection of available hardware functions.
HARDWARE_TOOLS = {
    "get_cpu_info": get_cpu_info,
    "get_memory_summary": get_memory_summary,
    "get_memory_topology": get_memory_topology,
    "get_storage_info": get_storage_info,
    "get_gpu_info": get_gpu_info,
    "get_system_info": get_system_info,
}

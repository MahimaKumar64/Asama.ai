
from backend.hardware_tools import HARDWARE_TOOLS


# Descriptions and schemas exposed to the LLM.
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_cpu_info",
            "description": (
                "Retrieve CPU information including processor model, "
                "architecture, cores, threads and virtualization."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_summary",
            "description": (
                "Retrieve RAM usage, total memory, used memory, "
                "free memory and available memory."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_topology",
            "description": (
                "Retrieve physical RAM module information, memory slots, "
                "maximum capacity and installed memory devices. "
                "Some environments may not expose this information."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_storage_info",
            "description": (
                "Retrieve storage device information including disk names, "
                "sizes, models, types and mount points."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_gpu_info",
            "description": (
                "Retrieve GPU and display controller information "
                "using PCI device information."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": (
                "Retrieve operating system, Linux distribution, "
                "architecture, WSL status and available hardware utilities."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    }
]


def get_tool_definitions():
    """Return the tool schemas exposed to the LLM."""
    return TOOL_DEFINITIONS


def execute_registered_tool(name, arguments=None):
    """
    Execute only a registered hardware function.

    The LLM cannot provide shell commands or arbitrary arguments.
    """

    if name not in HARDWARE_TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {name}"
        }

    if arguments is None:
        arguments = {}

    if not isinstance(arguments, dict):
        return {
            "success": False,
            "error": "Tool arguments must be an object."
        }

    # Current hardware tools do not accept arguments.
    if arguments:
        return {
            "success": False,
            "error": "This tool does not accept arguments."
        }

    try:
        result = HARDWARE_TOOLS[name]()

        return {
            "success": True,
            "tool": name,
            "result": result
        }

    except Exception:
        return {
            "success": False,
            "tool": name,
            "error": "Hardware tool execution failed."
        }

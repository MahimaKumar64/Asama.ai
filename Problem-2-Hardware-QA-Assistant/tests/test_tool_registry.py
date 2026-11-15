
from backend.tool_registry import (
    get_tool_definitions,
    execute_registered_tool,
)


def test_tool_definitions():
    tools = get_tool_definitions()

    assert len(tools) == 6

    names = [
        tool["function"]["name"]
        for tool in tools
    ]

    assert "get_cpu_info" in names
    assert "get_memory_summary" in names
    assert "get_storage_info" in names


def test_registered_cpu_tool():
    result = execute_registered_tool("get_cpu_info")

    assert result["success"] is True
    assert result["tool"] == "get_cpu_info"


def test_unknown_tool():
    result = execute_registered_tool("delete_files")

    assert result["success"] is False


def test_arbitrary_arguments_rejected():
    result = execute_registered_tool(
        "get_cpu_info",
        {"command": "rm -rf"}
    )

    assert result["success"] is False

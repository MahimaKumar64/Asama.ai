
from backend.hardware_tools import (
    get_cpu_info,
    get_memory_summary,
    get_memory_topology,
    get_storage_info,
    get_gpu_info,
    get_system_info,
)


def test_cpu_tool():
    result = get_cpu_info()

    assert result["available"] is True
    assert result["data"]["model"] is not None


def test_memory_tool():
    result = get_memory_summary()

    assert result["available"] is True
    assert result["data"]["total_bytes"] > 0


def test_storage_tool():
    result = get_storage_info()

    assert result["available"] is True
    assert "devices" in result["data"]


def test_gpu_tool():
    result = get_gpu_info()

    assert result["available"] is True
    assert "devices" in result["data"]


def test_memory_topology_tool():
    result = get_memory_topology()

    if result["available"]:
        assert "available" in result["data"]
    else:
        assert result["error"] is not None


def test_system_info():
    result = get_system_info()

    assert result["environment"]["is_wsl"] is True
    assert "lscpu" in result["utilities"]["available"]

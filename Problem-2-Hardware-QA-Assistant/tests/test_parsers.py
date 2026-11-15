
from backend.parsers import (
    parse_lscpu,
    parse_memory,
    parse_storage,
    parse_gpu,
    parse_memory_topology,
)


def test_cpu_parser():
    output = """
Architecture: x86_64
CPU(s): 12
Model name: AMD Ryzen 5 5600H
"""

    result = parse_lscpu(output)

    assert result["architecture"] == "x86_64"
    assert result["logical_cpus"] == 12
    assert result["model"] == "AMD Ryzen 5 5600H"


def test_memory_parser():
    output = """
Mem: 8000000000 2000000000 3000000000 1000000 3000000000 5000000000
"""

    result = parse_memory(output)

    assert result["total_bytes"] == 8000000000
    assert result["available_bytes"] == 5000000000


def test_storage_parser():
    output = """
{
    "blockdevices": [
        {
            "name": "sda",
            "size": "100G",
            "type": "disk",
            "model": "Virtual Disk",
            "tran": "virtio",
            "rota": false,
            "mountpoints": []
        }
    ]
}
"""

    result = parse_storage(output)

    assert len(result["devices"]) == 1
    assert result["devices"][0]["name"] == "sda"


def test_gpu_parser():
    output = """
01:00.0 3D controller: Microsoft Corporation Basic Render Driver
"""

    result = parse_gpu(output)

    assert len(result["devices"]) == 1
    assert result["devices"][0]["is_virtual"] is True


def test_memory_topology_unavailable():
    output = "No SMBIOS nor DMI entry point found"

    result = parse_memory_topology(output)

    assert result["available"] is False
    assert result["maximum_capacity"] is None

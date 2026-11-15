
import json
import re


def parse_lscpu(output):
    """Convert lscpu key-value output into structured CPU data."""

    raw = {}

    for line in output.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        raw[key.strip().lower()] = value.strip()

    return {
        "model": raw.get("model name"),
        "architecture": raw.get("architecture"),
        "vendor": raw.get("vendor id"),
        "logical_cpus": _to_int(raw.get("cpu(s)")),
        "cores_per_socket": _to_int(raw.get("core(s) per socket")),
        "threads_per_core": _to_int(raw.get("thread(s) per core")),
        "sockets": _to_int(raw.get("socket(s)")),
        "virtualization": raw.get("virtualization"),
        "hypervisor_vendor": raw.get("hypervisor vendor"),
    }


def parse_memory(output):
    """Parse free -b output."""

    lines = output.splitlines()

    for line in lines:
        parts = line.split()

        if parts and parts[0] == "Mem:" and len(parts) >= 7:
            return {
                "total_bytes": _to_int(parts[1]),
                "used_bytes": _to_int(parts[2]),
                "free_bytes": _to_int(parts[3]),
                "shared_bytes": _to_int(parts[4]),
                "buff_cache_bytes": _to_int(parts[5]),
                "available_bytes": _to_int(parts[6]),
                "source": "Linux free command",
            }

    return {"error": "Memory information could not be parsed."}


def parse_storage(output):
    """Parse lsblk JSON output."""

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return {"error": "Invalid storage JSON output."}

    devices = []

    for device in data.get("blockdevices", []):
        if device.get("type") != "disk":
            continue

        devices.append({
            "name": device.get("name"),
            "size": device.get("size"),
            "model": device.get("model"),
            "transport": device.get("tran"),
            "rotational": device.get("rota"),
            "mountpoints": device.get("mountpoints") or [],
        })

    return {"devices": devices}


def parse_gpu(output):
    """Identify GPU-related PCI devices from lspci output."""

    devices = []

    for line in output.splitlines():
        lower_line = line.lower()

        if any(term in lower_line for term in [
            "vga compatible controller",
            "3d controller",
            "display controller",
        ]):
            devices.append({
                "description": line.strip(),
                "is_virtual": any(term in lower_line for term in [
                    "microsoft corporation",
                    "virtualbox",
                    "vmware",
                    "qemu",
                ]),
            })

    return {"devices": devices}


def parse_memory_topology(output):
    """
    Parse dmidecode memory information.

    Physical memory details may be unavailable in WSL.
    Never infer physical slot compatibility from missing data.
    """

    result = {
        "maximum_capacity": None,
        "installed_modules": [],
        "empty_slots": 0,
        "total_slots": 0,
        "available": False,
    }

    if not output or "No SMBIOS nor DMI entry point" in output:
        result["error"] = "SMBIOS/DMI information unavailable."
        return result

    capacity_match = re.search(
        r"Maximum Capacity:\s*(.+)",
        output,
        re.IGNORECASE
    )

    if capacity_match:
        result["maximum_capacity"] = capacity_match.group(1).strip()

    blocks = re.split(r"\n\s*Memory Device\s*\n", output)

    for block in blocks[1:]:
        size_match = re.search(r"Size:\s*(.+)", block)

        if not size_match:
            continue

        size = size_match.group(1).strip()

        result["total_slots"] += 1

        if size.lower() == "no module installed":
            result["empty_slots"] += 1
            continue

        if size.lower() == "unknown":
            continue

        module = {}

        for field in [
            "Size",
            "Type",
            "Speed",
            "Manufacturer",
            "Part Number",
            "Locator",
        ]:
            match = re.search(
                rf"{field}:\s*(.+)",
                block,
                re.IGNORECASE
            )

            if match:
                module[field.lower().replace(" ", "_")] = (
                    match.group(1).strip()
                )

        result["installed_modules"].append(module)

    result["available"] = True
    return result


def _to_int(value):
    """Safely convert values into integers."""

    if value is None:
        return None

    try:
        return int(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None

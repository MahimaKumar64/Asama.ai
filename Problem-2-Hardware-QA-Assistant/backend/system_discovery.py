
import platform
import shutil
import os


# Utilities our application knows how to use.
HARDWARE_UTILITIES = [
    "lscpu",
    "lsblk",
    "free",
    "lspci",
    "dmidecode",
    "nvidia-smi",
]


def discover_utilities():
    """
    Detect which hardware inspection utilities
    are installed and available on this system.
    """
    available = {}
    unavailable = []

    for utility in HARDWARE_UTILITIES:
        path = shutil.which(utility)

        if path:
            available[utility] = path
        else:
            unavailable.append(utility)

    return {
        "available": available,
        "unavailable": unavailable,
    }


def detect_environment():
    """
    Identify the operating system and whether
    the application is running inside WSL.
    """
    release = platform.release().lower()

    is_wsl = (
        "microsoft" in release
        or "WSL_DISTRO_NAME" in os.environ
    )

    try:
        distribution = platform.freedesktop_os_release()
        distro_name = distribution.get("PRETTY_NAME", "Unknown")
    except OSError:
        distro_name = "Unknown"

    return {
        "operating_system": platform.system(),
        "distribution": distro_name,
        "architecture": platform.machine(),
        "is_wsl": is_wsl,
        "python_version": platform.python_version(),
    }


def get_system_capabilities():
    """
    Combine environment information and
    available hardware utilities.
    """
    return {
        "environment": detect_environment(),
        "utilities": discover_utilities(),
    }

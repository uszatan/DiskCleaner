import os
import platform
import subprocess

# OS-specific imports
if platform.system() == "Windows":
    import ctypes

def get_volume_identifier(path: str) -> str:
    """
    Retrieves a unique identifier for the volume (disk) where the given path is located.

    This helps in recognizing a drive (especially external ones) even if its mount point
    or drive letter changes between sessions.

    Args:
        path (str): A path to a file or directory on the volume.

    Returns:
        str: A unique identifier for the volume (e.g., serial number, UUID) or an error/fallback string.
    """
    # The path to be scanned must exist.
    if not os.path.exists(path):
        raise FileNotFoundError(f"The path to scan does not exist: '{path}'")

    # os.path.realpath resolves symbolic links and returns the absolute path.
    abs_path = os.path.realpath(path)

    os_type = platform.system()

    if os_type == "Windows":
        # For Windows, we use the volume serial number.
        drive = os.path.splitdrive(abs_path)[0] + '\\'
        try:
            serial_number = ctypes.c_ulong()
            if ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(drive),
                None, 0,  # No volume name buffer
                ctypes.byref(serial_number),
                ctypes.c_ulong(), ctypes.c_ulong(),  # No max component length or flags
                None, 0  # No file system name buffer
            ):
                return hex(serial_number.value)
            else:
                return f"unknown_windows_volume_{ctypes.GetLastError()}"
        except Exception as e:
            return f"unknown_windows_volume_exception_{e}"

    elif os_type == "Linux":
        try:
            # For Linux, find the device for the path and get its UUID.
            device_path = subprocess.check_output(
                ['findmnt', '-n', '-o', 'SOURCE', '--target', abs_path],
                text=True, stderr=subprocess.PIPE
            ).strip()
            uuid = subprocess.check_output(
                ['lsblk', '-no', 'UUID', device_path],
                text=True, stderr=subprocess.PIPE
            ).strip()
            # Return UUID, or the device path if UUID is not available.
            return uuid if uuid else f"no_uuid_for_{device_path}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback if the above commands fail.
            return "unknown_linux_volume"

    elif os_type == "Darwin":  # macOS
        try:
            # For macOS, use 'diskutil' to find the Volume UUID.
            info = subprocess.check_output(
                ['diskutil', 'info', abs_path],
                text=True, stderr=subprocess.PIPE
            )
            for line in info.splitlines():
                if "Volume UUID" in line:
                    return line.split(":")[-1].strip()
            return "unknown_macos_volume_no_uuid"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown_macos_volume"

    return "unknown_os"
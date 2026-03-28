import platform
from unittest.mock import patch, MagicMock

import pytest

from src.system_info import get_volume_identifier


@patch('os.path.exists', return_value=True)
@patch('os.path.realpath', return_value='/test/path')
def test_get_volume_identifier_linux(mock_realpath, mock_exists, mocker):
    """Test get_volume_identifier on a mocked Linux system."""
    mocker.patch('platform.system', return_value='Linux')
    mock_check_output = mocker.patch('subprocess.check_output')
    # Simulate `findmnt` and `lsblk` calls
    mock_check_output.side_effect = [
        '/dev/sda1',  # Output of findmnt
        'a1b2c3d4-e5f6-7890-1234-567890abcdef'  # Output of lsblk
    ]
    
    identifier = get_volume_identifier('/test/path')
    assert identifier == 'a1b2c3d4-e5f6-7890-1234-567890abcdef'
    assert mock_check_output.call_count == 2


@patch('os.path.exists', return_value=True)
@patch('os.path.realpath', return_value='C:\\test\\path')
def test_get_volume_identifier_windows(mock_realpath, mock_exists, mocker):
    """Test get_volume_identifier on a mocked Windows system."""
    mocker.patch('platform.system', return_value='Windows')
    
    # Mock ctypes
    mock_ctypes = MagicMock()
    mock_ctypes.windll.kernel32.GetVolumeInformationW.return_value = True
    # Create a mock for the byref parameter
    serial_number_mock = MagicMock()
    serial_number_mock.value = 0x1234ABCD
    mock_ctypes.c_ulong.return_value = serial_number_mock

    mocker.patch.dict('sys.modules', {'ctypes': mock_ctypes})

    identifier = get_volume_identifier('C:\\test\\path')
    assert identifier == hex(0x1234ABCD)


@patch('os.path.exists', return_value=True)
@patch('os.path.realpath', return_value='/Users/test/path')
def test_get_volume_identifier_darwin(mock_realpath, mock_exists, mocker):
    """Test get_volume_identifier on a mocked macOS system."""
    mocker.patch('platform.system', return_value='Darwin')
    mock_check_output = mocker.patch('subprocess.check_output')
    mock_check_output.return_value = """
    Volume UUID:              F1E2D3C4-B5A6-9876-5432-10FEDCBA9876
    """
    
    identifier = get_volume_identifier('/Users/test/path')
    assert identifier == 'F1E2D3C4-B5A6-9876-5432-10FEDCBA9876'
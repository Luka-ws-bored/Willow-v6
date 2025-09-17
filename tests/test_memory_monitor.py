import unittest
from unittest.mock import patch, MagicMock
from src.utils.memory_monitor import MemoryMonitor

class TestMemoryMonitor(unittest.TestCase):
    @patch('psutil.virtual_memory')
    def test_get_memory_usage(self, mock_vm):
        mock_vm.return_value = MagicMock(percent=42.0)
        monitor = MemoryMonitor()
        usage = monitor.get_memory_usage()
        self.assertEqual(usage, 42.0)

if __name__ == '__main__':
    unittest.main()
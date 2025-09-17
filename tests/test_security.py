"""
Security validation tests for Willow v6.
Tests input validation, path validation, and security measures.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import validate_model_name, validate_prompt
from src.utils.file_ops import SecureFileOps, SecurityError
from pathlib import Path


class TestSecurityValidation(unittest.TestCase):
    """Test security validation functions."""
    
    def test_valid_model_names(self):
        """Test validation of valid model names."""
        valid_models = [
            'goekdenizguelmez/josiefied-qwen3:1.7b',
            'qwen3:0.6b',
            'nomic-embed-text:latest'
        ]
        
        for model in valid_models:
            with self.subTest(model=model):
                self.assertTrue(validate_model_name(model))
    
    def test_invalid_model_names(self):
        """Test validation rejects invalid model names."""
        invalid_models = [
            '',
            None,
            123,
            '../../../etc/passwd',
            'rm -rf /',
            'model; rm -rf /',
            'model && echo "hacked"',
            'model`whoami`',
            'model$(whoami)',
            'invalid-model-not-in-list'
        ]
        
        for model in invalid_models:
            with self.subTest(model=model):
                self.assertFalse(validate_model_name(model))
    
    def test_valid_prompts(self):
        """Test validation of valid prompts."""
        valid_prompts = [
            "Hello world",
            "Write a simple Python function",
            "A" * 1000,  # Long but under limit
            "Special chars: !@#$%^&*()",
            "Newlines\nare\nok"
        ]
        
        for prompt in valid_prompts:
            with self.subTest(prompt=prompt[:50] + "..."):
                self.assertTrue(validate_prompt(prompt))
    
    def test_invalid_prompts(self):
        """Test validation rejects invalid prompts."""
        invalid_prompts = [
            '',
            None,
            123,
            '   ',  # Only whitespace
            'A' * 100000,  # Too long
        ]
        
        for prompt in invalid_prompts:
            with self.subTest(prompt=str(prompt)[:50] + "..."):
                self.assertFalse(validate_prompt(prompt))


class TestSecureFileOps(unittest.TestCase):
    """Test secure file operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_root = Path(__file__).parent / 'temp_test_root'
        self.temp_root.mkdir(exist_ok=True)
        self.file_ops = SecureFileOps(self.temp_root)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root)
    
    def test_valid_path_validation(self):
        """Test validation of valid paths."""
        valid_paths = [
            'test.txt',
            'subdir/test.txt',
            './test.txt',
            'data/configs/test.json'
        ]
        
        for path in valid_paths:
            with self.subTest(path=path):
                validated = self.file_ops.validate_path(path)
                self.assertIsInstance(validated, Path)
    
    def test_invalid_path_validation(self):
        """Test validation rejects invalid paths."""
        invalid_paths = [
            '../../../etc/passwd',
            '/etc/passwd',
            '~/../../etc/passwd',
            '../outside_project.txt'
        ]
        
        for path in invalid_paths:
            with self.subTest(path=path):
                with self.assertRaises(SecurityError):
                    self.file_ops.validate_path(path)
    
    def test_safe_file_operations(self):
        """Test safe file read/write operations."""
        test_file = 'test_safe_ops.txt'
        test_content = 'Hello, secure world!'
        
        # Test safe write
        self.file_ops.safe_write_text(test_file, test_content)
        
        # Test safe read
        read_content = self.file_ops.safe_read_text(test_file)
        self.assertEqual(read_content, test_content)
        
        # Test safe delete
        deleted = self.file_ops.safe_delete(test_file)
        self.assertTrue(deleted)
        
        # Test delete non-existent file
        deleted_again = self.file_ops.safe_delete(test_file)
        self.assertFalse(deleted_again)


class TestSubprocessSecurity(unittest.TestCase):
    """Test subprocess security measures."""
    
    @patch('subprocess.run')
    def test_subprocess_call_structure(self, mock_run):
        """Test that subprocess calls use safe list format."""
        from src.main import list_available_models
        
        # Mock successful subprocess
        mock_run.return_value = MagicMock(
            stdout="NAME\nqwen3:0.6b\n",
            stderr="",
            returncode=0
        )
        
        models = list_available_models()
        
        # Verify subprocess was called with list (not string)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertIsInstance(call_args, list)
        self.assertEqual(call_args[0], "ollama")
        self.assertEqual(call_args[1], "list")
    
    @patch('subprocess.run')
    def test_query_llm_subprocess_security(self, mock_run):
        """Test that query_llm uses safe subprocess calls."""
        from src.main import query_llm
        
        # Mock successful subprocess
        mock_run.return_value = MagicMock(
            stdout="Hello! I'm Willow.",
            stderr="",
            returncode=0
        )
        
        response = query_llm("Hello", model="qwen3:0.6b")
        
        # Verify subprocess was called safely
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertIsInstance(call_args, list)
        self.assertEqual(call_args[:3], ["ollama", "run", "qwen3:0.6b"])
        # Ensure no shell=True is used
        self.assertNotIn('shell', mock_run.call_args[1])


if __name__ == '__main__':
    unittest.main()
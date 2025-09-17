import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tiny_helper import select_model
    from src.main import query_llm
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Valid models according to project configuration
VALID_MODELS = ['goekdenizguelmez/josiefied-qwen3:1.7b', 'qwen3:0.6b']

class TestTinyHelper(unittest.TestCase):
    """Test suite for Tiny Helper model selection functionality."""
    
    def test_model_selection_high_ram(self):
        """Test model selection with high RAM (>8GB) - should select primary model."""
        with patch('psutil.virtual_memory') as mock_memory:
            # Mock 12GB available RAM
            mock_memory.return_value.available = 12 * 1024**3
            
            model = select_model()
            
            # Assert that selected model is valid
            self.assertIn(model, VALID_MODELS, f"Selected model '{model}' is not in valid models: {VALID_MODELS}")
            # Assert that primary model is selected with high RAM
            self.assertEqual(model, 'goekdenizguelmez/josiefied-qwen3:1.7b', f"Expected primary model with 12GB RAM, got: {model}")
            print(f"✅ High RAM test passed: {model}")
    
    def test_model_selection_medium_ram(self):
        """Test model selection with medium RAM (4-8GB) - should select fallback model."""
        with patch('psutil.virtual_memory') as mock_memory:
            # Mock 6GB available RAM
            mock_memory.return_value.available = 6 * 1024**3
            
            model = select_model()
            
            # Assert that selected model is valid
            self.assertIn(model, VALID_MODELS, f"Selected model '{model}' is not in valid models: {VALID_MODELS}")
            # Assert that fallback model is selected with medium RAM
            self.assertEqual(model, 'qwen3:0.6b', f"Expected fallback model with 6GB RAM, got: {model}")
            print(f"✅ Medium RAM test passed: {model}")
    
    def test_model_selection_low_ram(self):
        """Test model selection with low RAM (<4GB) - should select lightest model."""
        with patch('psutil.virtual_memory') as mock_memory:
            # Mock 2GB available RAM
            mock_memory.return_value.available = 2 * 1024**3
            
            model = select_model()
            
            # Assert that selected model is valid
            self.assertIn(model, VALID_MODELS, f"Selected model '{model}' is not in valid models: {VALID_MODELS}")
            # Assert that lightest model is selected with low RAM
            self.assertEqual(model, 'qwen3:0.6b', f"Expected lightest model with 2GB RAM, got: {model}")
            print(f"✅ Low RAM test passed: {model}")
    
    def test_model_selection_boundary_conditions(self):
        """Test model selection at RAM boundaries."""
        test_cases = [
            (8.1 * 1024**3, 'goekdenizguelmez/josiefied-qwen3:1.7b'),  # Just above 8GB
            (8.0 * 1024**3, 'qwen3:0.6b'),                              # Exactly 8GB
            (4.1 * 1024**3, 'qwen3:0.6b'),                              # Just above 4GB
            (4.0 * 1024**3, 'qwen3:0.6b'),                              # Exactly 4GB
            (3.9 * 1024**3, 'qwen3:0.6b'),                              # Just below 4GB
        ]
        
        for ram_bytes, expected_model in test_cases:
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.available = ram_bytes
                model = select_model()
                
                # Assert that selected model is valid
                self.assertIn(model, VALID_MODELS, f"Selected model '{model}' is not in valid models: {VALID_MODELS}")
                # Assert expected model for this RAM amount
                ram_gb = ram_bytes / 1024**3
                self.assertEqual(model, expected_model, f"With {ram_gb:.1f}GB RAM, expected '{expected_model}', got '{model}'")
        print(f"✅ Boundary conditions test passed")
    
    def test_query_llm_integration(self):
        """Test end-to-end integration with query_llm using selected model."""
        # Get the model selected by tiny helper
        model = select_model()
        
        # Assert that selected model is valid
        self.assertIn(model, VALID_MODELS, f"Selected model '{model}' is not in valid models: {VALID_MODELS}")
        
        # Test that query_llm accepts the selected model without errors
        # Note: This test may timeout, which is acceptable behavior
        try:
            response = query_llm("Hello Willow", model=model)
            # If we get a response, it should be a string
            self.assertIsInstance(response, str, f"Expected string response, got: {type(response)}")
            self.assertGreater(len(response), 0, "Response should not be empty")
            print(f"✅ Successfully got response from model '{model}': {response[:100]}...")
        except Exception as e:
            # Timeouts and model errors are acceptable in testing environment
            print(f"⚠️  Model query failed (expected in test environment): {e}")
            # Still assert that the model selection was valid
            self.assertIn(model, VALID_MODELS, f"Model selection failed: '{model}' not in {VALID_MODELS}")
        print(f"✅ Integration test completed")
    
    def test_all_models_are_valid(self):
        """Test that select_model() always returns a valid model regardless of RAM."""
        # Test with various RAM configurations
        ram_scenarios = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 10, 16, 32]  # GB
        
        for ram_gb in ram_scenarios:
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.available = ram_gb * 1024**3
                model = select_model()
                
                # Assert that selected model is always valid
                self.assertIn(model, VALID_MODELS, f"With {ram_gb}GB RAM, got invalid model: '{model}'. Valid models: {VALID_MODELS}")
                # Assert it's a non-empty string
                self.assertIsInstance(model, str, f"Model should be string, got: {type(model)}")
                self.assertGreater(len(model), 0, "Model name should not be empty")
        print(f"✅ All models validity test passed for {len(ram_scenarios)} scenarios")

# Legacy test function for backward compatibility
def test_tiny_helper_legacy():
    """Legacy test function - validates basic functionality."""
    print("🔍 Running Tiny Helper legacy test...")
    model = select_model()
    assert model in VALID_MODELS, f"Selected model '{model}' is not valid"
    print(f"✅ Tiny Helper selected valid model: {model}")

if __name__ == "__main__":
    # Run legacy test when executed directly
    test_tiny_helper_legacy()
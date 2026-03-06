"""
AIM v3 Test Suite
Comprehensive tests for AIM core components
"""

import pytest
import json
import tempfile
from pathlib import Path

# Import AIM components
from aim_core import AIMModel, AIMManifest, create_manifest, get_engine
from aim_core.engines import MarkovEngine, NgramEngine
from aim_hub import Registry, RegistryClient
from aim_core.plugins import BasePlugin, PluginManager


class TestAIMManifest:
    """Test manifest creation and validation"""
    
    def test_create_manifest(self):
        """Test creating a new manifest"""
        manifest = create_manifest(
            name="Test Model",
            author="Test Author",
            version="1.0.0",
            description="A test model",
            model_type="text",
            engine="markov"
        )
        
        assert manifest["name"] == "Test Model"
        assert manifest["author"] == "Test Author"
        assert manifest["engine"] == "markov"
    
    def test_manifest_validation(self):
        """Test manifest validation"""
        # Valid manifest
        data = {
            "name": "Test",
            "version": "1.0.0",
            "author": "Test",
            "description": "Test",
            "type": "text",
            "engine": "markov",
            "files": {}
        }
        manifest = AIMManifest(data)
        assert manifest["name"] == "Test"
        
        # Invalid manifest (missing field)
        invalid_data = {
            "name": "Test",
            "author": "Test"
            # Missing required fields
        }
        with pytest.raises(ValueError):
            AIMManifest(invalid_data)


class TestEngines:
    """Test different AI engines"""
    
    def test_markov_engine_training(self):
        """Test Markov engine training"""
        engine = get_engine("markov")
        
        text = "once upon a time there was a kingdom. the kingdom had a king. "
        text *= 10  # Repeat for more training data
        
        stats = engine.train(text, order=2)
        
        assert "vocabulary_size" in stats
        assert "transitions_count" in stats
        assert stats["order"] == 2
    
    def test_markov_engine_generation(self):
        """Test Markov engine text generation"""
        engine = get_engine("markov")
        
        text = "the cat sat on the mat. the cat was happy. "
        text *= 20
        
        engine.train(text)
        output = engine.generate(prompt="the cat", max_length=20)
        
        assert isinstance(output, str)
        assert len(output) > 0
        assert "cat" in output.lower()
    
    def test_markov_engine_save_load(self):
        """Test saving and loading Markov model"""
        engine = get_engine("markov")
        text = "hello world hello world " * 20
        engine.train(text)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            # Save
            engine.save(filepath)
            
            # Load
            new_engine = get_engine("markov")
            new_engine.load(filepath)
            
            # Verify
            assert new_engine.order == engine.order
            assert len(new_engine.transitions) > 0
        finally:
            Path(filepath).unlink()


class TestAIMModel:
    """Test AIM Model class"""
    
    def test_create_model(self):
        """Test creating a new AIM model"""
        model = AIMModel.create(
            name="Test Model",
            author="Tester",
            engine="markov"
        )
        
        assert model.manifest["name"] == "Test Model"
        assert model.manifest["author"] == "Tester"
    
    def test_train_and_generate(self):
        """Test training and generating with a model"""
        model = AIMModel.create(
            name="Story Generator",
            author="Test",
            engine="markov"
        )
        
        training_data = "once upon a time there was a kingdom. " * 30
        
        stats = model.train(training_data)
        assert "vocabulary_size" in stats
        
        output = model.generate(prompt="once upon", max_length=50)
        assert isinstance(output, str)
        assert len(output) > 0
    
    def test_save_and_load_model(self):
        """Test saving and loading .aim files"""
        # Create and train
        model = AIMModel.create(
            name="Test Model",
            author="Tester",
            engine="markov"
        )
        
        training_data = "hello world hello world " * 20
        model.train(training_data)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.aim"
            
            # Save
            saved_path = model.save(str(filepath))
            assert Path(saved_path).exists()
            
            # Load
            loaded_model = AIMModel.load(saved_path)
            
            # Verify
            assert loaded_model.manifest["name"] == "Test Model"
            assert loaded_model.manifest["author"] == "Tester"
            
            # Generate with loaded model
            output = loaded_model.generate(prompt="hello", max_length=20)
            assert isinstance(output, str)


class TestRegistry:
    """Test local registry"""
    
    def test_registry_register_and_list(self):
        """Test registering and listing models"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Registry(tmpdir)
            
            # Register a model
            registry.register("test_model", "/path/to/model.aim", {})
            
            # List models
            models = registry.list()
            assert "test_model" in models
            
            # Get model info
            info = registry.get("test_model")
            assert info["path"] == "/path/to/model.aim"


class TestPlugins:
    """Test plugin system"""
    
    def test_plugin_base_class(self):
        """Test creating a custom plugin"""
        class TestPlugin(BasePlugin):
            name = "test_plugin"
            version = "1.0.0"
            description = "Test plugin"
            
            def execute(self, input_data, **kwargs):
                return f"Processed: {input_data}"
        
        plugin = TestPlugin()
        result = plugin.execute("test")
        
        assert result == "Processed: test"
        assert plugin.name == "test_plugin"
    
    def test_plugin_manager(self):
        """Test plugin manager"""
        manager = PluginManager()
        
        # Register a plugin
        class CustomPlugin(BasePlugin):
            name = "custom"
            version = "1.0.0"
            
            def execute(self, data, **kwargs):
                return data.upper()
        
        manager.register_plugin("custom", CustomPlugin())
        
        # Get plugin
        plugin = manager.get_plugin("custom")
        assert plugin is not None
        
        # Execute plugin
        result = manager.execute_plugin("custom", "hello")
        assert result == "HELLO"
        
        # List plugins
        plugins = manager.list_plugins()
        assert "custom" in plugins


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow: train -> save -> load -> generate"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create and train
            model = AIMModel.create(
                name="Integration Test Model",
                author="Tester",
                engine="markov"
            )
            
            training_data = """
            The quick brown fox jumps over the lazy dog.
            The fox was very quick and brown.
            The dog was lazy but friendly.
            """ * 20
            
            model.train(training_data)
            
            # 2. Save
            model_path = Path(tmpdir) / "integration_test.aim"
            model.save(str(model_path))
            
            assert model_path.exists()
            
            # 3. Load
            loaded = AIMModel.load(str(model_path))
            
            # 4. Generate
            output = loaded.generate(prompt="The fox", max_length=30)
            
            assert isinstance(output, str)
            assert len(output) > 0
            print(f"\nGenerated: {output}")


def test_markov_example():
    """Simple example test"""
    engine = get_engine("markov")
    
    # Training data
    text = """
    Once upon a time there was a beautiful princess.
    The princess lived in a castle far far away.
    One day a prince came to the castle.
    The prince and princess fell in love.
    They lived happily ever after.
    """ * 10
    
    # Train
    engine.train(text, order=2)
    
    # Generate multiple variations
    for i in range(3):
        output = engine.generate(prompt="Once upon a", max_length=40)
        print(f"  Variation {i+1}: {output}")


# Run tests with: pytest test_aim.py -v

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

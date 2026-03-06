"""
AIM Model
Unified interface for working with .aim model packages
"""

import json
import zipfile
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .manifest import AIMManifest
from .engines import get_engine, BaseEngine


class AIMModel:
    """
    Represents a complete AIM model package.
    
    An AIM model is a packaged AI model with:
    - Manifest (metadata)
    - Model files (weights, config, etc.)
    - Optional supporting files
    """
    
    def __init__(self, manifest: AIMManifest, engine: BaseEngine = None):
        """
        Initialize AIM model.
        
        Args:
            manifest: AIMManifest instance
            engine: Engine instance (optional, will be created if None)
        """
        self.manifest = manifest
        
        if engine is None:
            engine_name = manifest["engine"]
            config = manifest.get("engine_config", {})
            engine = get_engine(engine_name, config)
        
        self.engine = engine
    
    @classmethod
    def create(
        cls,
        name: str,
        author: str,
        engine: str = "markov",
        **manifest_kwargs
    ) -> "AIMModel":
        """
        Create a new AIM model.
        
        Args:
            name: Model name
            author: Author name
            engine: Engine type
            **manifest_kwargs: Additional manifest fields
        
        Returns:
            New AIMModel instance
        """
        from .manifest import create_manifest
        manifest = create_manifest(name=name, author=author, engine=engine, **manifest_kwargs)
        engine_instance = get_engine(engine)
        return cls(manifest, engine_instance)
    
    @classmethod
    def load(cls, filepath: str) -> "AIMModel":
        """
        Load an AIM model from .aim file.
        
        Args:
            filepath: Path to .aim file
        
        Returns:
            Loaded AIMModel instance
        """
        if not filepath.endswith(".aim"):
            raise ValueError("Model file must have .aim extension")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract .aim (ZIP) file
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # Load manifest
            manifest_path = os.path.join(tmpdir, "aim.json")
            manifest = AIMManifest.from_file(manifest_path)
            
            # Create engine and load model
            engine_name = manifest["engine"]
            engine = get_engine(engine_name, manifest.get("engine_config"))
            
            # Load model files
            model_files = manifest.get("files", {})
            if "model" in model_files:
                model_path = os.path.join(tmpdir, model_files["model"])
                engine.load(model_path)
            
            return cls(manifest, engine)
    
    def train(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            data: Training data
            **kwargs: Engine-specific parameters
        
        Returns:
            Training statistics
        """
        stats = self.engine.train(data, **kwargs)
        return stats
    
    def generate(self, prompt: str = None, **kwargs) -> str:
        """
        Generate output.
        
        Args:
            prompt: Optional input prompt
            **kwargs: Generation parameters
        
        Returns:
            Generated output
        """
        return self.engine.generate(prompt, **kwargs)
    
    def save(self, filepath: str = None) -> str:
        """
        Save model as .aim file (ZIP package).
        
        Args:
            filepath: Path to save to. If None, uses model name.
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            filepath = f"{self.manifest['name'].lower().replace(' ', '_')}.aim"
        
        if not filepath.endswith(".aim"):
            filepath += ".aim"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save manifest
            manifest_path = os.path.join(tmpdir, "aim.json")
            with open(manifest_path, 'w') as f:
                f.write(self.manifest.to_json())
            
            # Save model files
            model_files = self.manifest.get("files", {})
            if "model" not in model_files:
                model_files["model"] = "model.json"
                self.manifest["files"] = model_files
            
            model_path = os.path.join(tmpdir, model_files["model"])
            self.engine.save(model_path)
            
            # Create ZIP package
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, tmpdir)
                        zipf.write(file_path, arcname)
        
        return filepath
    
    def info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "manifest": self.manifest.to_dict(),
            "engine": self.engine.__class__.__name__
        }
    
    def __repr__(self) -> str:
        return f"AIMModel({self.manifest['name']} v{self.manifest['version']} by {self.manifest['author']})"

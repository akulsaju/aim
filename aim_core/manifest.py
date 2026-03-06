"""
AIM Manifest System
Handles .aim file metadata and manifest creation
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class AIMManifest:
    """
    Represents the metadata for an AIM model.
    
    An AIM manifest defines:
    - Model identity (name, author, version)
    - Model configuration (engine, type)
    - Files included in the model
    - License and metadata
    """
    
    REQUIRED_FIELDS = ["name", "version", "author", "description", "type", "engine"]
    VALID_TYPES = ["text", "image", "audio", "embedding", "classification"]
    VALID_ENGINES = ["markov", "ngram", "embedding", "llm", "custom"]
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize manifest from a dictionary.
        
        Args:
            data: Dictionary with manifest fields
        """
        self.data = data
        self._validate()
    
    def _validate(self):
        """Validate manifest contains all required fields."""
        for field in self.REQUIRED_FIELDS:
            if field not in self.data:
                raise ValueError(f"Missing required field: {field}")
        
        if self.data["type"] not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {self.data['type']}")
        
        if self.data["engine"] not in self.VALID_ENGINES:
            raise ValueError(f"Invalid engine: {self.data['engine']}")
    
    @classmethod
    def from_json(cls, json_str: str) -> "AIMManifest":
        """Load manifest from JSON string."""
        data = json.loads(json_str)
        return cls(data)
    
    @classmethod
    def from_file(cls, filepath: str) -> "AIMManifest":
        """Load manifest from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export manifest as dictionary."""
        return self.data.copy()
    
    def to_json(self, indent: int = 2) -> str:
        """Export manifest as JSON string."""
        return json.dumps(self.data, indent=indent)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.data[key]
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-style setting."""
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default."""
        return self.data.get(key, default)


def create_manifest(
    name: str,
    author: str,
    version: str = "1.0.0",
    description: str = "",
    model_type: str = "text",
    engine: str = "markov",
    files: Optional[Dict[str, str]] = None,
    license_name: str = "MIT",
    tags: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AIMManifest:
    """
    Create a new AIM manifest.
    
    Args:
        name: Model name
        author: Author name
        version: Version number
        description: Model description
        model_type: Type of model (text, image, audio, etc.)
        engine: Engine type (markov, ngram, etc.)
        files: Dictionary of file paths {"model": "model.json", ...}
        license_name: License type
        tags: List of tags for discovery
        metadata: Additional metadata
    
    Returns:
        AIMManifest instance
    """
    if files is None:
        files = {}
    
    if tags is None:
        tags = []
    
    if metadata is None:
        metadata = {}
    
    manifest_data = {
        "name": name,
        "version": version,
        "author": author,
        "description": description,
        "type": model_type,
        "engine": engine,
        "files": files,
        "license": license_name,
        "tags": tags,
        "created": datetime.now().isoformat(),
        "metadata": metadata
    }
    
    return AIMManifest(manifest_data)

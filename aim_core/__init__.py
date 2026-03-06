"""
AIM Core - Universal AI Model Ecosystem
Core components for AIM v3 system
"""

from .manifest import AIMManifest, create_manifest
from .model import AIMModel
from .engines import get_engine, list_engines

__version__ = "3.0.0"
__all__ = ["AIMManifest", "AIMModel", "get_engine", "list_engines", "create_manifest"]

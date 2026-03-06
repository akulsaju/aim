"""
AIM Hub - Model Registry
Central registry for discovering, sharing, and installing models
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class Registry:
    """
    Local registry for managing downloaded models.
    
    Stores metadata and paths for installed models.
    """
    
    def __init__(self, registry_dir: str = None):
        """
        Initialize local registry.
        
        Args:
            registry_dir: Directory to store registry data. 
                         Defaults to ~/.aim/registry
        """
        if registry_dir is None:
            home = Path.home()
            registry_dir = home / '.aim' / 'registry'
        
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.registry_dir / 'index.json'
        self._load_index()
    
    def _load_index(self):
        """Load registry index from file."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
    
    def _save_index(self):
        """Save registry index to file."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def register(self, name: str, filepath: str, metadata: Dict[str, Any] = None):
        """
        Register a model in the local registry.
        
        Args:
            name: Model name
            filepath: Path to .aim file
            metadata: Optional metadata
        """
        self.index[name] = {
            'path': filepath,
            'registered': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self._save_index()
    
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get model info from registry."""
        return self.index.get(name)
    
    def list(self) -> List[str]:
        """List all registered models."""
        return list(self.index.keys())
    
    def unregister(self, name: str):
        """Remove model from registry."""
        if name in self.index:
            del self.index[name]
            self._save_index()


class RegistryClient:
    """
    Client for interacting with model registries.
    
    Note: Currently configured for local use only.
    Created by @akulsaju - https://github.com/akulsaju
    """
    
    def __init__(self, hub_url: str = "http://localhost:8000", token: str = None):
        """
        Initialize registry client.
        
        Args:
            hub_url: URL of model registry (default: local)
            token: API token for authenticated requests
        """
        self.hub_url = hub_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
    
    def search(self, query: str = "", tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for models in registry.
        
        Args:
            query: Search query string
            tags: List of tags to filter by
            limit: Maximum number of results
        
        Returns:
            List of model metadata dictionaries
        """
        try:
            params = {
                'q': query,
                'limit': limit
            }
            
            if tags:
                params['tags'] = ','.join(tags)
            
            url = f"{self.hub_url}/api/search"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                return []
        
        except requests.RequestException as e:
            print(f"Error searching registry: {e}")
            return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a model.
        
        Args:
            model_name: Name of the model
        
        Returns:
            Model metadata or None if not found
        """
        try:
            url = f"{self.hub_url}/api/models/{model_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except requests.RequestException:
            return None
    
    def download(self, model_name: str, output_dir: str = None) -> str:
        """
        Download a model from the registry.
        
        Args:
            model_name: Name of the model
            output_dir: Directory to save to (default: ~/.aim/models)
        
        Returns:
            Path to downloaded .aim file
        """
        if output_dir is None:
            home = Path.home()
            output_dir = home / '.aim' / 'models'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{model_name}.aim"
        
        try:
            url = f"{self.hub_url}/api/models/{model_name}/download"
            response = self.session.get(url, timeout=30, stream=True)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return str(output_path)
            else:
                raise Exception(f"Download failed: {response.status_code}")
        
        except requests.RequestException as e:
            raise Exception(f"Failed to download model: {e}")
    
    def upload(self, filepath: str, metadata: Dict[str, Any] = None) -> str:
        """
        Upload a model to the registry.
        
        Args:
            filepath: Path to .aim file
            metadata: Optional metadata to include
        
        Returns:
            URL of the uploaded model
        """
        if not self.token:
            raise ValueError("API token required for uploading")
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (filepath.name, f)}
                data = metadata or {}
                
                url = f"{self.hub_url}/api/models/upload"
                response = self.session.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 201:
                return response.json().get('url', '')
            else:
                raise Exception(f"Upload failed: {response.status_code}")
        
        except requests.RequestException as e:
            raise Exception(f"Failed to upload model: {e}")
    
    def list_models(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all models in the registry.
        
        Args:
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of model metadata
        """
        try:
            params = {'limit': limit, 'offset': offset}
            url = f"{self.hub_url}/api/models"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('models', [])
            else:
                return []
        
        except requests.RequestException:
            return []


class HubServer:
    """
    Backend server for AIM Hub registry.
    
    This would typically be deployed separately and handle:
    - Model storage and serving
    - User authentication
    - Model discovery
    - Statistics and analytics
    """
    
    def __init__(self, storage_dir: str, db_url: str = None):
        """
        Initialize hub server.
        
        Args:
            storage_dir: Directory to store model files
            db_url: Database connection URL
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def register_model(self, model_data: Dict[str, Any]) -> str:
        """Register a new model in the hub."""
        # In real implementation, would store in database
        pass
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information."""
        pass
    
    def list_models(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List models with optional filters."""
        pass

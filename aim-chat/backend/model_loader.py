"""
AIM Chat - Model Loader
Loads .aim knowledge files in JSON format
"""

import json
import os


class ModelLoader:
    """Handles loading and validation of .aim model files"""
    
    def __init__(self):
        self.current_model = None
        self.knowledge_base = []
    
    def load_model(self, filepath):
        """
        Load a .aim model file
        
        Args:
            filepath: Path to the .aim file
            
        Returns:
            dict: Model metadata and knowledge
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        # Validate required fields
        required_fields = ['name', 'version', 'type', 'knowledge']
        for field in required_fields:
            if field not in model_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate knowledge is a list
        if not isinstance(model_data['knowledge'], list):
            raise ValueError("Knowledge must be a list of sentences")
        
        if len(model_data['knowledge']) == 0:
            raise ValueError("Knowledge base is empty")
        
        # Store the loaded model
        self.current_model = model_data
        self.knowledge_base = model_data['knowledge']
        
        return {
            'name': model_data['name'],
            'version': model_data['version'],
            'type': model_data['type'],
            'knowledge_count': len(self.knowledge_base)
        }
    
    def load_from_json(self, json_data):
        """
        Load a model from JSON data (for API uploads)
        
        Args:
            json_data: Dictionary containing model data
            
        Returns:
            dict: Model metadata
        """
        # Validate required fields
        required_fields = ['name', 'version', 'type', 'knowledge']
        for field in required_fields:
            if field not in json_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate knowledge
        if not isinstance(json_data['knowledge'], list):
            raise ValueError("Knowledge must be a list of sentences")
        
        if len(json_data['knowledge']) == 0:
            raise ValueError("Knowledge base is empty")
        
        # Store the model
        self.current_model = json_data
        self.knowledge_base = json_data['knowledge']
        
        return {
            'name': json_data['name'],
            'version': json_data['version'],
            'type': json_data['type'],
            'knowledge_count': len(self.knowledge_base)
        }
    
    def get_knowledge(self):
        """Get the current knowledge base"""
        return self.knowledge_base
    
    def get_model_info(self):
        """Get information about the current model"""
        if not self.current_model:
            return None
        
        return {
            'name': self.current_model['name'],
            'version': self.current_model['version'],
            'type': self.current_model['type'],
            'knowledge_count': len(self.knowledge_base),
            'description': self.current_model.get('description', 'No description')
        }
    
    def is_loaded(self):
        """Check if a model is currently loaded"""
        return self.current_model is not None

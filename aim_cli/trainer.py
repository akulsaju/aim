"""
AIM Dataset Trainer
Handles training data from various file formats
"""

import csv
import json
import os
from pathlib import Path
from typing import Optional, Union


class DatasetTrainer:
    """
    Load and preprocess training data from various formats.
    
    Supported formats:
    - .txt: Plain text
    - .md: Markdown files
    - .csv: CSV data
    - .json: JSON structures
    - .pdf (with pdf_reader plugin)
    """
    
    SUPPORTED_FORMATS = ['.txt', '.md', '.csv', '.json']
    
    @staticmethod
    def load(filepath: str, format: Optional[str] = None) -> str:
        """
        Load training data from file.
        
        Args:
            filepath: Path to data file
            format: Optional format override
        
        Returns:
            Text data for training
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Determine format
        if format is None:
            format = filepath.suffix.lower()
        
        # Load based on format
        if format in ['.txt', '.md']:
            return DatasetTrainer._load_text(filepath)
        elif format == '.csv':
            return DatasetTrainer._load_csv(filepath)
        elif format == '.json':
            return DatasetTrainer._load_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def _load_text(filepath: Path) -> str:
        """Load plain text file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _load_csv(filepath: Path) -> str:
        """Load CSV and convert to text."""
        texts = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Combine all columns
                text = ' '.join(str(v) for v in row.values() if v)
                texts.append(text)
        
        return '\n'.join(texts)
    
    @staticmethod
    def _load_json(filepath: Path) -> str:
        """Load JSON and extract text."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            texts = []
            for item in data:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict):
                    texts.append(' '.join(str(v) for v in item.values()))
            return '\n'.join(texts)
        elif isinstance(data, dict):
            return ' '.join(str(v) for v in data.values())
        else:
            return str(data)
    
    @staticmethod
    def combine_datasets(*filepaths: str) -> str:
        """
        Combine multiple training files into single dataset.
        
        Args:
            *filepaths: Paths to data files
        
        Returns:
            Combined text data
        """
        all_texts = []
        for filepath in filepaths:
            text = DatasetTrainer.load(filepath)
            all_texts.append(text)
        
        return '\n\n'.join(all_texts)


def create_trainer(input_file: str, **kwargs):
    """
    Create a trainer with loaded dataset.
    
    Args:
        input_file: Path to training data file
        **kwargs: Additional arguments
    
    Returns:
        Trainer with loaded data
    """
    data = DatasetTrainer.load(input_file)
    return data

"""
AIM Engine System
Pluggable engine implementations for different AI model types
"""

from typing import Dict, Type, Any
from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """Abstract base class for AIM engines."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize engine with configuration.
        
        Args:
            config: Engine-specific configuration
        """
        self.config = config or {}
        self.model_data = {}
    
    @abstractmethod
    def train(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            data: Training data (format depends on engine)
            **kwargs: Additional parameters
        
        Returns:
            Trained model data
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str = None, **kwargs) -> str:
        """
        Generate output.
        
        Args:
            prompt: Optional input prompt
            **kwargs: Additional parameters
        
        Returns:
            Generated output
        """
        pass
    
    @abstractmethod
    def save(self, filepath: str):
        """Save model to file."""
        pass
    
    @abstractmethod
    def load(self, filepath: str):
        """Load model from file."""
        pass


class MarkovEngine(BaseEngine):
    """Markov chain text generation engine."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.order = self.config.get("order", 2)
        self.transitions = {}
        self.start_words = []
    
    def train(self, text: str, **kwargs) -> Dict[str, Any]:
        """Train Markov model on text."""
        import re
        from collections import defaultdict
        
        order = kwargs.get("order", self.order)
        self.order = order
        
        # Preprocess text
        words = re.findall(r'\w+|[.,!?;]', text.lower())
        
        if len(words) < order + 1:
            raise ValueError(f"Text too short. Need at least {order + 1} words.")
        
        # Build transitions
        transitions = defaultdict(list)
        start_words = []
        
        for i in range(len(words) - order):
            state = tuple(words[i:i + order])
            next_word = words[i + order]
            transitions[state].append(next_word)
            
            if i == 0:
                start_words.append(state)
        
        # Track all starting states
        for i in range(min(100, len(words) - order)):
            state = tuple(words[i:i + order])
            if state not in start_words:
                start_words.append(state)
        
        self.transitions = dict(transitions)
        self.start_words = start_words
        
        return {
            "order": order,
            "vocabulary_size": len(set(words)),
            "transitions_count": len(self.transitions),
            "sample_states": list(self.transitions.keys())[:5]
        }
    
    def generate(self, prompt: str = None, max_length: int = 100, temperature: float = 1.0, **kwargs) -> str:
        """Generate text using Markov model."""
        import random
        
        if not self.transitions:
            return "Error: No trained model available."
        
        # Choose starting state
        if prompt:
            prompt_words = prompt.lower().split()
            if len(prompt_words) >= self.order:
                current_state = tuple(prompt_words[-self.order:])
                if current_state not in self.transitions:
                    current_state = random.choice(self.start_words)
                result = list(prompt_words)
            else:
                current_state = random.choice(self.start_words)
                result = list(current_state)
        else:
            current_state = random.choice(self.start_words)
            result = list(current_state)
        
        # Generate words
        for _ in range(max_length - len(result)):
            if current_state not in self.transitions:
                break
            
            possible_next = self.transitions[current_state]
            if not possible_next:
                break
            
            next_word = random.choice(possible_next)
            result.append(next_word)
            current_state = tuple(list(current_state[1:]) + [next_word])
        
        return ' '.join(result)
    
    def save(self, filepath: str):
        """Save Markov model to file."""
        import json
        data = {
            "engine": "markov",
            "order": self.order,
            "transitions": {' '.join(k): v for k, v in self.transitions.items()},
            "start_words": [' '.join(w) for w in self.start_words]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, filepath: str):
        """Load Markov model from file."""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.order = data["order"]
        self.transitions = {tuple(k.split()): v for k, v in data["transitions"].items()}
        self.start_words = [tuple(w.split()) for w in data["start_words"]]


class NgramEngine(BaseEngine):
    """N-gram language model engine."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.ngram_size = self.config.get("ngram_size", 3)
        self.ngrams = {}
    
    def train(self, text: str, **kwargs) -> Dict[str, Any]:
        """Train n-gram model."""
        import re
        from collections import Counter
        
        ngram_size = kwargs.get("ngram_size", self.ngram_size)
        self.ngram_size = ngram_size
        
        words = re.findall(r'\w+', text.lower())
        
        self.ngrams = {}
        for i in range(len(words) - ngram_size + 1):
            ngram = ' '.join(words[i:i + ngram_size])
            self.ngrams[ngram] = self.ngrams.get(ngram, 0) + 1
        
        return {
            "ngram_size": ngram_size,
            "total_ngrams": len(self.ngrams),
            "vocabulary_size": len(set(words))
        }
    
    def generate(self, prompt: str = None, max_length: int = 100, **kwargs) -> str:
        """Generate text using n-gram model."""
        return "N-gram generation not yet implemented"
    
    def save(self, filepath: str):
        """Save n-gram model."""
        import json
        data = {"engine": "ngram", "ngram_size": self.ngram_size, "ngrams": self.ngrams}
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, filepath: str):
        """Load n-gram model."""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.ngram_size = data["ngram_size"]
        self.ngrams = data["ngrams"]


class EmbeddingEngine(BaseEngine):
    """Embedding-based similarity engine."""
    
    def train(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Train embedding model."""
        return {"status": "Embedding engine requires external library (transformers)"}
    
    def generate(self, prompt: str = None, **kwargs) -> str:
        """Generate similar content using embeddings."""
        return "Embedding generation requires transformers library"
    
    def save(self, filepath: str):
        """Save embedding model."""
        pass
    
    def load(self, filepath: str):
        """Load embedding model."""
        pass


class LLMEngine(BaseEngine):
    """Large Language Model engine (OpenAI, Hugging Face, etc.)."""
    
    def train(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Configure LLM engine."""
        return {"status": "LLM engine uses pre-trained models"}
    
    def generate(self, prompt: str = None, **kwargs) -> str:
        """Generate text using LLM."""
        return "LLM generation requires API keys"
    
    def save(self, filepath: str):
        """Save LLM configuration."""
        pass
    
    def load(self, filepath: str):
        """Load LLM configuration."""
        pass


# Engine registry
ENGINE_REGISTRY: Dict[str, Type[BaseEngine]] = {
    "markov": MarkovEngine,
    "ngram": NgramEngine,
    "embedding": EmbeddingEngine,
    "llm": LLMEngine,
}


def get_engine(engine_name: str, config: Dict[str, Any] = None) -> BaseEngine:
    """
    Get an engine instance by name.
    
    Args:
        engine_name: Name of the engine
        config: Engine configuration
    
    Returns:
        Engine instance
    
    Raises:
        ValueError: If engine not found
    """
    if engine_name not in ENGINE_REGISTRY:
        raise ValueError(f"Unknown engine: {engine_name}")
    
    engine_class = ENGINE_REGISTRY[engine_name]
    return engine_class(config)


def list_engines() -> list:
    """List all available engines."""
    return list(ENGINE_REGISTRY.keys())


def register_engine(name: str, engine_class: Type[BaseEngine]):
    """
    Register a custom engine.
    
    Args:
        name: Engine name
        engine_class: Engine class
    """
    ENGINE_REGISTRY[name] = engine_class

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
    """Large Language Model engine supporting multiple providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.provider = self.config.get("provider", "openai")
        self.api_key = self.config.get("api_key", None)
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.context = self.config.get("context", "You are a helpful AI assistant.")
        self.training_data = []
        
    def train(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Store training data as context for LLM."""
        if isinstance(data, str):
            self.training_data.append(data)
            self.context = f"You are an AI trained on the following content:\n\n{data[:1000]}...\n\nUse this context to answer questions."
        
        return {
            "status": "LLM configured with context",
            "context_length": len(self.training_data),
            "provider": self.provider
        }
    
    def generate(self, prompt: str = None, **kwargs) -> str:
        """Generate text using LLM API."""
        max_length = kwargs.get("max_length", 100)
        temperature = kwargs.get("temperature", 0.7)
        
        if not prompt:
            prompt = "Generate some interesting content."
        
        # Try OpenAI if configured
        if self.provider == "openai" and self.api_key:
            return self._generate_openai(prompt, max_length, temperature)
        
        # Fallback to local generation
        return self._generate_local(prompt, max_length, temperature)
    
    def _generate_openai(self, prompt: str, max_length: int, temperature: float) -> str:
        """Generate using OpenAI API."""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_length,
                "temperature": temperature
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"OpenAI API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
    
    def _generate_local(self, prompt: str, max_length: int, temperature: float) -> str:
        """Fallback: Generate using simple template-based approach."""
        import random
        
        # Simple template responses for demonstration
        templates = [
            f"Based on your input '{prompt}', here's a thoughtful response: This is an interesting topic that deserves attention.",
            f"Regarding '{prompt}', I would say that understanding the context is key to providing meaningful insights.",
            f"Your question about '{prompt}' is intriguing. Let me share some thoughts on this subject.",
            f"Thank you for asking about '{prompt}'. This topic has several important aspects worth considering.",
        ]
        
        base_response = random.choice(templates)
        
        # Add training context if available
        if self.training_data:
            words = self.training_data[0].split()[:50]
            context_sample = " ".join(words)
            base_response += f"\n\nDrawing from the training data: {context_sample}"
        
        return base_response
    
    def save(self, filepath: str):
        """Save LLM configuration."""
        import json
        data = {
            "engine": "llm",
            "provider": self.provider,
            "model": self.model,
            "context": self.context,
            "training_data": self.training_data
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, filepath: str):
        """Load LLM configuration."""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.provider = data.get("provider", "openai")
        self.model = data.get("model", "gpt-3.5-turbo")
        self.context = data.get("context", "")
        self.training_data = data.get("training_data", [])


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

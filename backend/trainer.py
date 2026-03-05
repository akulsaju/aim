"""
AIM Studio - Trainer Module
This module handles text processing and Markov chain model training.
"""

import re
from collections import defaultdict
import random


class MarkovTrainer:
    """
    A simple Markov chain text model trainer.
    
    This trainer builds a probabilistic model that learns word transitions
    from input text. It can be used to generate new text that mimics the
    style and patterns of the training data.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov trainer.
        
        Args:
            order (int): The order of the Markov chain (number of previous words to consider).
                        Default is 2 (bigram model).
        """
        self.order = order
        self.transitions = defaultdict(list)
        self.start_words = []
        
    def preprocess_text(self, text):
        """
        Clean and tokenize the input text.
        
        Args:
            text (str): Raw input text
            
        Returns:
            list: List of cleaned words
        """
        # Convert to lowercase and split into words
        # Keep basic punctuation as separate tokens
        words = re.findall(r'\w+|[.,!?;]', text.lower())
        return words
    
    def train(self, text):
        """
        Train the Markov model on the provided text.
        
        This method builds a transition dictionary where each key is a tuple
        of N words (where N = order) and the value is a list of words that
        can follow that sequence.
        
        Args:
            text (str): Training text data
        """
        # Preprocess the text into words
        words = self.preprocess_text(text)
        
        if len(words) < self.order + 1:
            raise ValueError(f"Text too short. Need at least {self.order + 1} words.")
        
        # Build the transition dictionary
        for i in range(len(words) - self.order):
            # Create a key from the current sequence of words
            state = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            
            # Add the next word to the list of possible transitions
            self.transitions[state].append(next_word)
            
            # Track starting words (for text generation)
            if i == 0:
                self.start_words.append(state)
        
        # Also track all possible starting sequences
        for i in range(min(100, len(words) - self.order)):
            state = tuple(words[i:i + self.order])
            if state not in self.start_words:
                self.start_words.append(state)
    
    def get_model_data(self):
        """
        Export the trained model data.
        
        Returns:
            dict: Model data including transitions and metadata
        """
        # Convert defaultdict to regular dict for JSON serialization
        transitions_dict = {
            ' '.join(k): v for k, v in self.transitions.items()
        }
        
        start_words_list = [' '.join(words) for words in self.start_words]
        
        return {
            'order': self.order,
            'transitions': transitions_dict,
            'start_words': start_words_list,
            'vocabulary_size': len(set([w for words in transitions_dict.values() for w in words]))
        }
    
    def load_model_data(self, model_data):
        """
        Load previously trained model data.
        
        Args:
            model_data (dict): Model data to load
        """
        self.order = model_data['order']
        
        # Convert back from string keys to tuple keys
        self.transitions = defaultdict(list)
        for key, value in model_data['transitions'].items():
            tuple_key = tuple(key.split())
            self.transitions[tuple_key] = value
        
        # Convert start words back to tuples
        self.start_words = [tuple(words.split()) for words in model_data['start_words']]


def train_model(text, order=2):
    """
    Convenience function to train a new model.
    
    Args:
        text (str): Training text
        order (int): Markov chain order
        
    Returns:
        MarkovTrainer: Trained model object
    """
    trainer = MarkovTrainer(order=order)
    trainer.train(text)
    return trainer

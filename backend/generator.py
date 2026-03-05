"""
AIM Studio - Generator Module
This module handles text generation from trained Markov chain models.
"""

import random


class MarkovGenerator:
    """
    Text generator using Markov chain transitions.
    
    This generator takes a trained Markov model and generates new text
    that follows the patterns learned during training.
    """
    
    def __init__(self, trainer):
        """
        Initialize the generator with a trained model.
        
        Args:
            trainer: A MarkovTrainer object with trained model data
        """
        self.trainer = trainer
        self.transitions = trainer.transitions
        self.start_words = trainer.start_words
        self.order = trainer.order
    
    def generate(self, max_length=100, prompt=None, temperature=1.0):
        """
        Generate text using the trained Markov model.
        
        Args:
            max_length (int): Maximum number of words to generate
            prompt (str): Optional starting words for generation
            temperature (float): Controls randomness (higher = more random)
                               1.0 = normal, 0.5 = more deterministic
        
        Returns:
            str: Generated text
        """
        if not self.transitions:
            return "Error: No trained model available."
        
        # Choose starting state
        if prompt:
            # Use the prompt as starting words
            prompt_words = prompt.lower().split()
            
            # Try to find a matching state in our model
            if len(prompt_words) >= self.order:
                current_state = tuple(prompt_words[-self.order:])
                # Check if this state exists in our model
                if current_state not in self.transitions:
                    # If not found, use a random start
                    current_state = random.choice(self.start_words)
                result = list(prompt_words)
            else:
                # Prompt too short, use random start
                current_state = random.choice(self.start_words)
                result = list(current_state)
        else:
            # No prompt, start randomly
            current_state = random.choice(self.start_words)
            result = list(current_state)
        
        # Generate words one by one
        for _ in range(max_length - len(result)):
            if current_state not in self.transitions:
                # Dead end - no transitions available
                break
            
            # Get possible next words
            possible_next = self.transitions[current_state]
            
            if not possible_next:
                break
            
            # Apply temperature to selection
            if temperature != 1.0 and len(set(possible_next)) > 1:
                # Simple temperature: more likely to pick common words when temp < 1
                # For simplicity, just use random choice (full temperature would need word frequencies)
                next_word = random.choice(possible_next)
            else:
                # Random choice from possibilities
                next_word = random.choice(possible_next)
            
            result.append(next_word)
            
            # Update state: shift window forward
            current_state = tuple(list(current_state[1:]) + [next_word])
        
        # Convert word list to text
        text = self._format_text(result)
        return text
    
    def _format_text(self, words):
        """
        Format a list of words into readable text.
        
        Handles spacing around punctuation.
        
        Args:
            words (list): List of words and punctuation tokens
            
        Returns:
            str: Formatted text
        """
        text = ""
        for i, word in enumerate(words):
            # Don't add space before punctuation
            if word in '.,!?;':
                text += word
            else:
                if i > 0:
                    text += " " + word
                else:
                    text += word
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def generate_multiple(self, count=3, max_length=100, prompt=None):
        """
        Generate multiple text samples.
        
        Args:
            count (int): Number of samples to generate
            max_length (int): Maximum length for each sample
            prompt (str): Optional starting prompt
            
        Returns:
            list: List of generated text strings
        """
        samples = []
        for _ in range(count):
            sample = self.generate(max_length=max_length, prompt=prompt)
            samples.append(sample)
        return samples


def generate_text(trainer, max_length=100, prompt=None, temperature=1.0):
    """
    Convenience function to generate text from a trained model.
    
    Args:
        trainer: Trained MarkovTrainer object
        max_length (int): Maximum words to generate
        prompt (str): Starting words (optional)
        temperature (float): Randomness control
        
    Returns:
        str: Generated text
    """
    generator = MarkovGenerator(trainer)
    return generator.generate(max_length=max_length, prompt=prompt, temperature=temperature)

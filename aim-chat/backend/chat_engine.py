"""
AIM Chat - Chat Engine
Retrieves relevant knowledge based on user queries using keyword matching
"""

import re
from collections import Counter


class ChatEngine:
    """Simple keyword-based retrieval system for answering questions"""
    
    def __init__(self, knowledge_base=None):
        """
        Initialize the chat engine
        
        Args:
            knowledge_base: List of knowledge sentences
        """
        self.knowledge_base = knowledge_base or []
        self.conversation_history = []
    
    def set_knowledge(self, knowledge_base):
        """Update the knowledge base"""
        self.knowledge_base = knowledge_base
    
    def extract_keywords(self, text):
        """
        Extract meaningful keywords from text
        
        Args:
            text: Input text string
            
        Returns:
            list: List of keywords (lowercase, no stopwords)
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', text)
        
        # Common English stopwords to ignore
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'what', 'when', 'where', 'who', 'why',
            'how', 'i', 'you', 'me', 'my', 'we', 'us', 'am', 'do', 'does',
            'can', 'could', 'should', 'would', 'may', 'might', 'this', 'these',
            'those', 'tell', 'about', 'give', 'show', 'explain', 'get', 'make'
        }
        
        # Filter out stopwords and short words
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords
    
    def calculate_relevance(self, sentence, keywords):
        """
        Calculate how relevant a sentence is to the keywords
        
        Args:
            sentence: Knowledge sentence to check
            keywords: List of keywords from user query
            
        Returns:
            float: Relevance score (higher is better)
        """
        sentence_lower = sentence.lower()
        sentence_words = set(re.findall(r'\b\w+\b', sentence_lower))
        score = 0.0
        
        for keyword in keywords:
            # Exact word match - highest score
            if keyword in sentence_words:
                score += 10.0
            # Partial match (substring)
            elif keyword in sentence_lower:
                score += 3.0
            # Similar words (e.g., sun/solar, earth/planet)
            else:
                for word in sentence_words:
                    # Check if words share significant overlap
                    if len(keyword) >= 4 and len(word) >= 4:
                        if keyword[:3] == word[:3]:
                            score += 1.5
        
        # Bonus for multiple keyword matches
        matches = sum(1 for kw in keywords if kw in sentence_words)
        if matches > 1:
            score += matches * 2
        
        return score
    
    def find_best_response(self, user_message):
        """
        Find the most relevant knowledge sentence for the user's message
        
        Args:
            user_message: User's input message
            
        Returns:
            str: Best matching knowledge sentence, or default response if no match
        """
        if not self.knowledge_base:
            return "I don't have any knowledge loaded yet. Please load a model first."
        
        # Extract keywords from user message
        keywords = self.extract_keywords(user_message)
        
        if not keywords:
            return "Could you ask a more specific question? I'll do my best to help!"
        
        # Calculate relevance for each knowledge sentence
        scored_sentences = []
        for sentence in self.knowledge_base:
            score = self.calculate_relevance(sentence, keywords)
            if score > 0:
                scored_sentences.append((sentence, score))
        
        # If no matches found, try to suggest related topics
        if not scored_sentences:
            # Show what topics are available
            sample_topics = []
            for sentence in self.knowledge_base[:5]:
                words = re.findall(r'\b[A-Z][a-z]+\b', sentence)
                if words:
                    sample_topics.extend(words[:2])
            
            if sample_topics:
                topics = ', '.join(set(sample_topics[:5]))
                return f"I don't have information about that. Try asking about: {topics}"
            return "I don't have information about that. Try asking something else!"
        
        # Sort by relevance, then by length (prefer longer, more informative sentences)
        scored_sentences.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
        
        # Get top candidates (all with same best score)
        best_score = scored_sentences[0][1]
        top_candidates = [s for s in scored_sentences if s[1] == best_score]
        
        # If multiple candidates with same score, prefer longer ones
        if len(top_candidates) > 1:
            top_candidates.sort(key=lambda x: len(x[0]), reverse=True)
        
        # If best score is very low, inform user
        if best_score < 3:
            return f"I'm not very confident, but here's what I found: {top_candidates[0][0]}"
        
        # Return the best match (longest among highest scored)
        return top_candidates[0][0]
    
    def chat(self, user_message):
        """
        Process a user message and generate a response
        
        Args:
            user_message: User's input message
            
        Returns:
            dict: Response containing AI message and metadata
        """
        # Find the best response
        ai_response = self.find_best_response(user_message)
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        
        return {
            'response': ai_response,
            'confidence': 'high' if ai_response not in [
                "I don't have any knowledge loaded yet. Please load a model first.",
                "I'm not sure what you're asking. Could you rephrase your question?",
                "I don't have information about that. Try asking something else!"
            ] else 'low'
        }
    
    def get_conversation_history(self):
        """Get the full conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_stats(self):
        """Get statistics about the chat engine"""
        return {
            'knowledge_count': len(self.knowledge_base),
            'conversation_length': len(self.conversation_history),
            'user_messages': sum(1 for msg in self.conversation_history if msg['role'] == 'user'),
            'ai_messages': sum(1 for msg in self.conversation_history if msg['role'] == 'assistant')
        }

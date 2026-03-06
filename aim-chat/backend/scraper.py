"""
Web scraper for converting websites to AIM knowledge files
Created by @akulsaju - https://github.com/akulsaju
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class WebScraper:
    """Scrape websites and extract knowledge sentences"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_url(self, url):
        """
        Scrape a URL and extract text content
        
        Args:
            url: Website URL to scrape
            
        Returns:
            dict: Scraped content with title and sentences
        """
        try:
            # Fetch the webpage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Determine if it's Wikipedia
            is_wikipedia = 'wikipedia.org' in url.lower()
            
            if is_wikipedia:
                return self._scrape_wikipedia(soup, url)
            else:
                return self._scrape_generic(soup, url)
                
        except Exception as e:
            raise Exception(f"Scraping failed: {str(e)}")
    
    def _scrape_wikipedia(self, soup, url):
        """Extract comprehensive content from Wikipedia pages"""
        # Get title
        title_tag = soup.find('h1', {'id': 'firstHeading'})
        title = title_tag.get_text().strip() if title_tag else 'Wikipedia Article'
        
        # Get main content
        content_div = soup.find('div', {'id': 'mw-content-text'})
        
        if not content_div:
            raise Exception("Could not find Wikipedia content")
        
        paragraphs = []
        
        # Extract from infobox/sidebar first (contains key facts)
        infobox = content_div.find('table', {'class': 'infobox'})
        if infobox:
            # Get all text from infobox
            infobox_text = infobox.get_text().strip()
            # Process infobox content
            infobox_lines = [line.strip() for line in infobox_text.split('\n') if line.strip() and len(line.strip()) > 5]
            paragraphs.extend(infobox_lines[:20])  # Limit to 20 infobox facts
        
        # Extract all main paragraphs from content
        for element in content_div.find_all(['p', 'li'], recursive=True):
            # Skip if inside certain containers
            parent = element.parent
            parent_classes = str(parent.get('class', []))
            
            if any(cls in parent_classes for cls in ['reference', 'reflist', 'navbox', 'navframe', 'toc']):
                continue
            
            text = element.get_text().strip()
            
            # Clean references from text
            text = re.sub(r'\[\d+\]', '', text)
            text = re.sub(r'\[edit\]', '', text)
            text = text.strip()
            
            if text and len(text) > 15:  # Include more content
                paragraphs.append(text)
        
        # Extract section headings and their first paragraphs
        for heading in content_div.find_all(['h2', 'h3'], recursive=True):
            # Get heading text
            heading_text = heading.get_text().strip()
            
            # Skip edit links and references sections
            if '[edit]' in heading_text or heading_text.lower() in ['references', 'see also', 'external links']:
                heading_text = heading_text.replace('[edit]', '').strip()
                if heading_text.lower() in ['references', 'see also', 'external links']:
                    continue
            
            # Get next paragraph after heading
            next_elem = heading.find_next('p')
            if next_elem:
                section_text = next_elem.get_text().strip()
                if section_text and len(section_text) > 15:
                    # Add heading as context
                    full_text = f"{heading_text}: {section_text}"
                    paragraphs.append(full_text)
        
        # Remove duplicates and limit to 200 paragraphs
        paragraphs = list(dict.fromkeys(paragraphs))[:200]
        
        # Extract sentences
        sentences = self._extract_sentences(paragraphs)
        
        # Get a description from first real paragraph
        description = paragraphs[0][:200] + '...' if paragraphs else f'Knowledge from {title}'
        
        return {
            'title': title,
            'description': description,
            'sentences': sentences,
            'url': url,
            'source': 'Wikipedia',
            'paragraphs_extracted': len(paragraphs)
        }
    
    def _scrape_generic(self, soup, url):
        """Extract content from generic websites"""
        # Get title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Get main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if not main_content:
            raise Exception("Could not find main content")
        
        # Extract paragraphs
        paragraphs = []
        for p in main_content.find_all(['p', 'div']):
            text = p.get_text().strip()
            if text and len(text) > 20:
                paragraphs.append(text)
        
        # Extract sentences
        sentences = self._extract_sentences(paragraphs)
        
        description = f'Knowledge scraped from {urlparse(url).netloc}'
        
        return {
            'title': title,
            'description': description,
            'sentences': sentences,
            'url': url,
            'source': urlparse(url).netloc
        }
    
    def _extract_sentences(self, paragraphs):
        """
        Extract individual sentences from paragraphs
        
        Args:
            paragraphs: List of paragraph strings
            
        Returns:
            list: Clean sentences
        """
        sentences = []
        
        for paragraph in paragraphs:
            # Clean the text
            text = self._clean_text(paragraph)
            
            # Split into sentences using regex
            # Split on period, exclamation, or question mark followed by space/newline
            raw_sentences = re.split(r'([.!?])\s+', text)
            
            # Reconstruct sentences with punctuation
            current_sentence = ""
            for i, part in enumerate(raw_sentences):
                if part in ['.', '!', '?']:
                    current_sentence += part
                    if current_sentence.strip():
                        cleaned = current_sentence.strip()
                        # Only keep substantial sentences
                        if len(cleaned) > 15 and not self._is_junk(cleaned):
                            sentences.append(cleaned)
                    current_sentence = ""
                else:
                    current_sentence += part
            
            # Don't forget the last sentence if it doesn't end with punctuation
            if current_sentence.strip():
                cleaned = current_sentence.strip()
                if len(cleaned) > 15 and not self._is_junk(cleaned):
                    sentences.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sentences = []
        for sentence in sentences:
            if sentence not in seen:
                seen.add(sentence)
                unique_sentences.append(sentence)
        
        return unique_sentences
    
    def _clean_text(self, text):
        """Clean extracted text"""
        # Remove citation markers [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove newlines
        text = text.replace('\n', ' ')
        
        return text.strip()
    
    def _is_junk(self, sentence):
        """Check if a sentence is junk/noise"""
        junk_patterns = [
            r'^see also',
            r'^references',
            r'^external links',
            r'^retrieved',
            r'^archived',
            r'^\d+\s*$',  # Just numbers
            r'^[^a-zA-Z]+$',  # No letters
        ]
        
        sentence_lower = sentence.lower()
        
        for pattern in junk_patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        return False
    
    def save_as_aim(self, scraped_data, output_path, model_name=None):
        """
        Save scraped data as .aim file
        
        Args:
            scraped_data: Dict from scrape_url()
            output_path: Path to save .aim file
            model_name: Optional custom model name
            
        Returns:
            dict: Model info
        """
        import json
        
        # Create model structure
        model = {
            "name": model_name or scraped_data['title'].replace(' ', '_'),
            "version": "1.0",
            "type": "chat",
            "description": scraped_data['description'],
            "knowledge": scraped_data['sentences'],
            "metadata": {
                "source": scraped_data['source'],
                "url": scraped_data['url'],
                "sentences_count": len(scraped_data['sentences'])
            }
        }
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(model, f, indent=2, ensure_ascii=False)
        
        return {
            'name': model['name'],
            'sentences': len(model['knowledge']),
            'path': output_path
        }

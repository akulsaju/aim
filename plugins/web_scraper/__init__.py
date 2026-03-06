"""
Web Scraper Plugin
Extracts text from web pages for model training
"""

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0].rsplit('\\', 1)[0])

from aim_core.plugins import BasePlugin


class Plugin(BasePlugin):
    """Web page text scraping plugin."""
    
    name = "web_scraper"
    version = "1.0.0"
    description = "Scrape text from web pages"
    author = "AIM Team"
    
    def execute(self, url: str, **kwargs) -> str:
        """
        Scrape text from web page.
        
        Args:
            url: URL to scrape
            **kwargs: Additional arguments
        
        Returns:
            Extracted text
        """
        try:
            from bs4 import BeautifulSoup
            import requests
        except ImportError:
            return "BeautifulSoup/requests not installed. Install with: pip install beautifulsoup4 requests"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"

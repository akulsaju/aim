"""
PDF Reader Plugin
Extracts text from PDF files for model training
"""

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0].rsplit('\\', 1)[0])

from aim_core.plugins import BasePlugin


class Plugin(BasePlugin):
    """PDF text extraction plugin."""
    
    name = "pdf_reader"
    version = "1.0.0"
    description = "Extract text from PDF files"
    author = "AIM Team"
    
    def execute(self, pdf_path: str, **kwargs) -> str:
        """
        Extract text from PDF.
        
        Args:
            pdf_path: Path to PDF file
            **kwargs: Additional arguments
        
        Returns:
            Extracted text
        """
        try:
            import PyPDF2
        except ImportError:
            return "PyPDF2 not installed. Install with: pip install PyPDF2"
        
        text = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        
        return '\n'.join(text)

import fitz
import re
import io
from typing import List, Dict, Tuple

class EnhancedPDFProcessor:
    def __init__(self):
        self.page_content = []
    
    def extract_text_with_pages(self, pdf_file):
        pdf_file.seek(0)
        file_content = pdf_file.read()
        stream = io.BytesIO(file_content)
        
        doc = fitz.open(stream=stream, filetype="pdf")
        pages = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            cleaned_text = self._clean_text(text)
            
            page_data = {
                'page_number': page_num + 1,
                'text': cleaned_text,
                'word_count': len(cleaned_text.split()),
                'headers': self._extract_headers(cleaned_text),
                'has_tables': self._detect_tables(page),
                'has_images': self._detect_images(page)
            }
            pages.append(page_data)
        
        doc.close()
        self.page_content = pages
        return pages
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'Page \d+', '', text)
        return text.strip()
    
    def _extract_headers(self, text: str) -> list:
        lines = text.split('\n')
        headers = []
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100 and line.isupper():
                headers.append(line)
        return headers[:3]
    
    def _detect_tables(self, page) -> bool:
        text = page.get_text()
        table_chars = ['|', '+', '-', '=']
        return any(char in text for char in table_chars)
    
    def _detect_images(self, page) -> bool:
        return len(page.get_images()) > 0
    
    def create_structured_summary(self, pdf_file) -> Dict:
        pages = self.extract_text_with_pages(pdf_file)
        
        pages_with_tables = [p['page_number'] for p in pages if p['has_tables']]
        pages_with_images = [p['page_number'] for p in pages if p['has_images']]
        
        total_words = sum(p['word_count'] for p in pages)
        
        return {
            'total_pages': len(pages),
            'total_words': total_words,
            'pages_with_tables': pages_with_tables,
            'pages_with_images': pages_with_images
        }
    
    def _classify_content_type(self, page: Dict) -> str:
        if page['has_tables'] and page['has_images']:
            return 'mixed'
        elif page['has_tables']:
            return 'data'
        elif page['has_images']:
            return 'visual'
        elif page['word_count'] > 500:
            return 'text-heavy'
        else:
            return 'standard'
    
    def get_relevant_pages(self, query: str) -> List[int]:
        query_lower = query.lower()
        relevant_pages = []
        
        for page in self.page_content:
            text_lower = page['text'].lower()
            if any(word in text_lower for word in query_lower.split()):
                relevant_pages.append(page['page_number'])
        
        return relevant_pages[:5]
    
    def get_page_text(self, page_number: int) -> str:
        for page in self.page_content:
            if page['page_number'] == page_number:
                return page['text']
        return ""

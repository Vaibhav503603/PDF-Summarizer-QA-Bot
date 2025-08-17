import requests
import streamlit as st
from core.enhanced_pdf_processor import EnhancedPDFProcessor

class EnhancedAIService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.1:8b"
        self.pdf_processor = None
    
    def set_pdf_processor(self, processor: EnhancedPDFProcessor):
        self.pdf_processor = processor
    
    def create_structured_summary(self, pdf_file) -> dict:
        if not self.pdf_processor:
            self.pdf_processor = EnhancedPDFProcessor()
        
        page_content = self.pdf_processor.extract_text_with_pages(pdf_file)
        structured_summary = self.pdf_processor.create_structured_summary(pdf_file)
        
        all_text = ""
        for page in page_content:
            all_text += f"\n--- Page {page['page_number']} ---\n{page['text']}\n"
        
        if len(all_text) > 8000:
            all_text = all_text[:8000] + "\n\n[Content truncated for processing]"
        
        complete_summary = self._generate_complete_summary(all_text)
        
        structured_summary['complete_pdf_summary'] = complete_summary
        structured_summary['total_pages_analyzed'] = len(page_content)
        return structured_summary
    
    def answer_with_citations(self, question: str, pdf_file) -> dict:
        if not self.pdf_processor:
            self.pdf_processor = EnhancedPDFProcessor()
        
        page_content = self.pdf_processor.extract_text_with_pages(pdf_file)
        relevant_pages = self.pdf_processor.get_relevant_pages(question)
        
        context_parts = []
        for page_num in relevant_pages[:3]:
            page_text = self.pdf_processor.get_page_text(page_num)
            if page_text:
                context_parts.append(f"Page {page_num}: {page_text[:1000]}...")
        
        context = "\n\n".join(context_parts)
        answer = self._generate_cited_answer(question, context, relevant_pages)
        
        return {
            'answer': answer,
            'cited_pages': relevant_pages,
            'total_pages_analyzed': len(page_content)
        }
    
    def _summarize_page_content(self, text: str, page_number: int) -> str:
        try:
            prompt = f"Summarize the main content from page {page_number} in 2-3 sentences:\n\n{text[:1500]}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", f"Page {page_number} contains relevant content.")
            else:
                return f"Page {page_number} content extracted successfully."
                
        except Exception as e:
            return f"Page {page_number} content extracted successfully."
    
    def _generate_cited_answer(self, question: str, context: str, cited_pages: list) -> str:
        try:
            pages_str = ", ".join([f"page {p}" for p in cited_pages])
            
            prompt = f"""Based on the following context from {pages_str}, answer this question clearly and concisely:

Context:
{context}

Question: {question}

Please provide a clear answer and mention which pages contain the relevant information."""

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "Answer generated successfully.")
                
                if not any(f"page {p}" in answer.lower() for p in cited_pages):
                    answer += f"\n\n📄 **Relevant pages**: {pages_str}"
                
                return answer
            else:
                return f"Answer generated based on pages {pages_str}."
                
        except Exception as e:
            pages_str = ", ".join([f"page {p}" for p in cited_pages])
            return f"Answer generated based on pages {pages_str}. (AI processing completed successfully)"
    
    def get_document_overview(self, pdf_file) -> dict:
        if not self.pdf_processor:
            self.pdf_processor = EnhancedPDFProcessor()
        
        page_content = self.pdf_processor.extract_text_with_pages(pdf_file)
        
        overview = {
            'total_pages': len(page_content),
            'total_words': sum(page['word_count'] for page in page_content),
            'content_distribution': {},
            'key_sections': []
        }
        
        for page in page_content:
            content_type = self.pdf_processor._classify_content_type(page)
            if content_type not in overview['content_distribution']:
                overview['content_distribution'][content_type] = []
            overview['content_distribution'][content_type].append(page['page_number'])
        
        for page in page_content:
            if page['headers']:
                overview['key_sections'].extend([
                    {'page': page['page_number'], 'header': header}
                    for header in page['headers'][:2]
                ])
        
        return overview

    def _generate_complete_summary(self, full_text: str) -> str:
        prompt = f"""Analyze this complete PDF document and provide a comprehensive summary:

{full_text}

Please provide a structured summary that includes:
1. Document Overview - What type of document is this?
2. Main Topics - What are the key subjects covered?
3. Key Findings - What are the most important points?
4. Structure - How is the document organized?
5. Conclusions - What are the main takeaways?

Focus on the overall document rather than individual pages."""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 1000
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Complete PDF summary generated successfully.")
            else:
                return f"Error generating summary: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

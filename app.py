import streamlit as st
import fitz
from core.enhanced_ai_service import EnhancedAIService
from core.enhanced_pdf_processor import EnhancedPDFProcessor

st.set_page_config(page_title="PDF Summarizer & QA Bot", layout="wide")

st.title("🤖 PDF Summarizer & QA Bot")

enhanced_ai = EnhancedAIService()
pdf_processor = EnhancedPDFProcessor()

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file is not None:
    with st.spinner("📖 Extracting text and analyzing document structure..."):
        overview = enhanced_ai.get_document_overview(uploaded_file)
        enhanced_ai.set_pdf_processor(pdf_processor)

    st.success(f"✅ PDF uploaded successfully! ({overview['total_pages']} pages, {overview['total_words']} words)")

    st.markdown("---")
    st.subheader("📊 Document Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Pages", overview['total_pages'])
        st.metric("Total Words", f"{overview['total_words']:,}")
    
    with col2:
        st.metric("Content Types", len(overview['content_distribution']))
        st.metric("Key Sections", len(overview['key_sections']))
    
    if overview['content_distribution']:
        st.subheader("📈 Content Distribution")
        for content_type, pages in overview['content_distribution'].items():
            st.write(f"**{content_type}**: Pages {', '.join(map(str, pages))}")
    
    if overview['key_sections']:
        st.subheader("🔑 Key Sections Identified")
        for section in overview['key_sections'][:10]:
            st.write(f"**Page {section['page']}**: {section['header']}")

    if st.button("📋 Generate Structured Summary", key="summary_btn", use_container_width=True):
        with st.spinner("🤖 AI is creating a structured hierarchical summary..."):
            summary = enhanced_ai.create_structured_summary(uploaded_file)
        
        st.markdown("---")
        st.subheader("📋 Structured Summary")
        
        st.metric("Total Pages", summary['total_pages'])
        st.metric("Total Words", f"{summary['total_words']:,}")
        
        if summary['pages_with_tables']:
            st.write(f"📊 **Pages with Tables**: {', '.join(map(str, summary['pages_with_tables']))}")
        if summary['pages_with_images']:
            st.write(f"🖼️ **Pages with Images**: {', '.join(map(str, summary['pages_with_images']))}")
        
        if 'complete_pdf_summary' in summary:
            st.subheader("🤖 Complete PDF Summary")
            st.write(summary['complete_pdf_summary'])
            st.info(f"📊 **Pages Analyzed**: {summary.get('total_pages_analyzed', 'N/A')}")

    st.markdown("---")
    st.subheader("💬 Ask Questions About Your Document")
    
    query = st.text_input(
        "What would you like to know about this document?",
        placeholder="e.g., What are the main points? What does it say about...?",
        help="Ask any question about the content of your uploaded PDF"
    )
    
    if st.button("🚀 Get Answer", type="primary", use_container_width=True):
        if query.strip():
            with st.spinner("🤖 AI is analyzing your document and finding relevant pages..."):
                result = enhanced_ai.answer_with_citations(query, uploaded_file)
            
            st.markdown("---")
            st.subheader("📝 AI Answer")
            st.write(result['answer'])
            
            if result['cited_pages']:
                st.info(f"📄 **Cited Pages**: {', '.join(map(str, result['cited_pages']))}")
                st.info(f"🔍 **Pages Analyzed**: {result['total_pages_analyzed']}")
        else:
            st.warning("Please enter a question first!")

elif uploaded_file is None:
    st.info("👆 Upload a PDF document to start analysis!")
    st.markdown("""
    ### 🚀 How it works:
    1. **Upload** your PDF document
    2. **Get overview** with content analysis and structure
    3. **Generate summary** with AI-powered insights
    4. **Ask questions** and receive answers with page citations
    
    Perfect for research papers, reports, articles, and any document requiring detailed analysis!
    """)

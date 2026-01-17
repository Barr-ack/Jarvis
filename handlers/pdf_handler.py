"""
PDF Handler
Handles PDF reading and extraction
"""

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class PDFHandler:
    def __init__(self):
        pass
    
    def read_pdf(self, file_path):
        """Read PDF file and extract text"""
        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            return {
                "status": "error", 
                "message": "PDF libraries not installed. Install PyPDF2 or pdfplumber."
            }
        
        try:
            text = self.extract_pdf_text(file_path)
            return text
        except Exception as e:
            return {"status": "error", "message": f"Failed to read PDF: {str(e)}"}
    
    def extract_pdf_text(self, file_path, page_range=None):
        """Extract text from PDF with optional page range"""
        try:
            import os
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"PDF file not found: {file_path}"}
            
            text = ""
            
            # Try pdfplumber first (better text extraction)
            if PDFPLUMBER_AVAILABLE:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    pages = pdf.pages
                    
                    if page_range:
                        start, end = map(int, page_range.split('-'))
                        pages = pages[start-1:end]
                    
                    for page in pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            
            # Fallback to PyPDF2
            elif PYPDF2_AVAILABLE:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    
                    if page_range:
                        start, end = map(int, page_range.split('-'))
                        start = max(0, start - 1)
                        end = min(total_pages, end)
                    else:
                        start, end = 0, total_pages
                    
                    for page_num in range(start, end):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            else:
                return {
                    "status": "error", 
                    "message": "No PDF library available. Install PyPDF2 or pdfplumber."
                }
            
            if text.strip():
                return {
                    "status": "success",
                    "message": f"Extracted text from PDF ({len(text)} characters)",
                    "text": text.strip()
                }
            else:
                return {
                    "status": "error",
                    "message": "No text could be extracted from the PDF"
                }
                
        except Exception as e:
            return {"status": "error", "message": f"PDF extraction failed: {str(e)}"}
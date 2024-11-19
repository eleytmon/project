import PyPDF2

class PDFProcessor:
    def __init__(self):
        self.pdf_contents = {}
    
    def read_pdf(self, uploaded_file):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error al procesar el PDF: {str(e)}")
    
    def store_pdf_content(self, filename, content):
        self.pdf_contents[filename] = content
    
    def get_all_contents(self):
        return "\n".join(self.pdf_contents.values())
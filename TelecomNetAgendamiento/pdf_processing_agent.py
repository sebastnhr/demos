from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer

class PDFProcessingAgent:
    def __init__(self):
        pass

    def read_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error al leer el archivo {file_path}: {str(e)}")
            return ""

    def read_multiple_pdfs(self, pdf_paths):
        all_text = ""
        for path in pdf_paths:
            all_text += self.read_pdf(path) + "\n\n"
        return all_text

    def split_text(self, text, chunk_size=1000, overlap=200):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def create_index(self, chunks):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(chunks)
        return vectorizer, tfidf_matrix
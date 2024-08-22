import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from urllib.parse import urlparse
import warnings

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

    def read_url(self, url):
        try:
            # Desactivar las advertencias de InsecureRequestWarning
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
            
            # Desactivar la verificación SSL
            response = requests.get(url, verify=False)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar scripts y estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            # Eliminar líneas en blanco y espacios extra
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error al leer la URL {url}: {str(e)}")
            return ""

    def read_multiple_sources(self, sources):
        all_text = ""
        for source in sources:
            if urlparse(source).scheme:  # Es una URL
                all_text += self.read_url(source) + "\n\n"
            else:  # Es un archivo local
                all_text += self.read_pdf(source) + "\n\n"
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
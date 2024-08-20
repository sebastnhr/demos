from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RetrievalAgent:
    def __init__(self, vectorizer, tfidf_matrix, chunks):
        self.vectorizer = vectorizer
        self.tfidf_matrix = tfidf_matrix
        self.chunks = chunks
        
    def get_relevant_chunks(self, question, top_k=3):
        question_vector = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vector, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices]
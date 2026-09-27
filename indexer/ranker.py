import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

class SearchEngineIndex:
    def __init__(self):
        # 1. Load a lightweight, high-performance Transformer model
        # This converts any text into a 384-dimensional vector (array of numbers)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Initialize the FAISS index for fast nearest-neighbor search
        # 384 is the exact dimension output of our specific MiniLM model
        self.index = faiss.IndexFlatL2(384)
        
        # Dictionary to map FAISS internal IDs back to our crawled URLs
        self.doc_map = {} 
        self.doc_counter = 0

    def add_document(self, url: str, text: str):
        """Converts webpage text into an AI embedding and stores it."""
        if not text:
            return
            
        # Convert text to a vector of 32-bit floats (required by FAISS)
        vector = self.model.encode([text]).astype('float32')
        
        # Add the vector to the FAISS database
        self.index.add(vector)
        
        # Save the URL so we can retrieve it later
        self.doc_map[self.doc_counter] = url
        self.doc_counter += 1

    def search(self, query: str, top_k: int = 5):
        """Searches the vector database for conceptual matches."""
        if self.doc_counter == 0:
            return []
        
        # Convert the user's search query into its own vector
        query_vector = self.model.encode([query]).astype('float32')
        
        # FAISS calculates the mathematical distance between the query vector 
        # and every website vector in the index.
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:  # FAISS returns -1 if it runs out of results
                # Convert the L2 distance into a similarity score (closer to 1 = better match)
                similarity_score = round(float(1 / (1 + distances[0][i])), 4)
                
                results.append({
                    "url": self.doc_map[idx],
                    "score": similarity_score
                })
                
        return results
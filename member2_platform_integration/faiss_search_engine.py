import numpy as np

# A mock version of FAISS since we're generating the scaffold for the user.
# In production, `import faiss` is required.
class FaissSearchEngine:
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
        self.index = None
        self.mapping = {}  # index -> str(user_id)
        # Assuming 512 embedding size output from FaceNet
        self.dimension = 512
        self.mock_vectors = None

    def build_index(self, embeddings: dict):
        """
        Builds the memory index using vector embeddings.
        Input format: { 'user_uuid': [ 0.1, 0.4, ... 512 dims ] }
        """
        # We try to import faiss here so the rest of the application doesn't crash if faiss isn't installed natively
        try:
            import faiss
            self.index = faiss.IndexFlatIP(self.dimension)
            
            # Convert dictionaries into a matrix
            if not embeddings:
                return
                
            vectors = []
            for i, (user_id, vec) in enumerate(embeddings.items()):
                self.mapping[i] = user_id
                vectors.append(vec)
                
            # L2 normalization for cosine similarity
            mat = np.array(vectors).astype('float32')
            faiss.normalize_L2(mat)
            self.index.add(mat)
            print(f"FAISS index built successfully with {len(vectors)} embeddings.")
            
        except ImportError:
            print("FAISS module not installed. Using mock memory search.")
            self.index = "mock"
            self.mapping = {i: user_id for i, user_id in enumerate(embeddings.keys())}
            self.mock_vectors = np.array(list(embeddings.values()))

    def search(self, target_embedding: list, top_k: int = 1) -> dict:
        """
        Searches the stored FAISS index for the target face embedding vector.
        """
        if self.index is None:
            return {"match_found": False}
            
        vec = np.array([target_embedding]).astype('float32')
        
        try:
            import faiss
            faiss.normalize_L2(vec)
            distances, indices = self.index.search(vec, top_k)
            
            best_dist = distances[0][0]
            best_idx = indices[0][0]
            
            # Assuming distance is inner product (cosine similarity) 
            if best_dist >= self.threshold and best_idx in self.mapping:
                return {
                    "match_found": True,
                    "user_id": self.mapping[best_idx],
                    "confidence": float(best_dist)
                }
        except ImportError:
            # Simple mock implementation using numpy dot product
            if self.mock_vectors is not None:
                # Calculate cosine similarity (assuming vectors are normalized)
                # or simplified dot product for the mock
                similarities = np.dot(self.mock_vectors, vec.flatten())
                best_idx = np.argmax(similarities)
                best_dist = similarities[best_idx]
                
                if best_dist >= self.threshold and best_idx in self.mapping:
                    return {
                        "match_found": True,
                        "user_id": self.mapping[best_idx],
                        "confidence": float(best_dist)
                    }
        
        return {"match_found": False}

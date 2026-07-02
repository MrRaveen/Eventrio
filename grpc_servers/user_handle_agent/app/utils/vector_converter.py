class vector_converter:
    def __init__(self):
        print("Loading SentenceTransformer model (this may take a few minutes on slow drives)...", flush=True)
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("SentenceTransformer loaded successfully!", flush=True)
        
    def convertToVector(self, text: str) -> list:
        try:
            if not text:
                return "text is none in vector converter"    
            embedding_vector = self.model.encode(text) 
            return embedding_vector.tolist()
        except Exception as e:
            print(f"Error in vector converter: {e}")
            return []

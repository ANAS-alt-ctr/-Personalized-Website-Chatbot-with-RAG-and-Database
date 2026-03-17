_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embedding(text: str):
    model = _get_model()
    embedding = model.encode(text)
    return embedding.tolist()
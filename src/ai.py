from re import S
from api.clients import qdrant_client 
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

class AIService:
    def __init__(self, model_name: str, texts: list[str]) -> None:
        self.model = SentenceTransformer(model_name)
        self.texts = texts  

    def load_dataset(self, file_path: str) -> pd.DataFrame:
        if not self.texts:
            self.texts = pd.read_csv(file_path)
        return pd.DataFrame(self.texts, columns=['title','author','description'])
    
test_service = AIService("all-MiniLM-L6-v2", [])
print(test_service.load_dataset("data/commonlit_texts.csv"))


        

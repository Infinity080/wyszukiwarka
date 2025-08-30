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
            df = pd.read_csv(file_path)
            # id
            df.reset_index(inplace=True)
            df.insert(0, 'id', df.pop('index'))

            # text
            text_columns = ["description", "excerpt", "notes"]
            df["text"] = df[text_columns].fillna("").astype(str).agg(' '.join, axis=1)
            
            # metadata
            metadata_columns = [column for column in df.columns if column not in text_columns + ["id", "text"]]
            df["metadata"] = df[metadata_columns].to_dict(orient='records')

            self.texts = df[["id", "text", "metadata"]]
        return self.texts

test_service = AIService("all-MiniLM-L6-v2", [])
print(test_service.load_dataset("data/commonlit_texts.csv"))


        

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

class AIService:
    def __init__(self, model_name: str, collection_name: str, qdrant_client: AsyncQdrantClient) -> None:
        self.model = None
        self.collection_name = collection_name
        self.texts = pd.DataFrame()
        self.qdrant_client = qdrant_client

    @classmethod
    async def create(cls, model_name: str, collection_name: str, qdrant_client: AsyncQdrantClient) -> "AIService":
        self = cls(model_name, collection_name, qdrant_client)
        self.model = SentenceTransformer(model_name)
        
        self.texts = self._load_dataset("data/commonlit_texts.csv")

        collection_info = await self.qdrant_client.get_collection(collection_name)
        if collection_info.points_count <= 0:
            embeddings = self._generate_embeddings()
            await self.save_embeddings_to_qdrant(embeddings)

        return self

    def _load_dataset(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        # id
        df.reset_index(inplace=True)
        df.insert(0, 'id', df.pop('index'))

        # text
        text_columns = ["description", "description", "intro", "excerpt", "notes"]
        df["text"] = df[text_columns].fillna("").astype(str).agg(' '.join, axis=1)
        
        # metadata
        metadata_columns = [column for column in df.columns if column not in text_columns + ["id", "text"]]
        df["metadata"] = df[metadata_columns].to_dict(orient='records')

        return df[["id", "text", "metadata"]]

    def _generate_embeddings(self) -> np.ndarray:
        embeddings = self.model.encode(self.texts["text"].tolist())
        return embeddings 

    async def save_embeddings_to_qdrant(self, embeddings: np.ndarray) -> None:
        points = []
        for row, embedding in zip(self.texts.itertuples(), embeddings):
            point = {
                "id": row.id,
                "vector": embedding.tolist(),
                "payload": {"text": row.text, **row.metadata} # save text and unpacked metadata
            }
            points.append(point)
        for i in range(0, len(points), 100): # upload in batches of 100 to avoid timeouts
            batch = points[i:i + 100]
            await self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

    async def find_k_similar(self, prompt: str, k: int = 5) -> pd.DataFrame:
        prompt_embedding = self.model.encode([prompt])
        
        k_similar = await self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=prompt_embedding[0].tolist(),
            limit=k
        )

        return pd.DataFrame([
        {
            "id": item.id,
            "text": item.payload.get("text", ""),
            "score": item.score,
            **{key: value for key, value in item.payload.items()}
        } for item in k_similar ])

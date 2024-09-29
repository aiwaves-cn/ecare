from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from typing import List, Optional
from langchain_core.embeddings import Embeddings
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import math


MAX_BATCHES = 256
MAX_REQUEST_TOKENS = 200000


class JinaEmbeddings(Embeddings):
    def __init__(self, url: str, cpu: Optional[bool] = False) -> None:
        super().__init__()
        self.url = url
        self.cpu = cpu
    
    def get_batch_embedding(self, batch_texts):
        payload = {"inputs": batch_texts}
        response = requests.post(self.url, json=payload)
        if response.status_code == 200:
            return np.array(response.json())
        else:
            raise ValueError(f"Error Code {response.status_code}, {response.text}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.cpu:
            payload = {"text": texts}
            response = requests.post(self.url, json=payload)
            if response.status_code == 200:
                return np.array(response.json())
            else:
                raise ValueError(f"Error Code {response.status_code}, {response.text}")
        else:
            length_per_batch = max([len(text) for text in texts])
            num_batch = min(MAX_BATCHES, MAX_REQUEST_TOKENS//length_per_batch)
            batches = math.ceil(len(texts) / num_batch)
            _results = [None] * batches
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_map = {
                    executor.submit(self.get_batch_embedding, texts[i * num_batch: (i+ 1) * num_batch] ): i
                    for i in range(batches)
                }
                for future in as_completed(future_map):
                    index = future_map[future]
                    _results[index] = future.result()
            results = np.concatenate(_results, axis=0)
            return results
        
    def embed_query(self, text: str) -> List[float]:   
        return self.embed_documents([text])[0]
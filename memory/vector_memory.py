"""Deprecated implementation retained as an inert compatibility tombstone.

import os
from pathlib import Path


# ==============================
# 必须在 import chromadb 前设置
# ==============================

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["DISABLE_TELEMETRY"] = "true"

# 禁止 posthog
os.environ["POSTHOG_DISABLED"] = "true"


import logging

logging.getLogger("chromadb").setLevel(logging.CRITICAL)
logging.getLogger("posthog").setLevel(logging.CRITICAL)


# Legacy implementation below is intentionally not initialized. Importing Chroma is
# deferred to memory.chroma_store.VectorMemory to keep application startup fast.
import time
import threading

from app.config import MEMORY_PATH
from app.llm_service import OllamaServiceError, embedding as llm_embedding


VECTOR_STORE_PATH = MEMORY_PATH / "vector_store"


class _LegacyVectorMemory:


    def __init__(self):


        self.client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_PATH),
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )


        self.collection = self.client.get_or_create_collection(
            name="chat_memory",
            embedding_function=None
        )

        self._embedding_cache = {}
        self._embedding_lock = threading.Lock()



    def embedding(self,text):


        with self._embedding_lock:

            if text in self._embedding_cache:

                return self._embedding_cache[text]


        print("生成embedding:")
        print(text)


        try:
            vector = llm_embedding(text, timeout=60, model="nomic-embed-text")
        except OllamaServiceError as exc:
            print("Ollama embedding 失败:", exc)
            return []


        print(
            "embedding长度:",
            len(vector)
        )


        with self._embedding_lock:

            self._embedding_cache[text] = vector


        return vector




    def check_duplicate(
            self,
            vector,
            threshold=20
    ):


        result=self.collection.query(

            query_embeddings=[
                vector
            ],

            n_results=1

        )


        if not result["documents"][0]:

            return False



        distance=result["distances"][0][0]


        print(
            "相似距离:",
            distance
        )


        if distance < threshold:

            print(
                "发现相似记忆，跳过保存"
            )

            return True



        return False




    def add_memory(self,text):


        print("\n======添加记忆======")



        vector=self.embedding(text)



        if self.check_duplicate(vector):

            return



        memory_id=str(time.time())



        print(
            "写入Chroma"
        )



        self.collection.add(

            ids=[
                memory_id
            ],


            embeddings=[
                vector
            ],


            documents=[
                text
            ]

        )


        print(
            "保存成功"
        )




    def search(
            self,
            query,
            limit=3
    ):


        print(
            "\n======搜索记忆======"
        )


        vector=self.embedding(query)



        result=self.collection.query(

            query_embeddings=[
                vector
            ],

            n_results=limit

        )


        return result["documents"][0]



    def count_memory(self):


        return self.collection.count()


"""

from memory.chroma_store import VECTOR_STORE_PATH, VectorMemory

__all__ = ["VECTOR_STORE_PATH", "VectorMemory"]

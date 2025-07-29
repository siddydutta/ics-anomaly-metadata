import json
import os

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

DOCUMENTS_FILE = "documents.json"
EMBEDDING_MODEL = "text-embedding-ada-002"

client = chromadb.CloudClient(
    api_key=os.getenv("CHROMADB_KEY"),
    tenant=os.getenv("CHROMADB_TENANT"),
    database=os.getenv("CHROMADB_DATABASE"),
)

collection = client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_EMBEDDING_KEY"),
        model_name=EMBEDDING_MODEL,
    ),
)

with open(DOCUMENTS_FILE, "r") as file:
    documents = json.load(file)

ids = [doc["id"] for doc in documents]
texts = [doc["text"] for doc in documents]
metadatas = []
for doc in documents:
    metadata = doc.get("metadata", {})
    # Remove keys with value None
    cleaned_metadata = {k: v for k, v in metadata.items() if v is not None}
    metadatas.append(cleaned_metadata)

BATCH_SIZE = 50
for i in tqdm(
    range(0, len(documents), BATCH_SIZE), desc="Persisting embeddings", unit="batch"
):
    collection.add(
        ids=ids[i : i + BATCH_SIZE],
        documents=texts[i : i + BATCH_SIZE],
        metadatas=metadatas[i : i + BATCH_SIZE],
    )

import json
import os

from dotenv import load_dotenv
from llama_cloud import PipelineCreate, PipelineMetadataConfig
from llama_cloud.client import LlamaCloud
from llama_cloud.types import CloudDocumentCreate
from llama_cloud.types.advanced_mode_transform_config_segmentation_config import (
    AdvancedModeTransformConfigSegmentationConfig_Page,
)
from llama_cloud.types.open_ai_embedding import OpenAiEmbedding
from llama_cloud.types.pipeline_create_embedding_config import (
    PipelineCreateEmbeddingConfig_OpenaiEmbedding,
)
from llama_cloud.types.pipeline_create_transform_config import AutoTransformConfig
from tqdm import tqdm

load_dotenv()


PIPELINE_NAME = "ICS Knowledge Base"
DOCUMENTS_FILE = "documents.json"
EMBEDDING_MODEL = "text-embedding-ada-002"

EMBEDDING_CONFIG = PipelineCreateEmbeddingConfig_OpenaiEmbedding(
    type="OPENAI_EMBEDDING",
    component=OpenAiEmbedding(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=EMBEDDING_MODEL,
    ),
)

TRANSFORM_CONFIG = AutoTransformConfig(
    segmentation_config=AdvancedModeTransformConfigSegmentationConfig_Page(mode="page"),
    chunking_config=None,
)

METADATA_CONFIG = PipelineMetadataConfig(
    excluded_embed_metadata_keys=["pipeline_id", "document_id"],
    excluded_llm_metadata_keys=["pipeline_id", "document_id"],
)

client = LlamaCloud(token=os.getenv("LLAMA_CLOUD_API_KEY"))

pipeline_request = PipelineCreate(
    name=PIPELINE_NAME,
    embedding_config=EMBEDDING_CONFIG,
    transform_config=TRANSFORM_CONFIG,
    metadata_config=METADATA_CONFIG,
)
pipeline = client.pipelines.upsert_pipeline(request=pipeline_request)


with open(DOCUMENTS_FILE, "r") as file:
    raw_documents = json.load(file)


BATCH_SIZE = 50
for i in tqdm(
    range(0, len(raw_documents), BATCH_SIZE), desc="Uploading documents", unit="batch"
):
    documents = []
    for doc in raw_documents[i : i + BATCH_SIZE]:
        cleaned_metadata = {
            k: v for k, v in doc.get("metadata", {}).items() if v is not None
        }
        document = CloudDocumentCreate(
            id=doc["id"],
            text=doc["text"],
            metadata=cleaned_metadata,
        )
        documents.append(document)
    client.pipelines.create_batch_pipeline_documents(
        pipeline_id=pipeline.id, request=documents
    )

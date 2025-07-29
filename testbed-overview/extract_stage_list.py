import json
import sys

from dotenv import load_dotenv
from llama_cloud import DocumentChunkMode, ExtractRun, StatusEnum
from llama_cloud_services import LlamaExtract
from llama_cloud_services.extract import (
    ExtractConfig,
    ExtractionAgent,
    ExtractMode,
    ExtractTarget,
    SourceText,
)
from stage_schema import StageSchema

load_dotenv()

FILENAME = "SWaT_technical_details-051018-v4.2.pdf"
AGENT_NAME = "Stage List Extractor"
PROMPT = """You are an ICS technical document reader.
Extract all six stages, their descriptions, and components from the document, based on the provided schema.
"""

CONFIG = ExtractConfig(
    priority=None,
    extraction_target=ExtractTarget.PER_PAGE,
    extraction_mode=ExtractMode.PREMIUM,
    multimodal_fast_mode=False,
    system_prompt=PROMPT,
    use_reasoning=True,
    cite_sources=True,
    confidence_scores=False,
    chunk_mode=DocumentChunkMode.PAGE,
    high_resolution_mode=True,
    invalidate_cache=True,
    # page_range="2-3",
)


def handle_extraction_job(extraction_job: ExtractRun):
    print("Job ID:", extraction_job.job_id)
    if extraction_job.status == StatusEnum.SUCCESS:
        with open("testbed-stages.json", "w") as f:
            json.dump(extraction_job.data, f, indent=2)
    else:
        print(f"Extraction job failed with status: {extraction_job.status}")
        if extraction_job.error:
            print(f"Error: {extraction_job.error}")


def main():
    job_id = sys.argv[1] if len(sys.argv) > 1 else None
    extractor = LlamaExtract()
    agent: ExtractionAgent = (
        extractor.get_agent(AGENT_NAME)
        if job_id
        else extractor.create_agent(AGENT_NAME, config=CONFIG, data_schema=StageSchema)
    )
    if job_id:
        extraction_job = agent.get_extraction_run_for_job(job_id)
        handle_extraction_job(extraction_job)
    else:
        with open(FILENAME, "rb") as file:
            file_content = file.read()
        extraction_job = agent.extract(SourceText(file=file_content, filename=FILENAME))
        handle_extraction_job(extraction_job)


if __name__ == "__main__":
    main()

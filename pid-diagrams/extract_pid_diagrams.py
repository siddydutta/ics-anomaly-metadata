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
from pid_schema import PIDSchemaRoot

load_dotenv()

FILENAME = "SWaT_technical_details-051018-v4.2.pdf"
AGENT_NAME = "PID List Extractor"

PROMPT = """You are an ICS P&ID reader. 
Extract the P&ID components stage-wise and their connections from the document. Each component should have a unique identifier (e.g., MV-101) and a list of connections to other components.
The connections should specify the target component and the media used for the connection if applicable.
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
    invalidate_cache=False,
    page_range="5-8",
)


def handle_extraction_job(extraction_job: ExtractRun):
    print("Job ID:", extraction_job.job_id)
    if extraction_job.status == StatusEnum.SUCCESS:
        with open("pid-components.json", "w") as f:
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
        else extractor.create_agent(
            AGENT_NAME, config=CONFIG, data_schema=PIDSchemaRoot
        )
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

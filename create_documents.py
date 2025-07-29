import json
import uuid

from pydantic import ValidationError
from tqdm import tqdm

from document_schema import DocTypeEnum, Document, Metadata, SourceEnum, TacticEnum

DOCUMENTS = []
OUTPUT_FILE = "documents.json"

# Create attack_technique documents
ATTACK_TECHNIQUES_JSON = "attack-techniques/attack-techniques.json"
with open(ATTACK_TECHNIQUES_JSON, "r") as f:
    attack_techniques = json.load(f)

for technique in tqdm(
    attack_techniques, desc="Creating attack technique documents", unit="documents"
):
    text = f"Name: {technique['name']}"
    text += f"\nDescription: {technique['description']}"
    if technique.get("detections"):
        text += f"\nDetection: {', '.join(technique['detections'])}"
    if technique.get("mitigations"):
        text += f"\nMitigation: {', '.join(technique['mitigations'])}"
    for tactic in technique["tactics"]:
        document = Document(
            id=str(uuid.uuid4()),
            text=text,
            metadata=Metadata(
                source=SourceEnum.MITRE_ICS,
                doc_type=DocTypeEnum.ATTACK_TECHNIQUE,
                technique_id=technique["technique_id"],
                tactic=TacticEnum(tactic),
            ),
        )
        DOCUMENTS.append(document)


# Create component documents
COMPONENTS_JSON = "equipment-list/equipment-list.json"
with open(COMPONENTS_JSON, "r") as f:
    raw_data = json.load(f)
    component_list = [item for data in raw_data for item in data["equipment_lists"]]

for stage_components in tqdm(
    component_list, desc="Creating component documents", unit="stages"
):
    for component in stage_components["equipments"]:
        if not component.get("remarks"):
            continue
        text = f"Component: {component['remarks']}"
        text += f"\nDescription: {component['description']}"
        text += f"\nDesign Specification: {component['design_specification']}"
        text += f"\nMaterial: {component['material']}"
        text += f"\nBrand Model: {component['brand_model']}"
        try:
            document = Document(
                id=str(uuid.uuid4()),
                text=text,
                metadata=Metadata(
                    source=SourceEnum.SWAT_DOC,
                    doc_type=DocTypeEnum.COMPONENT,
                    component_id=component["remarks"],
                    stage_id=stage_components["stage"],
                ),
            )
            DOCUMENTS.append(document)
        except ValidationError:
            print(f"Validation error for component: {component}")
            continue

# Create pid documents
PID_JSON = "pid-diagrams/pid-components.json"
with open(PID_JSON, "r") as f:
    stage_pid_data = json.load(f)
for stage in tqdm(
    stage_pid_data["stages"], desc="Creating PID documents", unit="stages"
):
    for component in stage["components"]:
        text = f"Component: {component['component_id']}\nConnects to: {', '.join(component['connections'])}"
        try:
            document = Document(
                id=str(uuid.uuid4()),
                text=text,
                metadata=Metadata(
                    source=SourceEnum.SWAT_DOC,
                    doc_type=DocTypeEnum.PID,
                    component_id=component["component_id"],
                    stage_id=stage["stage_id"],
                ),
            )
            DOCUMENTS.append(document)
        except ValidationError as error:
            print(f"Validation error for PID component: {component}")
            raise error


# Create stage documents
STAGES_JSON = "testbed-overview/testbed-stages.json"
with open(STAGES_JSON, "r") as f:
    stages_data = json.load(f)
for stage in tqdm(stages_data, desc="Creating stage documents", unit="stages"):
    text = f"Stage: {stage['stage_id']}\nName: {stage['stage_name']}\nDescription: {stage['description']}"
    if stage.get("components"):
        text += "\nComponents:\n"
        for component in stage["components"]:
            text += f"- {component['component_id']} ({component['role']})\n"
    try:
        document = Document(
            id=str(uuid.uuid4()),
            text=text,
            metadata=Metadata(
                source=SourceEnum.SWAT_DOC,
                doc_type=DocTypeEnum.STAGE,
                stage_id=stage["stage_id"],
            ),
        )
        DOCUMENTS.append(document)
    except ValidationError:
        print(f"Validation error for stage: {stage}")
        continue

with open(OUTPUT_FILE, "w") as f:
    json.dump([doc.model_dump() for doc in DOCUMENTS], f, indent=2)

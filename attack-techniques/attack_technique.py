from pydantic import BaseModel, HttpUrl


class AttackTechnique(BaseModel):
    technique_id: str
    name: str
    description: str
    tactics: list[str]
    detections: list[str]
    mitigations: list[str]
    url: HttpUrl

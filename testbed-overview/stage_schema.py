from pydantic import BaseModel, Field


class StageComponent(BaseModel):
    component_id: str = Field(
        ...,
        description="Unique identifier for the component (e.g., T101, MV101, LIT101).",
    )
    role: str = Field(
        ...,
        description="Role or function of the component (e.g., storage tank, inlet control valve, level sensor).",
    )


class StageSchema(BaseModel):
    stage_id: str = Field(
        ..., description="Identifier for the stage (e.g., P1, P2, P3, P4, P5, P6)."
    )
    stage_name: str = Field(..., description="Human-readable name of the stage.")
    description: str = Field(
        ..., description="Description of the stage and its function."
    )
    components: list[StageComponent] = Field(
        ..., description="List of components in this stage."
    )

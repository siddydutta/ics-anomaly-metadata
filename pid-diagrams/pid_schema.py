from typing import Optional

from pydantic import BaseModel, Field


class Connection(BaseModel):
    from_: str = Field(..., alias="from", description="Component ID of the source.")
    to: str = Field(..., description="Component ID of the destination.")
    via: str = Field(
        ...,
        description="Description of the connection medium (e.g., pipe, tube, wire).",
    )


class PIDComponent(BaseModel):
    component_id: str = Field(
        ..., description="Unique identifier for the component (e.g., P-101, LIT-101)."
    )
    connections: Optional[list[Connection]] = Field(
        None, description="List of connections for the component."
    )


class Stage(BaseModel):
    stage_id: str = Field(
        ..., description="Name or identifier of the stage (e.g., P1, Raw Water)."
    )
    components: Optional[list[PIDComponent]] = Field(
        None, description="List of components in this stage."
    )


class PIDSchemaRoot(BaseModel):
    stages: list[Stage] = Field(
        ..., description="List of stages in the water treatment process."
    )

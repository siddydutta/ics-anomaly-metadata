from typing import Optional

from pydantic import BaseModel, Field


class EquipmentItem(BaseModel):
    description: str = Field(
        ..., description="Description of the equipment from the table."
    )
    design_specification: Optional[str] = Field(
        None, description="Design specification of the equipment."
    )
    material: Optional[str] = Field(None, description="Material of the equipment.")
    quantity: Optional[str] = Field(None, description="Quantity of the equipment.")
    brand_model: Optional[str] = Field(
        None, description="Brand and model of the equipment."
    )
    remarks: Optional[str] = Field(
        None, description="Component ID or any remarks about the equipment."
    )
    type: str = Field(..., description="Type of equipment: sensor, actuator")


class EquipmentList(BaseModel):
    stage: str = Field(
        ..., description="Identifier for the stage (e.g., 'P1', 'P2', 'P3')."
    )
    equipments: list[EquipmentItem] = Field(
        ..., description="Array of equipment items in this stage."
    )


class EquipmentListsRoot(BaseModel):
    equipment_lists: list[EquipmentList] = Field(
        ..., description="Array of equipment lists for different stages."
    )

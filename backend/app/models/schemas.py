from pydantic import BaseModel
from typing import Optional, Union

class EquipmentItem(BaseModel):
    equipment_tag: Optional[str] = None
    equipment_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    quantity: Optional[Union[str, int]] = None
    capacity: Optional[str] = None
    voltage: Optional[str] = None
    source_page: Optional[int] = None
    low_confidence: Optional[bool] = False
    confidence_score: Optional[float] = None

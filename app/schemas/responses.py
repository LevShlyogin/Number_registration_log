from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .equipment import EquipmentOut
from .users import UserInResponse


class CreatedDocumentInfo(BaseModel):
    id: int
    numeric: int
    formatted_no: str
    doc_name: str
    note: str | None
    reg_date: datetime
    equipment: EquipmentOut
    user: UserInResponse

    model_config = ConfigDict(from_attributes=True)


class AssignNumberOut(BaseModel):
    created: CreatedDocumentInfo
    message: str

from pydantic import BaseModel
from typing import Optional, List

class CurriculumBase(BaseModel):
    title: str
    parent_id: Optional[int] = None

class CurriculumCreate(CurriculumBase):
    pass

class CurriculumRead(CurriculumBase):
    id: int
    children: List['CurriculumRead'] = []

    model_config = {"from_attributes": True}

CurriculumRead.model_rebuild()

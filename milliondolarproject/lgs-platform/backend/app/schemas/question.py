from pydantic import BaseModel
from typing import Optional

class QuestionBase(BaseModel):
    text: str
    choice_a: Optional[str] = None
    choice_b: Optional[str] = None
    choice_c: Optional[str] = None
    choice_d: Optional[str] = None
    correct_choice: Optional[str] = None
    curriculum_id: Optional[int] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int

    model_config = {"from_attributes": True}

from pydantic import BaseModel
from typing import Optional


class CreateModuleRequest(BaseModel):
    title: str
    description: Optional[str] = None


class UpdateModuleRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

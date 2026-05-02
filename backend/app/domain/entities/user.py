from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal


class User(BaseModel):
    id: Optional[str] = None
    email: str
    name: str
    role: Literal["admin", "user"] = "user"
    picture: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

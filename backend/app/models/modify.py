from pydantic import BaseModel


class ModifyRequest(BaseModel):
    message: str
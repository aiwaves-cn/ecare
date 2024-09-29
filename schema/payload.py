from pydantic import BaseModel, Field

class TextPayload(BaseModel):
    sn: int = Field(description="序列号", default=0)
    text: str = Field(description="")
    
from pydantic import BaseModel, Field
from typing import List


class ChatRequest(BaseModel):
    message:    str = Field(..., min_length=1, max_length=2000)
    website_id: str = Field(..., description="Routes to correct knowledge collection")
    session_id: str = Field(..., description="Tracks conversation across turns")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message":    "What services do you offer?",
                "website_id": "crushaders_tech",
                "session_id": "sess-1750000000000"
            }
        }
    }


class ChatResponse(BaseModel):
    reply:   str       = Field(..., description="Assistant response text")
    sources: List[str] = Field(default_factory=list,
                               description="Source URLs — empty in Phase 1, populated in Phase 2")

    model_config = {
        "json_schema_extra": {
            "example": {
                "reply":   "Crushaders Tech offers 7 core digital marketing services...",
                "sources": []
            }
        }
    }
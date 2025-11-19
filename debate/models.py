from pydantic import BaseModel, Field
from typing import Optional, List


class DebateRequest(BaseModel):
    topic: str = Field(..., description="Debate topic provided by the user")
    enable_rebuttals: bool = Field(default=True, description="Include rebuttal rounds")
    rounds: int = Field(default=1, ge=0, le=5, description="Number of rebuttal rounds (per side)")


class Argument(BaseModel):
    stance: str
    content: str


class Rebuttal(BaseModel):
    from_debater: str
    content: str


class DebateResult(BaseModel):
    topic: str
    stance_a: str
    stance_b: str
    arguments_a: List[Argument]
    arguments_b: List[Argument]
    rebuttals_a: List[Rebuttal] = []
    rebuttals_b: List[Rebuttal] = []
    verdict: Optional[str] = None
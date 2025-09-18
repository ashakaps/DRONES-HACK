
from pydantic import BaseModel
from typing import Any, Dict

class UiEvent(BaseModel):
    context_id: str
    kind: str
    payload: Dict[str, Any]

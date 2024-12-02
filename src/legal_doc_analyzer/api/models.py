from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchQuery(BaseModel):
    query: str
    document_type: Optional[str] = None
    limit: Optional[int] = 5

class SearchResponse(BaseModel):
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]

class AnalysisResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
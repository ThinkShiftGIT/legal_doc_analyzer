from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from legal_doc_analyzer.chunkers.base_chunker import BaseChunk

class SearchResult(BaseModel):
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]

class MockStore:
    def __init__(self):
        self.documents = {}
        
    def add_document(self, chunk: BaseChunk) -> str:
        doc_id = str(len(self.documents))
        self.documents[doc_id] = chunk
        return doc_id

    def search(self, query: str, document_type: Optional[str] = None, limit: int = 5) -> List[SearchResult]:
        results = []
        for doc_id, chunk in self.documents.items():
            if document_type and chunk.metadata.get("document_type") != document_type:
                continue
            results.append(
                SearchResult(
                    id=doc_id,
                    content=chunk.content,
                    score=1.0,
                    metadata=chunk.metadata
                )
            )
        return results[:limit]
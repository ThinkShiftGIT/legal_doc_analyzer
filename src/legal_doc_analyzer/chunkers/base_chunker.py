from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar

T = TypeVar('T')

class BaseChunk(Generic[T]):
    def __init__(self, content: T, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
        self.vector = None
        
    def __len__(self):
        return len(str(self.content).strip())

class BaseChunker(ABC):
    def __init__(self, min_chunk_size: int = 10, overlap: int = 2):
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap

    @abstractmethod
    def create_chunks(self, content: Any) -> List[BaseChunk]:
        pass

    def _validate_chunk(self, chunk: BaseChunk) -> bool:
        return len(chunk) >= self.min_chunk_size
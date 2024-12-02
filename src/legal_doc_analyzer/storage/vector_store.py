from typing import Optional, List, Dict, Any
import logging
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from .base import BaseChunk, SearchResult

logger = logging.getLogger(__name__)

class ChromaStore:
    """Vector store implementation using ChromaDB through LangChain."""
    
    def __init__(self,
                persist_directory: str = "./chroma_db",
                embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize ChromaDB instance.
        
        Args:
            persist_directory: Directory to persist vector store
            embedding_model: Name of the sentence transformer model to use
        """
        try:
            # Initialize embeddings
            self.embedding_model = SentenceTransformerEmbeddings(model_name=embedding_model)
            
            # Ensure persist directory exists
            os.makedirs(persist_directory, exist_ok=True)
            
            # Initialize ChromaDB through LangChain
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embedding_model,
                collection_name="legal_documents"
            )
            
            logger.info(f"Successfully initialized ChromaDB at {persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise ConnectionError(f"Could not initialize ChromaDB: {str(e)}")
    
    def add_document(self, chunk: BaseChunk) -> str:
        """Add a single document chunk to the vector store"""
        try:
            metadata = {
                "document_type": chunk.metadata.get("document_type"),
                "page_number": chunk.metadata.get("page_number"),
                "timestamp": chunk.metadata.get("timestamp", 0.0),
                "source_file": chunk.metadata.get("source_file"),
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "language": chunk.metadata.get("language", "en")
            }
            
            return self.add_texts([chunk.content], [metadata])[0]
            
        except Exception as e:
            logger.error(f"Failed to add document to ChromaDB: {str(e)}")
            raise
            
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Add multiple texts with metadata to the vector store.
        
        Args:
            texts: List of text content to add
            metadatas: Optional list of metadata dictionaries for each text
            
        Returns:
            List of document IDs
        """
        try:
            return self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            logger.error(f"Failed to add texts to ChromaDB: {str(e)}")
            raise
            
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for documents similar to the query text.
        
        Args:
            query: Text to search for
            k: Number of results to return
            
        Returns:
            List of documents with their content and metadata
        """
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise

    def batch_add_documents(self, chunks: List[BaseChunk], batch_size: int = 100) -> None:
        """Add multiple document chunks in batch"""
        try:
            texts = []
            metadatas = []
            
            for chunk in chunks:
                texts.append(chunk.content)
                metadatas.append({
                    "document_type": chunk.metadata.get("document_type"),
                    "page_number": chunk.metadata.get("page_number"),
                    "timestamp": chunk.metadata.get("timestamp", 0.0),
                    "source_file": chunk.metadata.get("source_file"),
                    "chunk_index": chunk.metadata.get("chunk_index", 0),
                    "language": chunk.metadata.get("language", "en")
                })
            
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(chunks)} documents in batch")
            
        except Exception as e:
            logger.error(f"Error in batch operation: {str(e)}")
            raise

    def search(self, 
              query: str, 
              document_type: Optional[str] = None,
              limit: int = 5) -> List[SearchResult]:
        """Search for similar documents"""
        try:
            filter_dict = {"document_type": document_type} if document_type else None
            
            docs_and_scores = self.vectorstore.similarity_search_with_score(
                query=query,
                k=limit,
                filter=filter_dict
            )
            
            results = []
            for doc, score in docs_and_scores:
                results.append(
                    SearchResult(
                        id=doc.metadata.get("id", ""),
                        content=doc.page_content,
                        score=float(score),
                        metadata={
                            "document_type": doc.metadata.get("document_type"),
                            "page_number": doc.metadata.get("page_number"),
                            "source_file": doc.metadata.get("source_file"),
                            "language": doc.metadata.get("language")
                        }
                    )
                )
            logger.debug(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID"""
        try:
            results = self.vectorstore.get(
                ids=[document_id]
            )
            
            if results and results['documents']:
                doc = results['documents'][0]
                metadata = results['metadatas'][0]
                return {
                    "content": doc,
                    "metadata": {
                        "document_type": metadata.get("document_type"),
                        "page_number": metadata.get("page_number"),
                        "source_file": metadata.get("source_file"),
                        "language": metadata.get("language")
                    }
                }
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
        return None

    def delete_document(self, document_id: str) -> None:
        """Delete a document by ID"""
        try:
            self.vectorstore.delete(
                ids=[document_id]
            )
            logger.info(f"Successfully deleted document {document_id}")
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise
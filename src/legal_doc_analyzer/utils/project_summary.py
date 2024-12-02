from pathlib import Path
import inspect
import importlib
from typing import Dict, List
from datetime import datetime

class ProjectSummarizer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules = {}
        self.api_endpoints = []
        self.dependencies = {}
        
    def analyze_project(self) -> Dict:
        """Analyze the entire project structure and components"""
        return {
            "project_name": "Legal Document Analysis System",
            "timestamp": datetime.now().isoformat(),
            "architecture": self._get_architecture(),
            "components": self._get_components(),
            "api_endpoints": self._get_api_endpoints(),
            "dependencies": self._get_dependencies(),
            "capabilities": self._get_capabilities()
        }
        
    def _get_architecture(self) -> Dict:
        return {
            "storage": {
                "type": "Vector Database",
                "implementation": "Weaviate",
                "features": [
                    "Document storage with vector embeddings",
                    "Semantic search capabilities",
                    "Multi-modal content support"
                ]
            },
            "processors": {
                "document_types": ["PDF", "Audio", "Video"],
                "features": [
                    "Content extraction",
                    "Chunk generation",
                    "Metadata extraction"
                ]
            },
            "ai_integration": {
                "embedding_model": "all-MiniLM-L6-v2",
                "llm_model": "Mistral AI",
                "capabilities": [
                    "Document analysis",
                    "Summarization",
                    "Question answering",
                    "Key point extraction"
                ]
            }
        }
        
    def _get_components(self) -> Dict:
        return {
            "processors": {
                "PDFProcessor": "Handles PDF document processing and text extraction",
                "AudioProcessor": "Processes audio files and transcriptions",
                "VideoProcessor": "Handles video content and metadata extraction"
            },
            "storage": {
                "WeaviateStore": "Vector database integration for document storage and retrieval",
                "Capabilities": [
                    "Vector similarity search",
                    "Document metadata storage",
                    "Batch document processing"
                ]
            },
            "services": {
                "MistralService": "AI-powered document analysis and interaction",
                "Features": [
                    "Document analysis",
                    "Content summarization",
                    "Question answering",
                    "Key point extraction"
                ]
            }
        }
        
    def _get_api_endpoints(self) -> List[Dict]:
        return [
            {
                "path": "/documents/upload",
                "method": "POST",
                "description": "Upload and process new documents",
                "supported_types": ["pdf", "audio", "video"]
            },
            {
                "path": "/documents/search",
                "method": "POST",
                "description": "Search through processed documents",
                "features": ["semantic search", "filtering"]
            },
            {
                "path": "/documents/analyze",
                "method": "POST",
                "description": "Analyze document content with specific queries"
            },
            {
                "path": "/documents/summarize/{document_id}",
                "method": "POST",
                "description": "Generate document summaries"
            },
            {
                "path": "/documents/key-points/{document_id}",
                "method": "POST",
                "description": "Extract key points from documents"
            },
            {
                "path": "/documents/qa",
                "method": "POST",
                "description": "Answer questions about documents"
            }
        ]
        
    def _get_dependencies(self) -> Dict:
        try:
            import toml
            with open(self.project_root / "pyproject.toml") as f:
                pyproject = toml.load(f)
                return pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})
        except Exception:
            return {}
            
    def _get_capabilities(self) -> Dict:
        return {
            "document_processing": {
                "supported_formats": ["PDF", "Audio", "Video"],
                "features": [
                    "Text extraction",
                    "Layout preservation",
                    "Metadata extraction",
                    "Audio transcription",
                    "Video content analysis"
                ]
            },
            "search_capabilities": {
                "methods": [
                    "Semantic search",
                    "Keyword search",
                    "Metadata filtering"
                ],
                "features": [
                    "Cross-document search",
                    "Multi-modal search",
                    "Relevance ranking"
                ]
            },
            "ai_features": {
                "analysis": [
                    "Document summarization",
                    "Key point extraction",
                    "Question answering",
                    "Content analysis"
                ],
                "models": {
                    "embedding": "all-MiniLM-L6-v2",
                    "llm": "Mistral AI"
                }
            }
        }

    def generate_summary(self) -> str:
        """Generate a formatted summary of the project"""
        analysis = self.analyze_project()
        
        summary = [
            f"# {analysis['project_name']} - Project Summary",
            f"Generated on: {analysis['timestamp']}",
            "\n## Project Architecture",
            self._format_dict(analysis['architecture']),
            "\n## Components",
            self._format_dict(analysis['components']),
            "\n## API Endpoints",
            self._format_endpoints(analysis['api_endpoints']),
            "\n## System Capabilities",
            self._format_dict(analysis['capabilities']),
            "\n## Dependencies",
            self._format_dict(analysis['dependencies'])
        ]
        
        return "\n".join(summary)
    
    def _format_dict(self, d: Dict, indent: int = 0) -> str:
        """Format dictionary into readable string"""
        lines = []
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append("  " * indent + f"- {key}:")
                lines.append(self._format_dict(value, indent + 1))
            elif isinstance(value, list):
                lines.append("  " * indent + f"- {key}:")
                for item in value:
                    lines.append("  " * (indent + 1) + f"- {item}")
            else:
                lines.append("  " * indent + f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_endpoints(self, endpoints: List[Dict]) -> str:
        """Format API endpoints into readable string"""
        lines = []
        for endpoint in endpoints:
            lines.append(f"- {endpoint['method']} {endpoint['path']}")
            lines.append(f"  Description: {endpoint['description']}")
            for key, value in endpoint.items():
                if key not in ['method', 'path', 'description']:
                    if isinstance(value, list):
                        lines.append(f"  {key}:")
                        for item in value:
                            lines.append(f"    - {item}")
                    else:
                        lines.append(f"  {key}: {value}")
        return "\n".join(lines)
"""
MistralService: Handles interactions with the Mistral AI API for document analysis.
Provides comprehensive legal document analysis capabilities including:
- Document analysis and summarization
- Legal citation extraction
- Contract clause analysis
- Risk assessment
- Document classification
- Party identification
"""

from typing import List, Dict, Any, Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import json
from logging import getLogger
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

# Configure logging
logger = getLogger(__name__)

class MistralService:
    """Service class for interacting with Mistral AI API for legal document analysis."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-medium"):
        """
        Initialize the Mistral service.
        
        Args:
            api_key: Optional API key. If not provided, will look for MISTRAL_API_KEY in environment
            model: Model to use for analysis. Defaults to "mistral-medium"
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set MISTRAL_API_KEY environment variable or provide it directly.")
        
        try:
            self.client = MistralClient(api_key=self.api_key)
            self.model = model
            logger.info(f"Initialized MistralService with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {str(e)}")
            raise

    def _create_messages(self, system_content: str, user_content: str) -> List[Dict[str, str]]:
        """
        Create properly formatted chat messages.
        
        Args:
            system_content: System role message content
            user_content: User role message content
            
        Returns:
            List of message dictionaries
        """
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

    async def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.1) -> str:
        """
        Make a request to the Mistral API with error handling.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens in response
            temperature: Temperature for response generation
            
        Returns:
            Response content string
        """
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in Mistral API request: {str(e)}")
            raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

    async def analyze_document(self, content: str, query: str) -> str:
        """
        Analyze document content based on a specific query.
        
        Args:
            content: Document content to analyze
            query: Specific query about the document
            
        Returns:
            Analysis result
        """
        try:
            messages = self._create_messages(
                system_content="You are a legal document analysis assistant. Analyze the provided document and answer questions about it.",
                user_content=f"Document content: {content}\n\nQuery: {query}"
            )
            return await self._make_request(messages)
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

    async def summarize_document(self, content: str) -> str:
        """
        Generate a concise summary of the document.
        
        Args:
            content: Document content to summarize
            
        Returns:
            Document summary
        """
        try:
            messages = self._create_messages(
                system_content="You are a legal document analysis assistant. Provide clear and concise summaries of legal documents.",
                user_content=f"Please summarize this legal document:\n\n{content}"
            )
            return await self._make_request(messages, max_tokens=500)
        except Exception as e:
            logger.error(f"Error summarizing document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document summarization failed: {str(e)}")

    async def extract_key_points(self, content: str) -> List[str]:
        """
        Extract key points from the document.
        
        Args:
            content: Document content to analyze
            
        Returns:
            List of key points
        """
        try:
            messages = self._create_messages(
                system_content="You are a legal document analysis assistant. Extract and list the key points from legal documents.",
                user_content=f"Extract the key points from this document:\n\n{content}"
            )
            response = await self._make_request(messages, max_tokens=500)
            return [point.strip() for point in response.split('\n') if point.strip()]
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Key point extraction failed: {str(e)}")

    async def extract_legal_citations(self, content: str) -> List[Dict[str, str]]:
        """
        Extract legal citations from the document.
        
        Args:
            content: Document content to analyze
            
        Returns:
            List of dictionaries containing citation information:
            - citation: The full citation text
            - type: Type of citation (case law, statute, regulation, etc.)
            - relevance: Brief explanation of citation's relevance
        """
        try:
            messages = self._create_messages(
                system_content="""You are a legal citation expert. Extract and analyze legal citations from documents.
                For each citation, provide:
                1. The full citation text
                2. The type of citation (case law, statute, regulation, etc.)
                3. A brief explanation of its relevance
                Format your response as a list with each citation on a new line, separated by '|' characters.""",
                user_content=f"Extract and analyze all legal citations from this document:\n\n{content}"
            )
            response = await self._make_request(messages)
            citations = []
            for line in response.split('\n'):
                if '|' in line:
                    citation, type_, relevance = [part.strip() for part in line.split('|')]
                    citations.append({
                        'citation': citation,
                        'type': type_,
                        'relevance': relevance
                    })
            return citations
        except Exception as e:
            logger.error(f"Error extracting legal citations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Citation extraction failed: {str(e)}")

    async def analyze_contract_clauses(self, content: str) -> List[Dict[str, Any]]:
        """
        Analyze contract clauses and provide insights.
        
        Args:
            content: Contract content to analyze
            
        Returns:
            List of dictionaries containing clause analysis:
            - clause: The clause text
            - type: Type of clause
            - risk_level: Risk assessment (low, medium, high)
            - comments: Analysis and potential issues
        """
        try:
            messages = self._create_messages(
                system_content="""You are a contract analysis expert. Analyze contract clauses and provide insights.
                For each significant clause:
                1. Identify the clause type
                2. Assess risk level
                3. Provide analysis and highlight potential issues
                Format your response as a list with each clause analysis on a new line, using '|' as separator.""",
                user_content=f"Analyze the clauses in this contract:\n\n{content}"
            )
            response = await self._make_request(messages, max_tokens=1500)
            analyses = []
            for line in response.split('\n'):
                if '|' in line:
                    clause, type_, risk, comments = [part.strip() for part in line.split('|')]
                    analyses.append({
                        'clause': clause,
                        'type': type_,
                        'risk_level': risk,
                        'comments': comments
                    })
            return analyses
        except Exception as e:
            logger.error(f"Error analyzing contract clauses: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Contract analysis failed: {str(e)}")

    async def assess_legal_risks(self, content: str) -> Dict[str, Any]:
        """
        Perform a comprehensive legal risk assessment of the document.
        
        Args:
            content: Document content to analyze
            
        Returns:
            Dictionary containing:
            - overall_risk_level: Overall risk assessment
            - risk_factors: List of identified risk factors
            - recommendations: List of recommendations
            - priority_issues: List of high-priority issues
        """
        try:
            messages = self._create_messages(
                system_content="""You are a legal risk assessment expert. Analyze documents for potential legal risks.
                Provide:
                1. Overall risk level (low, medium, high)
                2. Specific risk factors identified
                3. Recommendations for risk mitigation
                4. High-priority issues requiring immediate attention""",
                user_content=f"Perform a legal risk assessment of this document:\n\n{content}"
            )
            response = await self._make_request(messages)
            sections = response.split('\n\n')
            return {
                'overall_risk_level': sections[0].split(':')[1].strip(),
                'risk_factors': [factor.strip() for factor in sections[1].split('\n')[1:]],
                'recommendations': [rec.strip() for rec in sections[2].split('\n')[1:]],
                'priority_issues': [issue.strip() for issue in sections[3].split('\n')[1:]]
            }
        except Exception as e:
            logger.error(f"Error assessing legal risks: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

    async def classify_document(self, content: str) -> Dict[str, Any]:
        """
        Classify the legal document and provide detailed categorization.
        
        Args:
            content: Document content to classify
            
        Returns:
            Dictionary containing:
            - document_type: Primary document classification
            - sub_type: More specific document category
            - jurisdiction: Relevant jurisdiction
            - practice_area: Legal practice area
            - confidence: Confidence score for classification
        """
        try:
            messages = self._create_messages(
                system_content="""You are a legal document classification expert. Analyze and categorize legal documents.
                Provide:
                1. Primary document type
                2. Specific sub-type
                3. Relevant jurisdiction
                4. Legal practice area
                5. Classification confidence (0-1)
                Format as JSON-like structure.""",
                user_content=f"Classify this legal document:\n\n{content}"
            )
            response = await self._make_request(messages, max_tokens=500)
            lines = response.split('\n')
            return {
                'document_type': lines[0].split(':')[1].strip(),
                'sub_type': lines[1].split(':')[1].strip(),
                'jurisdiction': lines[2].split(':')[1].strip(),
                'practice_area': lines[3].split(':')[1].strip(),
                'confidence': float(lines[4].split(':')[1].strip())
            }
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document classification failed: {str(e)}")

    async def identify_parties(self, content: str) -> List[Dict[str, Any]]:
        """
        Identify and analyze parties mentioned in the legal document.
        
        Args:
            content: Document content to analyze
            
        Returns:
            List of dictionaries containing:
            - name: Party name
            - role: Party's role in the document
            - type: Type of party (individual, corporation, etc.)
            - obligations: Key obligations or rights
        """
        try:
            messages = self._create_messages(
                system_content="""You are a legal party analysis expert. Identify and analyze parties in legal documents.
                For each party provide:
                1. Full name/identifier
                2. Role in the document
                3. Type of party
                4. Key obligations or rights
                Format each party on a new line with '|' separators.""",
                user_content=f"Identify and analyze all parties in this document:\n\n{content}"
            )
            response = await self._make_request(messages)
            parties = []
            for line in response.split('\n'):
                if '|' in line:
                    name, role, type_, obligations = [part.strip() for part in line.split('|')]
                    parties.append({
                        'name': name,
                        'role': role,
                        'type': type_,
                        'obligations': obligations
                    })
            return parties
        except Exception as e:
            logger.error(f"Error identifying parties: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Party identification failed: {str(e)}")
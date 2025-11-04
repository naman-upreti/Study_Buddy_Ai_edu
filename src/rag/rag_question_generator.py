"""RAG Question Generator Module

Generates questions based on document content using retrieval-augmented generation.
"""

import json
from typing import Union

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import ValidationError

from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import (
    rag_mcq_prompt_template,
    rag_fill_blank_prompt_template
)
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from src.rag.retriever import DocumentRetriever
from src.rag.document_processor import DocumentProcessor


class RAGQuestionGenerator:
    """Generates questions from documents using RAG approach."""
    
    def __init__(self):
        """Initialize RAG question generator."""
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
        self.document_processor = DocumentProcessor()
        self.retriever = DocumentRetriever()
        self.logger.info("RAGQuestionGenerator initialized")
    
    def load_document(self, uploaded_file) -> str:
        """Load and process document from file upload.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            str: Processed document text
            
        Raises:
            CustomException: If document loading fails
        """
        try:
            self.logger.info(f"Loading document: {uploaded_file.name}")
            text = self.document_processor.process_file(uploaded_file)
            
            # Split into chunks
            chunks = self.document_processor.chunk_text(text)
            
            # Add to retriever
            self.retriever.add_documents(chunks)
            
            self.logger.info(f"Document loaded successfully with {len(chunks)} chunks")
            return text
        
        except CustomException:
            raise
        except Exception as e:
            error_msg = f"Failed to load document: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def _clean_json_response(self, response_text: str) -> str:
        """Extract and clean JSON from LLM response."""
        response_text = response_text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        return response_text.strip()
    
    def generate_rag_mcq(
        self,
        query: str,
        difficulty: str = 'medium',
        top_k: int = 3
    ) -> MCQQuestion:
        """Generate MCQ based on document content.
        
        Args:
            query: Question topic or query
            difficulty: Difficulty level (easy/medium/hard)
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            MCQQuestion: Generated question
            
        Raises:
            CustomException: If generation fails
        """
        try:
            # Retrieve relevant documents
            relevant_docs = self.retriever.retrieve(query, top_k=top_k)
            
            if not relevant_docs:
                raise CustomException(
                    "No relevant documents found. Please upload a document first."
                )
            
            context = "\n\n".join([doc for doc, _ in relevant_docs])
            
            self.logger.info(
                f"Generating RAG MCQ for: {query} (difficulty: {difficulty})"
            )
            
            # Create parser
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            
            # Format prompt with context
            prompt_text = rag_mcq_prompt_template.format(
                context=context,
                query=query,
                difficulty=difficulty.lower()
            )
            
            # Generate response
            response = self.llm.invoke(prompt_text)
            cleaned_content = self._clean_json_response(str(response.content))
            
            # Parse and validate
            question = parser.parse(cleaned_content)
            
            if len(question.options) != 4:
                raise ValueError(f"Expected 4 options, got {len(question.options)}")
            
            if question.correct_answer not in question.options:
                raise ValueError(
                    f"Correct answer '{question.correct_answer}' not in options"
                )
            
            self.logger.info("RAG MCQ generated successfully")
            return question
        
        except CustomException:
            raise
        except ValidationError as ve:
            error_msg = f"Validation error in RAG MCQ generation: {str(ve)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, ve)
        except Exception as e:
            error_msg = f"Failed to generate RAG MCQ: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def generate_rag_fill_blank(
        self,
        query: str,
        difficulty: str = 'medium',
        top_k: int = 3
    ) -> FillBlankQuestion:
        """Generate fill-in-the-blank question based on document content.
        
        Args:
            query: Question topic or query
            difficulty: Difficulty level (easy/medium/hard)
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            FillBlankQuestion: Generated question
            
        Raises:
            CustomException: If generation fails
        """
        try:
            # Retrieve relevant documents
            relevant_docs = self.retriever.retrieve(query, top_k=top_k)
            
            if not relevant_docs:
                raise CustomException(
                    "No relevant documents found. Please upload a document first."
                )
            
            context = "\n\n".join([doc for doc, _ in relevant_docs])
            
            self.logger.info(
                f"Generating RAG fill-blank for: {query} (difficulty: {difficulty})"
            )
            
            # Create parser
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
            
            # Format prompt with context
            prompt_text = rag_fill_blank_prompt_template.format(
                context=context,
                query=query,
                difficulty=difficulty.lower()
            )
            
            # Generate response
            response = self.llm.invoke(prompt_text)
            cleaned_content = self._clean_json_response(str(response.content))
            
            # Parse and validate
            question = parser.parse(cleaned_content)
            
            if "_____" not in question.question:
                raise ValueError("Question must contain '_____' blank marker")
            
            if not question.answer or question.answer.strip() == "":
                raise ValueError("Answer cannot be empty")
            
            self.logger.info("RAG fill-blank generated successfully")
            return question
        
        except CustomException:
            raise
        except ValidationError as ve:
            error_msg = f"Validation error in RAG fill-blank generation: {str(ve)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, ve)
        except Exception as e:
            error_msg = f"Failed to generate RAG fill-blank: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def clear(self) -> None:
        """Clear loaded documents from retriever."""
        self.retriever.clear()
        self.logger.info("RAG generator cleared")

"""Question Data Models and Schemas

This module defines Pydantic models for validating AI-generated questions.
These schemas ensure data integrity and consistency across the application.

Models:
    - MCQQuestion: Multiple Choice Question with 4 options and 1 correct answer
    - FillBlankQuestion: Fill-in-the-blank question with a single answer

Pydantic Benefits:
    - Automatic data validation and type checking
    - Clear data structure definitions
    - JSON serialization/deserialization
    - Runtime error detection for invalid data
"""

from typing import List
from pydantic import BaseModel, Field, validator, ValidationError

class MCQQuestion(BaseModel):
    """Multiple Choice Question Model
    
    Validates MCQ structure with exactly 4 options and ensures the correct answer
    matches one of the provided options.
    
    Attributes:
        question (str): The question text - must be clear and unambiguous
        options (List[str]): Exactly 4 possible answers
        correct_answer (str): The correct answer - must match one of the options
    
    Raises:
        ValidationError: If data doesn't meet the schema requirements
    """
    
    question: str = Field(
        ...,
        description="The question text",
        min_length=10,
        max_length=500
    )
    
    options: List[str] = Field(
        ...,
        description="List of exactly 4 answer options"
    )
    
    correct_answer: str = Field(
        ...,
        description="The correct answer - must match one of the options exactly"
    )
    
    @validator('question', pre=True)
    def clean_question(cls, v):
        """Clean and normalize question text.
        
        Handles cases where the question might be nested in a dict structure.
        """
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v).strip()
    
    @validator('options')
    def validate_options(cls, v):
        """Ensure all options are unique and non-empty."""
        if len(v) != 4:
            raise ValueError('Must have exactly 4 options')
        
        # Check for empty options
        if any(not option.strip() for option in v):
            raise ValueError('All options must be non-empty strings')
        
        # Check for duplicate options
        if len(set(v)) != len(v):
            raise ValueError('All options must be unique')
        
        return [option.strip() for option in v]
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v, values):
        """Ensure correct_answer matches one of the options exactly."""
        if 'options' in values:
            if v.strip() not in values['options']:
                raise ValueError(
                    f"correct_answer '{v}' must exactly match one of the options: {values['options']}"
                )
        return v.strip()
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "question": "What is the primary purpose of Python's __init__ method in a class?",
                "options": [
                    "To initialize class variables",
                    "To destroy objects",
                    "To create static methods",
                    "To import modules"
                ],
                "correct_answer": "To initialize class variables"
            }
        }
    

class FillBlankQuestion(BaseModel):
    """Fill-in-the-Blank Question Model
    
    Validates fill-in-the-blank question structure with a single blank marker
    and corresponding answer.
    
    Attributes:
        question (str): Question text with exactly one '_____' blank marker (5 underscores)
        answer (str): The correct word or phrase to fill the blank
    
    Raises:
        ValidationError: If data doesn't meet the schema requirements
    """
    
    question: str = Field(
        ...,
        description="Question text with '_____' marking the blank position",
        min_length=15,
        max_length=500
    )
    
    answer: str = Field(
        ...,
        description="The correct word or phrase for the blank",
        min_length=1,
        max_length=100
    )
    
    @validator('question', pre=True)
    def clean_question(cls, v):
        """Clean and normalize question text.
        
        Handles cases where the question might be nested in a dict structure.
        """
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v).strip()
    
    @validator('question')
    def validate_blank_marker(cls, v):
        """Ensure question contains exactly one blank marker ('_____')."""
        blank_marker = '_____'
        blank_count = v.count(blank_marker)
        
        if blank_count == 0:
            raise ValueError(
                f"Question must contain at least one blank marker: '{blank_marker}'"
            )
        
        if blank_count > 1:
            raise ValueError(
                f"Question must contain exactly ONE blank marker '{blank_marker}', found {blank_count}"
            )
        
        return v
    
    @validator('answer')
    def validate_answer(cls, v):
        """Ensure answer is meaningful and properly formatted."""
        v = v.strip()
        
        if not v:
            raise ValueError('Answer cannot be empty')
        
        # Check if answer is too generic
        if v.lower() in ['answer', 'blank', 'fill', 'here']:
            raise ValueError('Answer appears to be a placeholder, not an actual answer')
        
        return v
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "question": "In machine learning, the process of adjusting model parameters to minimize error is called _____.",
                "answer": "training"
            }
        }

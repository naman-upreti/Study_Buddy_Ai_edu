"""Additional Question Types Module

Implements True/False, Matching, and Multiple Select question types
with proper validation and scoring.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json


class TrueFalseQuestion(BaseModel):
    """True/False question schema."""
    
    question: str = Field(..., description="The true/false question")
    correct_answer: str = Field(
        ...,
        description="Correct answer (True or False)"
    )
    explanation: Optional[str] = Field(
        None,
        description="Optional explanation for the answer"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Python is a compiled language.",
                "correct_answer": "False",
                "explanation": "Python is an interpreted language, not compiled."
            }
        }


class MatchingQuestion(BaseModel):
    """Matching question schema - match terms to definitions."""
    
    question: str = Field(..., description="Instructions for matching")
    pairs: List[Dict[str, str]] = Field(
        ...,
        description="List of dicts with 'term' and 'definition' keys"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Match the following concepts to their definitions",
                "pairs": [
                    {"term": "Algorithm", "definition": "Step-by-step procedure for solving a problem"},
                    {"term": "Variable", "definition": "Named container for storing data"}
                ]
            }
        }


class MultipleSelectQuestion(BaseModel):
    """Multiple Select question - select all correct answers."""
    
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of answer options")
    correct_answers: List[str] = Field(
        ...,
        description="List of all correct answers (must be from options)"
    )
    explanation: Optional[str] = Field(
        None,
        description="Optional explanation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Which of the following are programming languages?",
                "options": ["Python", "HTML", "Java", "CSS"],
                "correct_answers": ["Python", "Java"],
                "explanation": "HTML and CSS are markup languages, not programming languages."
            }
        }


def validate_true_false_answer(user_answer: str, correct_answer: str) -> bool:
    """Validate true/false answer (case-insensitive).
    
    Args:
        user_answer: User's answer
        correct_answer: Correct answer
        
    Returns:
        bool: True if correct
    """
    return user_answer.strip().lower() == correct_answer.strip().lower()


def validate_matching_answer(user_pairs: List[Dict], correct_pairs: List[Dict]) -> tuple:
    """Validate matching question answers.
    
    Args:
        user_pairs: User's term-definition mappings
        correct_pairs: Correct mappings
        
    Returns:
        tuple: (is_correct, correct_count, total_count)
    """
    correct_count = 0
    total_count = len(correct_pairs)
    
    # Create a mapping of correct answers
    correct_mapping = {pair['term']: pair['definition'] for pair in correct_pairs}
    
    # Check each user answer
    for user_pair in user_pairs:
        term = user_pair.get('term', '')
        definition = user_pair.get('definition', '')
        
        if correct_mapping.get(term, '').lower() == definition.lower():
            correct_count += 1
    
    is_fully_correct = correct_count == total_count
    
    return is_fully_correct, correct_count, total_count


def validate_multiple_select(
    user_selections: List[str],
    correct_answers: List[str]
) -> tuple:
    """Validate multiple select answers.
    
    Args:
        user_selections: User's selected answers
        correct_answers: Correct answers
        
    Returns:
        tuple: (is_correct, correct_count, total_correct)
    """
    user_set = set(s.lower().strip() for s in user_selections)
    correct_set = set(c.lower().strip() for c in correct_answers)
    
    correct_count = len(user_set & correct_set)
    total_correct = len(correct_set)
    
    # All correct answers must be selected, no extra answers allowed
    is_correct = user_set == correct_set
    
    return is_correct, correct_count, total_correct

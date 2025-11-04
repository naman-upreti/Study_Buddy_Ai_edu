"""Question Generator Module

Core logic for generating educational questions using LLM with Pydantic validation.
"""

import json
import time
from typing import Union

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import ValidationError

from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import mcq_prompt_template, fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:
    """Generates educational questions using LLM with robust error handling."""
    
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("QuestionGenerator initialized successfully")

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

    def _retry_with_backoff(self, prompt, parser, topic: str, difficulty: str):
        """Generate and parse question with exponential backoff retry."""
        last_error = None
        
        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                self.logger.info(
                    f"Attempt {attempt}/{settings.MAX_RETRIES}: "
                    f"Generating {parser.pydantic_object.__name__} for '{topic}' ({difficulty})"
                )
                
                formatted_prompt = prompt.format(topic=topic, difficulty=difficulty)
                response = self.llm.invoke(formatted_prompt)
                
                cleaned_content = self._clean_json_response(str(response.content))
                self.logger.debug(f"LLM Response: {cleaned_content[:200]}...")
                
                parsed = parser.parse(cleaned_content)
                
                self.logger.info(f"Successfully parsed {parser.pydantic_object.__name__}")
                return parsed
                
            except ValidationError as ve:
                last_error = ve
                self.logger.warning(
                    f"Validation error on attempt {attempt}: {str(ve)}"
                )
                
            except json.JSONDecodeError as je:
                last_error = je
                self.logger.warning(
                    f"JSON parsing error on attempt {attempt}: {str(je)}"
                )
                
            except Exception as e:
                last_error = e
                self.logger.error(
                    f"Unexpected error on attempt {attempt}: {str(e)}"
                )
            
            if attempt < settings.MAX_RETRIES:
                wait_time = 2 ** (attempt - 1)
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        error_msg = f"Failed to generate question after {settings.MAX_RETRIES} attempts"
        self.logger.error(f"{error_msg}. Last error: {str(last_error)}")
        raise CustomException(error_msg, last_error if last_error else Exception("Unknown error"))
                
    
    def generate_mcq(self, topic: str, difficulty: str = 'medium') -> MCQQuestion:
        """Generate a multiple-choice question.
        
        Args:
            topic: Subject matter for the question
            difficulty: Question difficulty level (easy/medium/hard)
            
        Returns:
            MCQQuestion: Validated MCQ with 4 options
            
        Raises:
            CustomException: If generation or validation fails
        """
        try:
            self.logger.info(f"Starting MCQ generation: topic='{topic}', difficulty='{difficulty}'")
            
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            question = self._retry_with_backoff(
                mcq_prompt_template, parser, topic, difficulty
            )
            
            if len(question.options) != 4:
                raise ValueError(
                    f"Invalid MCQ: Expected 4 options, got {len(question.options)}"
                )
            
            if question.correct_answer not in question.options:
                raise ValueError(
                    f"Invalid MCQ: correct_answer '{question.correct_answer}' "
                    f"not found in options {question.options}"
                )
            
            self.logger.info(
                f"MCQ generated successfully: {question.question[:50]}..."
            )
            return question
            
        except CustomException:
            raise
            
        except Exception as e:
            error_msg = f"MCQ generation failed for topic '{topic}'"
            self.logger.error(f"{error_msg}: {str(e)}")
            raise CustomException(error_msg, e)
        
    
    def generate_fill_blank(
        self, topic: str, difficulty: str = 'medium'
    ) -> FillBlankQuestion:
        """Generate a fill-in-the-blank question.
        
        Args:
            topic: Subject matter for the question
            difficulty: Question difficulty level (easy/medium/hard)
            
        Returns:
            FillBlankQuestion: Validated fill-in-the-blank question
            
        Raises:
            CustomException: If generation or validation fails
        """
        try:
            self.logger.info(
                f"Starting Fill-Blank generation: topic='{topic}', difficulty='{difficulty}'"
            )
            
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
            question = self._retry_with_backoff(
                fill_blank_prompt_template, parser, topic, difficulty
            )
            
            if "_____" not in question.question:
                raise ValueError(
                    "Invalid Fill-Blank: Question must contain '_____' blank marker"
                )
            
            if not question.answer or question.answer.strip() == "":
                raise ValueError(
                    "Invalid Fill-Blank: Answer cannot be empty"
                )
            
            self.logger.info(
                f"Fill-Blank generated successfully: {question.question[:50]}..."
            )
            return question
            
        except CustomException:
            raise
            
        except Exception as e:
            error_msg = f"Fill-Blank generation failed for topic '{topic}'"
            self.logger.error(f"{error_msg}: {str(e)}")
            raise CustomException(error_msg, e)

    def generate_batch(
        self, 
        topic: str, 
        count: int, 
        question_type: str = 'mcq',
        difficulty: str = 'medium'
    ) -> list[Union[MCQQuestion, FillBlankQuestion]]:
        """Generate multiple questions in batch.
        
        Args:
            topic: Subject matter for questions
            count: Number of questions to generate
            question_type: Type of questions ('mcq' or 'fill_blank')
            difficulty: Question difficulty level
            
        Returns:
            List of generated questions
        """
        self.logger.info(
            f"Batch generation started: {count} {question_type} questions on '{topic}'"
        )
        
        questions = []
        generator = (
            self.generate_mcq if question_type == 'mcq' 
            else self.generate_fill_blank
        )
        
        for i in range(1, count + 1):
            try:
                self.logger.info(f"Generating question {i}/{count}")
                question = generator(topic, difficulty)
                questions.append(question)
            except Exception as e:
                self.logger.error(f"Failed to generate question {i}/{count}: {str(e)}")
                continue
        
        self.logger.info(
            f"Batch generation completed: {len(questions)}/{count} questions generated"
        )
        return questions


# ============================================================================
# EXPLANATION - How This Works (In Simple Terms)
# ============================================================================

"""
WHAT IS THIS FILE FOR?
----------------------
This is the brain of the question generation system. It takes a topic (like "Python")
and uses AI to create educational questions. Think of it as a teacher that never
runs out of creative questions!


MAIN CLASS: QuestionGenerator
------------------------------
This class does all the heavy lifting:
  1. Connects to the AI (Groq LLM)
  2. Sends prompts asking for questions
  3. Gets AI responses back
  4. Validates they're properly formatted
  5. Returns clean, usable questions


KEY OPTIMIZATIONS MADE:
-----------------------

1. EXPONENTIAL BACKOFF RETRY
   - Old way: Retry immediately 3 times
   - New way: Wait 1s, then 2s, then 4s between retries
   - Why: Gives the AI time to "reset" and reduces rapid failures
   - Example: Attempt 1 fails → wait 1 sec → Attempt 2 fails → wait 2 sec → Attempt 3

2. JSON CLEANING
   - Problem: AI sometimes wraps JSON in markdown code blocks like ```json...```
   - Solution: _clean_json_response() strips away the extra formatting
   - Result: More reliable parsing, fewer errors

3. BETTER ERROR HANDLING
   - Catches 3 specific error types:
     * ValidationError: Question structure is wrong (missing fields, etc.)
     * JSONDecodeError: AI response isn't valid JSON
     * General Exception: Anything else unexpected
   - Logs each error type differently for easier debugging

4. BATCH GENERATION (NEW!)
   - Generate multiple questions at once
   - Continues even if one fails (resilient)
   - Perfect for creating quiz banks or practice sets
   - Example: generate_batch("Python", count=5, question_type='mcq')

5. ENHANCED VALIDATION
   - MCQ: Checks exactly 4 options AND correct answer is in the list
   - Fill-Blank: Checks for "_____" marker AND answer isn't empty
   - Prevents bad questions from reaching users

6. BETTER LOGGING
   - Logs show progress: "Attempt 2/3: Generating MCQQuestion..."
   - Debug logs show partial AI responses (first 200 chars)
   - Success logs show question preview
   - Makes troubleshooting 10x easier


HOW THE FLOW WORKS:
-------------------

User calls generate_mcq("Python", "medium")
    ↓
1. Create Pydantic parser for MCQQuestion validation
    ↓
2. Call _retry_with_backoff()
    ↓
3. Format prompt: "Generate a medium MCQ about Python..."
    ↓
4. Send to AI (Groq LLM)
    ↓
5. Get response (hopefully JSON)
    ↓
6. Clean response (_clean_json_response)
    ↓
7. Parse with Pydantic (validates structure)
    ↓
8. If valid → Return question ✓
   If invalid → Retry with backoff (up to 3 times)
    ↓
9. Extra validation (4 options? correct answer in list?)
    ↓
10. Return validated MCQQuestion to caller


WHAT IS EXPONENTIAL BACKOFF?
-----------------------------
Imagine you're calling a busy friend:
  - Try 1: No answer → Wait 1 second
  - Try 2: No answer → Wait 2 seconds  
  - Try 3: No answer → Wait 4 seconds
  - Try 4: No answer → Wait 8 seconds

Each wait is 2x the previous. This prevents overwhelming the AI service
and gives it breathing room to recover from temporary issues.

Formula: wait_time = 2 ** (attempt - 1)
  - Attempt 1: 2^0 = 1 second
  - Attempt 2: 2^1 = 2 seconds
  - Attempt 3: 2^2 = 4 seconds


WHAT CAN GO WRONG?
------------------
1. AI returns malformed JSON
   → _clean_json_response() tries to fix it
   → If still broken, retry with backoff

2. AI returns valid JSON but wrong structure
   → Pydantic ValidationError is raised
   → Log the specific validation issue
   → Retry with backoff

3. AI returns correct structure but invalid content
   → Our manual validation catches it (e.g., only 3 options instead of 4)
   → Raise ValueError with clear message
   → Gets wrapped in CustomException for consistent error handling

4. All retries exhausted
   → Raise CustomException with full error details
   → Application can show user-friendly error message


BATCH GENERATION EXAMPLE:
-------------------------
generator = QuestionGenerator()

# Generate 5 MCQs about Python
questions = generator.generate_batch(
    topic="Python Programming",
    count=5,
    question_type='mcq',
    difficulty='medium'
)

# Returns list of MCQQuestion objects
# Even if 1 or 2 fail, you still get 3-4 questions back!
# Perfect for creating practice quizzes


SINGLE QUESTION EXAMPLE:
------------------------
generator = QuestionGenerator()

# Generate one MCQ
mcq = generator.generate_mcq(
    topic="Machine Learning",
    difficulty="hard"
)

print(mcq.question)  # "What is the primary purpose of..."
print(mcq.options)   # ["Option A", "Option B", "Option C", "Option D"]
print(mcq.correct_answer)  # "Option B"

# Generate one Fill-in-the-Blank
fib = generator.generate_fill_blank(
    topic="Data Science",
    difficulty="easy"
)

print(fib.question)  # "In statistics, the mean is also called the _____."
print(fib.answer)    # "average"


WHY THIS DESIGN IS BETTER:
--------------------------
✓ Resilient: Handles AI failures gracefully
✓ Fast: Exponential backoff prevents wasted rapid retries
✓ Scalable: Batch generation for bulk question creation
✓ Debuggable: Rich logging shows exactly what's happening
✓ Safe: Multiple validation layers prevent bad questions
✓ Maintainable: Clean code with explanations
✓ User-friendly: Clear error messages when things go wrong
"""
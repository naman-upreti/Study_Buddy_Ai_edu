"""Groq LLM Client Module

This module creates and configures ChatGroq instances for interacting with Groq's LLM API.
Groq provides fast, cost-effective LLM inference for generating educational questions.
"""

from langchain_groq import ChatGroq
from src.config.settings import settings
from src.common.custom_exception import CustomException
from src.common.logger import logging


def get_groq_llm() -> ChatGroq:
    """Factory function to create a configured ChatGroq LLM instance.
    
    Returns:
        ChatGroq: Configured LLM client ready for question generation
        
    Raises:
        CustomException: If API key is missing or initialization fails
    """
    try:
        if not settings.GROQ_API_KEY:
            error_message = (
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
            logging.error(error_message)
            raise CustomException(error_message)
        
        logging.info(f"Initializing Groq LLM with model: {settings.MODEL_NAME}")
        logging.info(f"Temperature set to: {settings.TEMPERATURE}")
        
        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,  # type: ignore
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE
        )
        
        logging.info("Groq LLM client initialized successfully")
        return llm
        
    except CustomException:
        raise
    
    except Exception as e:
        error_message = f"Failed to initialize Groq LLM: {str(e)}"
        logging.error(error_message)
        raise CustomException(error_message, e)


# ============================================================================
# EXPLANATION - How This Works (In Simple Terms)
# ============================================================================

"""
WHAT IS THIS FILE FOR?
----------------------
This file creates a connection to Groq's AI service so we can generate questions.
Think of it like setting up a phone line to call an AI assistant.


WHAT IS GROQ?
-------------
Groq is a company that provides super-fast AI language models. Instead of running
AI on our own computer (which would be slow and expensive), we send requests to
their servers and get answers back really quickly.

Benefits:
  ✓ Very fast response times
  ✓ Access to powerful models like Llama 3.1
  ✓ Cheaper than running AI locally
  ✓ Easy to use with LangChain


HOW DOES get_groq_llm() WORK?
------------------------------
This function does 3 main things:

1. CHECK IF WE HAVE AN API KEY
   - The API key is like a password to use Groq's service
   - It comes from your .env file (GROQ_API_KEY=your_key_here)
   - If missing, we throw an error because we can't connect without it

2. CREATE THE CONNECTION (ChatGroq)
   - api_key: Your secret password to authenticate
   - model: Which AI brain to use (we use "llama-3.1-8b-instant")
   - temperature: How creative the AI should be (0.0 to 1.0)

3. RETURN THE CONNECTED CLIENT
   - Other parts of the app use this client to generate questions
   - They just call get_groq_llm() and get a ready-to-use AI


WHAT IS TEMPERATURE?
--------------------
Temperature controls how creative vs. predictable the AI is:

  0.0 = Super focused and deterministic
        "What's 2+2?" → Always answers "4"
        
  0.5 = Balanced between creative and consistent
        Good for most tasks
        
  0.9 = Very creative and varied (OUR SETTING)
        "Write a question about Python" → Gets different creative questions
        Perfect for generating diverse educational questions!
        
  1.0 = Maximum randomness
        Can be too unpredictable


WHERE IS THIS USED?
-------------------
The question_generator.py file calls this function to get an AI client,
then uses it to:
  - Generate multiple choice questions
  - Generate fill-in-the-blank questions
  - Process prompts through LangChain


ERROR HANDLING
--------------
We handle two types of errors:

1. Missing API Key
   - Logs the error
   - Throws CustomException with helpful message
   - User knows exactly what to fix

2. Connection/Initialization Problems
   - Catches any unexpected errors
   - Logs what went wrong
   - Throws CustomException with details


EXAMPLE USAGE
-------------
from src.llm.groq_client import get_groq_llm

# Get the AI client
llm = get_groq_llm()

# Use it to generate something
response = llm.invoke("Explain Python in simple terms")
print(response.content)
# Output: "Python is a programming language that..."


WHY THE # type: ignore COMMENT?
-------------------------------
The type checker complains that we're passing a string (GROQ_API_KEY) when
it expects a special SecretStr type. But don't worry! ChatGroq is smart
enough to convert the string automatically. The # type: ignore just tells
the type checker to relax - we know what we're doing.
"""
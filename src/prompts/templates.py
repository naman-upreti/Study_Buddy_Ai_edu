from langchain_core.prompts import PromptTemplate

# Multiple Choice Question (MCQ) Prompt Template
mcq_prompt_template = PromptTemplate(
    template=(
        "You are an expert educational content creator. Generate a high-quality {difficulty} level "
        "multiple-choice question about the topic: {topic}.\n\n"
        "REQUIREMENTS:\n"
        "1. The question must be clear, unambiguous, and test real understanding\n"
        "2. Provide exactly 4 distinct and plausible answer options\n"
        "3. Ensure only ONE option is definitively correct\n"
        "4. Make incorrect options (distractors) realistic but clearly wrong\n"
        "5. Match the difficulty level: easy (basic), medium (application), hard (advanced analysis)\n\n"
        "Return ONLY a valid JSON object with these exact fields:\n"
        "- 'question': A clear, specific question string\n"
        "- 'options': An array of exactly 4 possible answer strings\n"
        "- 'correct_answer': The correct answer string (must match one option)\n\n"
        "Generate the question now. Return ONLY the JSON object, no additional text:"
    ),
    input_variables=["topic", "difficulty"]
)

# Fill-in-the-Blank Question Prompt Template
fill_blank_prompt_template = PromptTemplate(
    template=(
        "You are an expert educational content creator. Generate a high-quality {difficulty} level "
        "fill-in-the-blank question about the topic: {topic}.\n\n"
        "REQUIREMENTS:\n"
        "1. Create a complete, grammatically correct sentence with ONE blank\n"
        "2. Mark the blank location with exactly 5 underscores: '_____'\n"
        "3. The blank should test key knowledge\n"
        "4. The sentence should provide enough context to determine the answer\n"
        "5. The answer should be 1-3 words\n"
        "6. Match the difficulty level: easy (basic facts), medium (concepts), hard (technical terms)\n\n"
        "Return ONLY a valid JSON object with these exact fields:\n"
        "- 'question': A complete sentence with '_____' marking the blank position\n"
        "- 'answer': The correct word or short phrase\n\n"
        "Generate the question now. Return ONLY the JSON object, no additional text:"
    ),
    input_variables=["topic", "difficulty"]
)

# RAG-based MCQ Prompt Template
rag_mcq_prompt_template = PromptTemplate(
    template=(
        "You are an expert educational content creator. Using the provided document context, "
        "generate a high-quality {difficulty} level multiple-choice question about: {query}.\n\n"
        "DOCUMENT CONTEXT:\n"
        "{context}\n\n"
        "REQUIREMENTS:\n"
        "1. Create a question directly based on the document context\n"
        "2. The question should test understanding of the provided material\n"
        "3. Provide exactly 4 distinct and plausible answer options\n"
        "4. Ensure only ONE option is definitively correct based on the context\n"
        "5. Make incorrect options realistic but clearly wrong\n"
        "6. Do not ask about information outside the provided context\n"
        "7. Match the difficulty level: easy (recall), medium (understanding), hard (analysis)\n\n"
        "Return ONLY a valid JSON object with these exact fields:\n"
        "- 'question': A clear question string\n"
        "- 'options': An array of exactly 4 possible answer strings\n"
        "- 'correct_answer': The correct answer string (must match one option)\n\n"
        "Generate the question now. Return ONLY the JSON object, no additional text:"
    ),
    input_variables=["context", "query", "difficulty"]
)

# RAG-based Fill-in-the-Blank Prompt Template
rag_fill_blank_prompt_template = PromptTemplate(
    template=(
        "You are an expert educational content creator. Using the provided document context, "
        "generate a high-quality {difficulty} level fill-in-the-blank question about: {query}.\n\n"
        "DOCUMENT CONTEXT:\n"
        "{context}\n\n"
        "REQUIREMENTS:\n"
        "1. Create a question directly based on the document context\n"
        "2. The answer must be explicitly found in the provided context\n"
        "3. Create a complete, grammatically correct sentence with ONE blank\n"
        "4. Mark the blank location with exactly 5 underscores: '_____'\n"
        "5. The blank should test key knowledge from the material\n"
        "6. The sentence should provide enough context to determine the answer\n"
        "7. The answer should be 1-3 words\n"
        "8. Match the difficulty level: easy (obvious), medium (understanding), hard (deep knowledge)\n\n"
        "Return ONLY a valid JSON object with these exact fields:\n"
        "- 'question': A complete sentence with '_____' marking the blank position\n"
        "- 'answer': The correct word or short phrase\n\n"
        "Generate the question now. Return ONLY the JSON object, no additional text:"
    ),
    input_variables=["context", "query", "difficulty"]
)

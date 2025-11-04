# Standard library imports for file operations and date/time handling
import os
from datetime import datetime

# Third-party library imports for data manipulation and web UI
import pandas as pd
import streamlit as st

# Internal imports for quiz question generation
from src.generator.question_generator import QuestionGenerator


def rerun() -> None:
    """Toggle the rerun trigger in session state.
    
    This function toggles a boolean flag in Streamlit's session state,
    which can be used to trigger reruns of the application.
    If the key doesn't exist, it defaults to False.
    """
    # Toggle the rerun_trigger between True and False
    st.session_state['rerun_trigger'] = not st.session_state.get('rerun_trigger', False)


class QuizManager:
    """Manages quiz generation, execution, and result evaluation.
    
    This class handles the complete quiz workflow:
    - Generating questions from a QuestionGenerator
    - Displaying questions and collecting user answers via Streamlit UI
    - Evaluating answers and creating detailed results
    - Exporting results to CSV files
    """

    def __init__(self) -> None:
        """Initialize QuizManager with empty questions, answers, and results.
        
        Attributes:
            questions: List storing generated quiz questions with metadata
            user_answers: List storing user responses to each question
            results: List storing evaluation results with correctness info
        """
        # Initialize empty lists for storing quiz data
        self.questions: list = []  # Stores generated questions
        self.user_answers: list = []  # Stores user's answers
        self.results: list = []  # Stores evaluated results

    def generate_questions(
        self,
        generator: QuestionGenerator,
        topic: str,
        question_type: str,
        difficulty: str,
        num_questions: int,
    ) -> bool:
        """Generate quiz questions based on type and difficulty.

        Args:
            generator: QuestionGenerator instance to generate questions
            topic: Topic for questions (e.g., "Python", "Data Science")
            question_type: Type of question ("Multiple Choice" or "Fill in the blank")
            difficulty: Difficulty level (e.g., "easy", "medium", "hard")
            num_questions: Number of questions to generate

        Returns:
            bool: True if successful, False otherwise
        """
        # Reset all quiz data to start fresh
        self.questions = []  # Clear previous questions
        self.user_answers = []  # Clear previous answers
        self.results = []  # Clear previous results

        try:
            # Generate the specified number of questions
            for _ in range(num_questions):
                # Check question type and call appropriate generator method
                if question_type == "Multiple Choice":
                    # Generate MCQ question from the generator
                    question = generator.generate_mcq(topic, difficulty.lower())
                    # Store MCQ with all necessary metadata
                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_answer': question.correct_answer,
                    })
                else:
                    # Generate fill-in-the-blank question from the generator
                    question = generator.generate_fill_blank(topic, difficulty.lower())
                    # Store fill-in-the-blank question with metadata
                    self.questions.append({
                        'type': 'Fill in the blank',
                        'question': question.question,
                        'correct_answer': question.answer,
                    })
        except Exception as e:
            # Display error message in Streamlit UI and return failure status
            st.error(f"Error generating question: {e}")
            return False

        # Return success status
        return True
    

    def attempt_quiz(self) -> None:
        """Display quiz questions and collect user answers via Streamlit UI.
        
        Iterates through all generated questions and displays them with
        appropriate input widgets (radio buttons for MCQ, text input for fill-in-the-blank).
        Stores all user responses in self.user_answers.
        """
        # Loop through each question with its index
        for i, q in enumerate(self.questions):
            # Display question number and text in bold formatting
            st.markdown(f"**Question {i + 1}: {q['question']}**")

            # Check question type to determine input widget
            if q['type'] == 'MCQ':
                # Display radio button widget for multiple choice questions
                # The key ensures unique widget identification for Streamlit
                user_answer = st.radio(
                    f"Select and answer for Question {i + 1}",
                    q['options'],  # Display all available options
                    key=f"mcq_{i}",  # Unique key to prevent state conflicts
                )
                # Store the selected answer
                self.user_answers.append(user_answer)
            else:
                # Display text input widget for fill-in-the-blank questions
                user_answer = st.text_input(
                    f"Fill in the blank for Question {i + 1}",
                    key=f"fill_blank_{i}",  # Unique key for this text input
                )
                # Store the user's typed answer
                self.user_answers.append(user_answer)

    def evaluate_quiz(self) -> None:
        """Evaluate user answers and generate results.
        
        Compares user answers with correct answers and generates detailed result
        dictionaries. MCQ answers are compared exactly, while fill-in-the-blank
        answers are compared case-insensitively with whitespace trimmed.
        """
        # Reset results list to store fresh evaluation data
        self.results = []

        # Pair each question with its corresponding user answer
        for i, (q, user_ans) in enumerate(zip(self.questions, self.user_answers)):
            # Determine if this is a multiple choice question
            is_mcq = q['type'] == 'MCQ'
            
            # Evaluate correctness based on question type
            # MCQ: exact match required
            # Fill-in-blank: case-insensitive match with whitespace trimming
            is_correct = (
                user_ans == q['correct_answer']
                if is_mcq
                else user_ans.strip().lower() == q['correct_answer'].strip().lower()
            )

            # Create a dictionary containing complete result information
            result_dict = {
                'question_number': i + 1,  # Question number (1-indexed)
                'question': q['question'],  # The question text
                'question_type': q['type'],  # Type: 'MCQ' or 'Fill in the blank'
                'user_answer': user_ans,  # What the user answered
                'correct_answer': q['correct_answer'],  # The correct answer
                'is_correct': is_correct,  # Boolean: True if answer is correct
                'options': q['options'] if is_mcq else [],  # Available options for MCQ
            }

            # Store the result dictionary
            self.results.append(result_dict)

    def generate_result_dataframe(self) -> pd.DataFrame:
        """Generate a DataFrame from quiz results.
        
        Converts the results list into a pandas DataFrame for easy data
        manipulation, analysis, and export.

        Returns:
            pd.DataFrame: DataFrame containing quiz results, or empty DataFrame if no results
        """
        # Create DataFrame from results if available, otherwise return empty DataFrame
        return pd.DataFrame(self.results) if self.results else pd.DataFrame()
    
    def save_to_csv(self, filename_prefix: str = "quiz_results") -> str | None:
        """Save quiz results to a CSV file with timestamp.
        
        Exports the evaluated quiz results to a CSV file with a unique timestamp
        to prevent file overwrites. Creates 'results' directory if it doesn't exist.

        Args:
            filename_prefix: Prefix for the output filename (default: "quiz_results")

        Returns:
            str: Path to saved file, or None if save failed
        """
        # Check if there are any results to save
        if not self.results:
            st.warning("No results to save!")
            return None

        # Convert results to DataFrame for CSV export
        df = self.generate_result_dataframe()
        
        # Generate timestamp to ensure unique filename (prevents overwriting)
        # Format: YYYYMMDD_HHMMSS (e.g., 20231115_143022)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename with prefix and timestamp
        unique_filename = f"{filename_prefix}_{timestamp}.csv"

        # Create 'results' directory if it doesn't exist
        # exist_ok=True prevents error if directory already exists
        os.makedirs('results', exist_ok=True)
        
        # Construct full file path
        full_path = os.path.join('results', unique_filename)

        try:
            # Write DataFrame to CSV file without index column
            df.to_csv(full_path, index=False)
            # Display success message in Streamlit UI
            st.success("Results saved successfully!")
            # Return the path to the saved file
            return full_path
        except Exception as e:
            # Display error message if save operation fails
            st.error(f"Failed to save results: {e}")
            # Return None to indicate failure
            return None
            

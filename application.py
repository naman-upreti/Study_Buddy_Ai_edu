"""Study Buddy AI - Interactive Quiz Application

A Streamlit-based application for generating and managing interactive quizzes
using AI-powered question generation. Supports multiple question types and
difficulty levels with comprehensive result tracking and export.

Author: Study Buddy AI Team
Version: 1.0.0
"""

import os
import time
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from src.generator.question_generator import QuestionGenerator
from src.utils.helpers import QuizManager, rerun
from src.rag.rag_question_generator import RAGQuestionGenerator
from src.analytics.performance_tracker import PerformanceTracker

# Load environment variables from .env file
load_dotenv()


def configure_page() -> None:
    """Configure Streamlit page layout and settings.
    
    Sets page title, icon, and layout configuration for optimal
    user experience.
    """
    st.set_page_config(
        page_title="Study Buddy AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Apply custom CSS styling
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main Background */
        .main {
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        }
        
        /* Header Section */
        .header-container {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .header-container h1 {
            font-size: 3em;
            font-weight: 800;
            margin-bottom: 15px;
            letter-spacing: -1px;
        }
        
        .header-container p {
            font-size: 1.2em;
            opacity: 0.95;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
        }
        
        /* Metric Cards */
        .metric-container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 1.1em;
            font-weight: 600;
            padding: 15px 30px;
            border-radius: 12px 12px 0 0;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1em;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
        }
        
        /* Success/Error Messages */
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.1);
            border-left: 4px solid #10b981;
            border-radius: 8px;
            padding: 16px;
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
            border-radius: 8px;
            padding: 16px;
        }
        
        .stInfo {
            background-color: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 16px;
        }
        
        .stWarning {
            background-color: rgba(245, 158, 11, 0.1);
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            padding: 16px;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px;
            font-size: 1em;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: white;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            padding: 15px;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: #f9fafb;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        /* Card Containers */
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            margin-bottom: 20px;
        }
        
        /* Progress Bars */
        .stProgress > div > div > div {
            border-radius: 10px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
        }
        
        /* Section Headers */
        h2 {
            color: #1f2937;
            font-weight: 800;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
        }
        
        h3 {
            color: #374151;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 15px;
        }
        
        /* Text Styling */
        p {
            color: #6b7280;
            line-height: 1.6;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
        }
        
        /* Grid Layout Helper */
        .grid-container {
            display: grid;
            gap: 20px;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }
        </style>
    """, unsafe_allow_html=True)


def initialize_session_state() -> None:
    """Initialize all required session state variables.
    
    Creates session state variables for quiz management, tracking quiz
    generation status, submission status, and rerun triggers.
    """
    # Initialize quiz manager if not present
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    
    # Track if quiz has been generated
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    
    # Track if quiz has been submitted for evaluation
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    
    # Flag to trigger application rerun
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False
    
    # Initialize RAG generator if not present
    if 'rag_generator' not in st.session_state:
        st.session_state.rag_generator = RAGQuestionGenerator()
    
    # Track RAG document loaded
    if 'rag_document_loaded' not in st.session_state:
        st.session_state.rag_document_loaded = False
    
    # Store RAG document text
    if 'rag_document_text' not in st.session_state:
        st.session_state.rag_document_text = ""
    
    # Initialize performance tracker
    if 'performance_tracker' not in st.session_state:
        st.session_state.performance_tracker = PerformanceTracker()
    
    # Track quiz start time for analytics
    if 'quiz_start_time' not in st.session_state:
        st.session_state.quiz_start_time = None


def render_sidebar() -> tuple:
    """Render quiz configuration sidebar.
    
    Displays all quiz settings input widgets in the sidebar and returns
    user selections.
    
    Returns:
        tuple: (question_type, topic, difficulty, num_questions)
    """
    st.sidebar.header("⚙️ Quiz Configuration")
    st.sidebar.markdown("---")
    
    # Question type selection
    question_type = st.sidebar.selectbox(
        "Question Type",
        ["Multiple Choice", "Fill in the Blank"],
        index=0,
        help="Choose the format of questions for the quiz",
    )
    
    # Topic input
    topic = st.sidebar.text_input(
        "Topic",
        placeholder="e.g., Indian History, Geography, Biology",
        help="Enter the topic for which you want to generate questions",
    )
    
    # Difficulty level selection
    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1,
        help="Select the difficulty level of questions",
    )
    
    # Number of questions input
    num_questions = st.sidebar.number_input(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=5,
        help="Total number of questions to generate (1-20)",
    )
    
    st.sidebar.markdown("---")
    
    return question_type, topic, difficulty, num_questions


def handle_quiz_generation(
    question_type: str,
    topic: str,
    difficulty: str,
    num_questions: int,
) -> bool:
    """Handle quiz generation process.
    
    Args:
        question_type: Type of questions ("Multiple Choice" or "Fill in the Blank")
        topic: Topic for question generation
        difficulty: Difficulty level ("Easy", "Medium", "Hard")
        num_questions: Number of questions to generate
    
    Returns:
        bool: True if generation was successful, False otherwise
    """
    # Validate topic input
    if not topic.strip():
        st.sidebar.error("⚠️ Please enter a topic")
        return False
    
    # Reset submission state for new quiz
    st.session_state.quiz_submitted = False
    
    # Store quiz parameters for analytics
    st.session_state.quiz_topic = topic
    st.session_state.quiz_difficulty = difficulty
    st.session_state.quiz_question_type = question_type
    
    # Create generator and generate questions
    try:
        with st.spinner("🔄 Generating questions..."):
            generator = QuestionGenerator()
            success = st.session_state.quiz_manager.generate_questions(
                generator,
                topic,
                question_type,
                difficulty,
                num_questions,
            )
        
        if success:
            st.sidebar.success("✅ Quiz generated successfully!")
            st.session_state.quiz_generated = success
            rerun()
        else:
            st.sidebar.error("❌ Failed to generate quiz. Please try again.")
            return False
    
    except Exception as e:
        st.sidebar.error(f"❌ Error generating quiz: {str(e)}")
        return False
    
    return True


def render_quiz_section() -> None:
    """Render the quiz attempt section.
    
    Displays quiz questions and handles the submission process.
    """
    if not (st.session_state.quiz_generated and st.session_state.quiz_manager.questions):
        return
    
    st.header("📝 Quiz")
    st.markdown("---")
    
    # Display quiz questions
    st.session_state.quiz_manager.attempt_quiz()
    
    # Submit button with columns for better layout
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("✅ Submit Quiz", use_container_width=True):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()


def render_results_section() -> None:
    """Render the quiz results and analysis section.
    
    Displays detailed results, score calculation, answer review,
    and CSV export functionality.
    """
    if not st.session_state.quiz_submitted:
        return
    
    st.header("📊 Quiz Results")
    st.markdown("---")
    
    results_df = st.session_state.quiz_manager.generate_result_dataframe()
    
    if results_df.empty:
        st.warning("⚠️ No results available")
        return
    
    # Calculate and display score
    correct_count = results_df["is_correct"].sum()
    total_questions = len(results_df)
    score_percentage = (correct_count / total_questions) * 100
    
    # Display score metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Score", f"{score_percentage:.1f}%")
    with col2:
        st.metric("Correct Answers", f"{int(correct_count)}/{total_questions}")
    with col3:
        st.metric("Accuracy", f"{(correct_count/total_questions)*100:.0f}%")
    with col4:
        st.metric("Incorrect", total_questions - int(correct_count))
    
    st.markdown("---")
    st.subheader("📋 Detailed Review")
    
    # Display each result with visual indicators
    for idx, (_, result) in enumerate(results_df.iterrows(), 1):
        question_num = result['question_number']
        is_correct = result['is_correct']
        
        # Create expandable section for each question
        with st.expander(
            f"{'✅' if is_correct else '❌'} Question {question_num}: {result['question']}",
            expanded=False,
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Your Answer:**")
                answer_style = "✅" if is_correct else "❌"
                st.info(f"{answer_style} {result['user_answer']}")
            
            with col2:
                st.write("**Correct Answer:**")
                st.success(f"✅ {result['correct_answer']}")
            
            # Display options for MCQ if available
            if result['options']:
                st.write("**All Options:**")
                for option in result['options']:
                    st.write(f"  • {option}")
    
    st.markdown("---")
    
    # Export and download section
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save Results", use_container_width=True):
            # Record performance
            time_taken = time.time() - st.session_state.quiz_start_time if st.session_state.quiz_start_time else 0
            tracker = st.session_state.performance_tracker
            
            # Get quiz parameters from session (they should be stored during generation)
            topic = st.session_state.get('quiz_topic', 'General')
            difficulty = st.session_state.get('quiz_difficulty', 'Medium')
            question_type = st.session_state.get('quiz_question_type', 'Mixed')
            
            tracker.record_attempt(
                topic=topic,
                question_type=question_type,
                difficulty=difficulty,
                total_questions=total_questions,
                correct_answers=int(correct_count),
                time_taken=time_taken,
                questions_data=results_df.to_dict('records')
            )
            
            saved_file = st.session_state.quiz_manager.save_to_csv()
            if saved_file:
                st.session_state.saved_file = saved_file
                st.success(f"✅ Results saved and analytics updated!")
            else:
                st.error("❌ Failed to save results")
    
    # Download button if file was saved
    if 'saved_file' in st.session_state:
        with col2:
            with open(st.session_state.saved_file, 'rb') as f:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=f.read(),
                    file_name=os.path.basename(st.session_state.saved_file),
                    mime='text/csv',
                    use_container_width=True,
                )


def render_rag_section() -> None:
    """Render the RAG-based question generation section.
    
    Allows users to upload documents and generate questions based on content.
    """
    st.header("📄 RAG-Based Questions")
    st.markdown("---")
    st.markdown("Upload a document and generate questions based on its content.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file (TXT, PDF, DOCX)",
            type=["txt", "pdf", "docx"],
            help="Supported formats: TXT, PDF, DOCX (Max 50MB)"
        )
        
        if uploaded_file:
            try:
                with st.spinner("📖 Processing document..."):
                    text = st.session_state.rag_generator.load_document(uploaded_file)
                    st.session_state.rag_document_loaded = True
                    st.session_state.rag_document_text = text
                    st.success(f"✅ Document loaded! ({len(text)} characters)")
            except Exception as e:
                st.error(f"❌ Error loading document: {str(e)}")
                st.session_state.rag_document_loaded = False
    
    with col2:
        st.subheader("❓ Generate Questions")
        if st.session_state.rag_document_loaded:
            rag_question_type = st.selectbox(
                "Question Type",
                ["Multiple Choice", "Fill in the Blank"],
                key="rag_question_type"
            )
            
            rag_query = st.text_input(
                "Question Topic",
                placeholder="What should the question be about?",
                help="Specify the aspect of the document to focus on"
            )
            
            rag_difficulty = st.selectbox(
                "Difficulty Level",
                ["Easy", "Medium", "Hard"],
                index=1,
                key="rag_difficulty"
            )
            
            if st.button("🚀 Generate Question", use_container_width=True):
                if not rag_query.strip():
                    st.error("⚠️ Please enter a question topic")
                else:
                    try:
                        with st.spinner("🔄 Generating question from document..."):
                            if rag_question_type == "Multiple Choice":
                                question = st.session_state.rag_generator.generate_rag_mcq(
                                    rag_query,
                                    rag_difficulty.lower()
                                )
                                st.session_state.current_rag_question = question
                                st.session_state.rag_question_type = "MCQ"
                            else:
                                question = st.session_state.rag_generator.generate_rag_fill_blank(
                                    rag_query,
                                    rag_difficulty.lower()
                                )
                                st.session_state.current_rag_question = question
                                st.session_state.rag_question_type = "FILL_BLANK"
                            
                            st.success("✅ Question generated!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating question: {str(e)}")
        else:
            st.info("📤 Upload a document first to generate questions")
    
    st.markdown("---")
    
    # Display generated question if available
    if 'current_rag_question' in st.session_state:
        st.subheader("📋 Generated Question")
        question = st.session_state.current_rag_question
        
        if st.session_state.rag_question_type == "MCQ":
            st.write(f"**Question:** {question.question}")
            st.write("**Options:**")
            for i, option in enumerate(question.options, 1):
                st.write(f"  {i}. {option}")
            
            user_answer = st.radio(
                "Select your answer:",
                question.options,
                key="rag_mcq_answer"
            )
            
            if st.button("Check Answer"):
                if user_answer == question.correct_answer:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {question.correct_answer}")
        
        else:  # Fill-in-the-blank
            st.write(f"**Question:** {question.question}")
            user_answer = st.text_input("Your answer:")
            
            if st.button("Check Answer"):
                if user_answer.strip().lower() == question.answer.strip().lower():
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {question.answer}")


def render_dashboard() -> None:
    """Render the analytics and performance dashboard.
    
    Displays overall statistics, topic-wise performance, and learning insights.
    """
    st.header("📊 Performance Analytics Dashboard")
    st.markdown("---")
    
    tracker = st.session_state.performance_tracker
    overall_stats = tracker.get_overall_stats()
    
    if overall_stats['total_attempts'] == 0:
        st.info("💶 No quiz attempts yet. Take some quizzes to see your analytics!")
        return
    
    # Overall Statistics Section
    st.subheader("🏆 Overall Performance")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style='text-align: center;'>
                    <p style='color: #6b7280; margin: 0; font-size: 0.9em;'>Total Quizzes</p>
                    <h2 style='color: #6366f1; margin: 10px 0;'>{overall_stats['total_attempts']}</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style='text-align: center;'>
                    <p style='color: #6b7280; margin: 0; font-size: 0.9em;'>Overall Accuracy</p>
                    <h2 style='color: #10b981; margin: 10px 0;'>{overall_stats['overall_accuracy']:.1f}%</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style='text-align: center;'>
                    <p style='color: #6b7280; margin: 0; font-size: 0.9em;'>Study Time</p>
                    <h2 style='color: #f59e0b; margin: 10px 0;'>{overall_stats['total_time']/60:.1f}m</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-container">
                <div style='text-align: center;'>
                    <p style='color: #6b7280; margin: 0; font-size: 0.9em;'>Questions</p>
                    <h2 style='color: #3b82f6; margin: 10px 0;'>{overall_stats['total_questions_answered']}</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Topic Performance Section
    st.subheader("📄 Topic-Wise Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Strong Areas** (80%+)", help="Topics where you're performing well")
        strong_areas = tracker.get_strong_areas()
        if strong_areas:
            for topic, accuracy in strong_areas.items():
                st.markdown(
                    f"""
                    <div style='background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #10b981;'>
                        <p style='margin: 0; color: #1f2937; font-weight: 600;'>{topic}</p>
                        <p style='margin: 5px 0 0 0; color: #10b981; font-weight: 700;'>{accuracy:.1f}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("📋 Keep practicing to reach 80% accuracy!")
    
    with col2:
        st.markdown("**⚠️ Areas to Improve** (<70%)", help="Topics that need more practice")
        weak_areas = tracker.get_weak_areas()
        if weak_areas:
            for topic, accuracy in weak_areas.items():
                st.markdown(
                    f"""
                    <div style='background: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ef4444;'>
                        <p style='margin: 0; color: #1f2937; font-weight: 600;'>{topic}</p>
                        <p style='margin: 5px 0 0 0; color: #ef4444; font-weight: 700;'>{accuracy:.1f}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.success("🌟 Excellent! No weak areas identified.")
    
    st.markdown("---")
    
    # Difficulty Distribution
    st.subheader("🎯 Difficulty Distribution")
    difficulty_dist = overall_stats['difficulty_distribution']
    
    if difficulty_dist:
        col1, col2, col3 = st.columns(3)
        difficulties = [('Easy', col1), ('Medium', col2), ('Hard', col3)]
        
        for difficulty, col in difficulties:
            with col:
                count = difficulty_dist.get(difficulty, 0)
                st.metric(f"{difficulty} Quizzes", count)
    
    st.markdown("---")
    
    # Recent Attempts
    st.subheader("💶 Recent Quiz Attempts")
    recent = tracker.get_recent_attempts(5)
    
    if recent:
        for idx, attempt in enumerate(recent, 1):
            # Determine color based on accuracy
            if attempt.accuracy >= 80:
                color = "#10b981"
                status = "🌟 Excellent"
            elif attempt.accuracy >= 70:
                color = "#f59e0b"
                status = "🎉 Good"
            else:
                color = "#ef4444"
                status = "💶 Keep Trying"
            
            st.markdown(
                f"""
                <div style='background: white; border-radius: 12px; border-left: 4px solid {color}; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);'>
                    <div style='display: flex; justify-content: space-between; align-items: start;'>
                        <div>
                            <h4 style='margin: 0 0 8px 0; color: #1f2937;'>{attempt.topic}</h4>
                            <p style='margin: 5px 0; color: #6b7280; font-size: 0.9em;'>
                                <span style='background: {color}; color: white; padding: 4px 8px; border-radius: 6px; font-weight: 600;'>{attempt.difficulty}</span>
                                <span style='margin-left: 10px;'>{attempt.question_type}</span>
                            </p>
                        </div>
                        <div style='text-align: right;'>
                            <h2 style='margin: 0; color: {color};'>{attempt.accuracy:.1f}%</h2>
                            <p style='margin: 5px 0 0 0; color: {color}; font-size: 0.9em;'>{status}</p>
                        </div>
                    </div>
                    <div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 0.9em;'>
                        <div><span style='color: #6b7280;'>Correct:</span> <strong>{attempt.correct_answers}/{attempt.total_questions}</strong></div>
                        <div><span style='color: #6b7280;'>Time:</span> <strong>{attempt.time_taken:.0f}s</strong></div>
                        <div><span style='color: #6b7280;'>Date:</span> <strong>{attempt.timestamp[:10]}</strong></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("💶 No quiz attempts yet. Take a quiz to see your history!")
    
    st.markdown("---")
    
    # Clear Data Option
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if st.button("🗑️ Clear Analytics", type="secondary"):
            tracker.clear_data()
            st.success("Analytics cleared!")
            st.rerun()


def main() -> None:
    """Main application entry point.
    
    Orchestrates the entire Streamlit application flow including
    page configuration, session state initialization, sidebar rendering,
    quiz generation, quiz attempt, and results display.
    """
    # Configure page layout and settings
    configure_page()
    
    # Initialize session state variables
    initialize_session_state()
    
    # Enhanced Header Section
    st.markdown(
        """
        <div class="header-container">
            <h1>📚 Study Buddy AI</h1>
            <p>Your AI-powered interactive quiz platform. Generate quizzes, test your knowledge, and track your learning progress with advanced analytics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create tabs for different features
    tab1, tab2, tab3 = st.tabs([
        "🎯 Quiz Generator",
        "📄 Document Q&A",
        "📊 Analytics"
    ])
    
    with tab1:
        st.markdown("""<h2 style='color: #1f2937; margin-bottom: 30px;'>🎯 Create Your Quiz</h2>""", unsafe_allow_html=True)
        
        # Render sidebar configuration
        question_type, topic, difficulty, num_questions = render_sidebar()
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🚀 Generate Quiz", use_container_width=True, key="gen_btn"):
                st.session_state.quiz_start_time = time.time()
                handle_quiz_generation(question_type, topic, difficulty, num_questions)
        with col2:
            st.markdown("<p style='color: #6b7280; margin-top: 10px;'><i>Select your preferences above and click Generate to create a personalized quiz</i></p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Render quiz section if generated
        render_quiz_section()
        
        # Render results section if submitted
        render_results_section()
    
    with tab2:
        st.markdown("""<h2 style='color: #1f2937; margin-bottom: 30px;'>📄 Upload & Learn</h2>""", unsafe_allow_html=True)
        st.markdown("<p style='color: #6b7280; margin-bottom: 20px;'>Upload your study materials (PDF, DOCX, or TXT) and generate questions based on the content.</p>", unsafe_allow_html=True)
        
        # Render RAG section
        render_rag_section()
    
    with tab3:
        st.markdown("""<h2 style='color: #1f2937; margin-bottom: 30px;'>📊 Your Learning Dashboard</h2>""", unsafe_allow_html=True)
        
        # Render dashboard
        render_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; color: #6b7280;'>
            <p><strong>🚀 Study Buddy AI</strong> - Making learning smarter, one quiz at a time</p>
            <p style='font-size: 0.9em; margin-top: 10px;'>Powered by AI ❤️ | © 2024 Study Buddy AI Team</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

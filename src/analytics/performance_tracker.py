"""Performance Tracking and Analytics Module

Tracks user performance across quizzes, stores statistics, and provides
analytics for personalized learning insights.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Optional
import json
import os

from src.common.logger import get_logger
from src.common.custom_exception import CustomException


@dataclass
class QuizAttempt:
    """Represents a single quiz attempt with performance metrics."""
    
    attempt_id: str
    topic: str
    question_type: str
    difficulty: str
    total_questions: int
    correct_answers: int
    accuracy: float
    time_taken: float  # in seconds
    timestamp: str
    questions_data: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return asdict(self)


class PerformanceTracker:
    """Tracks and analyzes user quiz performance."""
    
    def __init__(self, storage_file: str = "quiz_performance.json"):
        """Initialize performance tracker.
        
        Args:
            storage_file: File path for storing performance data
        """
        self.logger = get_logger(self.__class__.__name__)
        self.storage_file = storage_file
        self.attempts: List[QuizAttempt] = []
        self._load_data()
        self.logger.info("PerformanceTracker initialized")
    
    def _load_data(self) -> None:
        """Load performance data from storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.attempts = [
                        QuizAttempt(**attempt) for attempt in data
                    ]
                self.logger.info(f"Loaded {len(self.attempts)} previous attempts")
        except Exception as e:
            self.logger.warning(f"Could not load performance data: {str(e)}")
            self.attempts = []
    
    def _save_data(self) -> None:
        """Save performance data to storage file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(
                    [attempt.to_dict() for attempt in self.attempts],
                    f,
                    indent=2
                )
            self.logger.info("Performance data saved")
        except Exception as e:
            self.logger.error(f"Failed to save performance data: {str(e)}")
    
    def record_attempt(
        self,
        topic: str,
        question_type: str,
        difficulty: str,
        total_questions: int,
        correct_answers: int,
        time_taken: float,
        questions_data: List[Dict]
    ) -> QuizAttempt:
        """Record a quiz attempt.
        
        Args:
            topic: Quiz topic
            question_type: Type of questions
            difficulty: Difficulty level
            total_questions: Total questions in quiz
            correct_answers: Number of correct answers
            time_taken: Time taken in seconds
            questions_data: Detailed question data
            
        Returns:
            QuizAttempt: Recorded attempt
        """
        try:
            attempt_id = f"attempt_{len(self.attempts) + 1}_{datetime.now().timestamp()}"
            accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            attempt = QuizAttempt(
                attempt_id=attempt_id,
                topic=topic,
                question_type=question_type,
                difficulty=difficulty,
                total_questions=total_questions,
                correct_answers=correct_answers,
                accuracy=accuracy,
                time_taken=time_taken,
                timestamp=datetime.now().isoformat(),
                questions_data=questions_data
            )
            
            self.attempts.append(attempt)
            self._save_data()
            
            self.logger.info(f"Recorded attempt: {attempt_id} (Accuracy: {accuracy:.1f}%)")
            return attempt
        
        except Exception as e:
            error_msg = f"Failed to record attempt: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg)
    
    def get_topic_stats(self, topic: str) -> Dict:
        """Get statistics for a specific topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Dict with topic statistics
        """
        topic_attempts = [a for a in self.attempts if a.topic.lower() == topic.lower()]
        
        if not topic_attempts:
            return {
                'total_attempts': 0,
                'average_accuracy': 0,
                'best_accuracy': 0,
                'worst_accuracy': 0,
                'total_time': 0,
                'average_time_per_question': 0
            }
        
        accuracies = [a.accuracy for a in topic_attempts]
        times = [a.time_taken for a in topic_attempts]
        total_questions = sum(a.total_questions for a in topic_attempts)
        
        return {
            'total_attempts': len(topic_attempts),
            'average_accuracy': sum(accuracies) / len(accuracies),
            'best_accuracy': max(accuracies),
            'worst_accuracy': min(accuracies),
            'total_time': sum(times),
            'average_time_per_question': sum(times) / total_questions if total_questions > 0 else 0,
            'total_correct': sum(a.correct_answers for a in topic_attempts),
            'total_questions_attempted': total_questions
        }
    
    def get_difficulty_stats(self, difficulty: str) -> Dict:
        """Get statistics for a specific difficulty level.
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Dict with difficulty statistics
        """
        difficulty_attempts = [
            a for a in self.attempts 
            if a.difficulty.lower() == difficulty.lower()
        ]
        
        if not difficulty_attempts:
            return {
                'total_attempts': 0,
                'average_accuracy': 0,
                'topics_attempted': []
            }
        
        accuracies = [a.accuracy for a in difficulty_attempts]
        topics = list(set(a.topic for a in difficulty_attempts))
        
        return {
            'total_attempts': len(difficulty_attempts),
            'average_accuracy': sum(accuracies) / len(accuracies),
            'topics_attempted': topics,
            'best_performance': max(accuracies),
            'worst_performance': min(accuracies)
        }
    
    def get_overall_stats(self) -> Dict:
        """Get overall statistics across all attempts.
        
        Returns:
            Dict with overall statistics
        """
        if not self.attempts:
            return {
                'total_attempts': 0,
                'overall_accuracy': 0,
                'total_time': 0,
                'topics_attempted': [],
                'difficulty_distribution': {}
            }
        
        accuracies = [a.accuracy for a in self.attempts]
        total_time = sum(a.time_taken for a in self.attempts)
        topics = list(set(a.topic for a in self.attempts))
        
        # Count attempts by difficulty
        difficulty_dist = {}
        for attempt in self.attempts:
            diff = attempt.difficulty
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        return {
            'total_attempts': len(self.attempts),
            'overall_accuracy': sum(accuracies) / len(accuracies),
            'best_accuracy': max(accuracies),
            'worst_accuracy': min(accuracies),
            'total_time': total_time,
            'average_time_per_attempt': total_time / len(self.attempts),
            'topics_attempted': topics,
            'difficulty_distribution': difficulty_dist,
            'total_questions_answered': sum(a.total_questions for a in self.attempts),
            'total_correct_answers': sum(a.correct_answers for a in self.attempts)
        }
    
    def get_recent_attempts(self, limit: int = 10) -> List[QuizAttempt]:
        """Get recent quiz attempts.
        
        Args:
            limit: Number of recent attempts to return
            
        Returns:
            List of recent QuizAttempt objects
        """
        return sorted(
            self.attempts,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
    
    def get_improvement_trend(self, topic: str, limit: int = 10) -> List[float]:
        """Get accuracy trend for a topic.
        
        Args:
            topic: Topic name
            limit: Number of recent attempts
            
        Returns:
            List of accuracy values in chronological order
        """
        topic_attempts = sorted(
            [a for a in self.attempts if a.topic.lower() == topic.lower()],
            key=lambda x: x.timestamp
        )
        
        return [a.accuracy for a in topic_attempts[-limit:]]
    
    def get_weak_areas(self, threshold: float = 70.0) -> Dict[str, float]:
        """Identify weak areas (topics below threshold).
        
        Args:
            threshold: Accuracy threshold (default 70%)
            
        Returns:
            Dict mapping topics to average accuracy
        """
        topic_stats = {}
        for topic in set(a.topic for a in self.attempts):
            stats = self.get_topic_stats(topic)
            if stats['average_accuracy'] < threshold:
                topic_stats[topic] = stats['average_accuracy']
        
        return dict(sorted(topic_stats.items(), key=lambda x: x[1]))
    
    def get_strong_areas(self, threshold: float = 80.0) -> Dict[str, float]:
        """Identify strong areas (topics above threshold).
        
        Args:
            threshold: Accuracy threshold (default 80%)
            
        Returns:
            Dict mapping topics to average accuracy
        """
        topic_stats = {}
        for topic in set(a.topic for a in self.attempts):
            stats = self.get_topic_stats(topic)
            if stats['average_accuracy'] >= threshold:
                topic_stats[topic] = stats['average_accuracy']
        
        return dict(sorted(topic_stats.items(), key=lambda x: x[1], reverse=True))
    
    def clear_data(self) -> None:
        """Clear all performance data."""
        self.attempts = []
        self._save_data()
        self.logger.info("Performance data cleared")

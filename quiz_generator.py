"""
Quiz generator module for creating diagnostic quizzes.
"""
from .ai_service import AIService
from typing import List, Dict, Any


class QuizGenerator:
    def __init__(self):
        self.ai_service = AIService()

    def generate_quiz(self, skill_name: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate a quiz for the given skill."""
        try:
            questions = self.ai_service.generate_questions(skill_name, num_questions)
            return questions
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")


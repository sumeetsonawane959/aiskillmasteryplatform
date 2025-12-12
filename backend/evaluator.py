"""
Evaluator module for AI-based answer evaluation.
"""
from .ai_service import AIService
from typing import List, Dict, Any


class Evaluator:
    def __init__(self):
        self.ai_service = AIService()

    def evaluate(self, skill_name: str, questions: List[Dict], 
                user_answers: List[str]) -> Dict[str, Any]:
        """Evaluate user answers and return structured evaluation."""
        try:
            evaluation = self.ai_service.evaluate_answers(skill_name, questions, user_answers)
            return evaluation
        except Exception as e:
            raise Exception(f"Failed to evaluate answers: {str(e)}")


"""
AI service for Google Gemini API integration.
"""
import os
import json
import google.generativeai as genai
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        
        # Try to get available models first
        available_models = self._get_available_models()
        
        # Use models/gemini-2.0-flash as default (latest available)
        # Can be overridden with GEMINI_MODEL env variable
        # Available models: models/gemini-2.5-flash, models/gemini-2.0-flash, etc.
        model_name = os.getenv("GEMINI_MODEL", None)
        
        # If no model specified, try to find a working one
        if not model_name:
            model_name = self._find_working_model(available_models)
        
        # Try different model name formats
        self.model = self._initialize_model(model_name, available_models)
    
    def _get_available_models(self):
        """Get list of available models from the API."""
        try:
            models = genai.list_models()
            return [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        except Exception as e:
            print(f"Warning: Could not list models: {str(e)}")
            return []
    
    def _find_working_model(self, available_models):
        """Find a working model from available models, prioritizing latest free tier."""
        # Priority order - latest models first
        preferred_models = [
            "models/gemini-2.5-flash",      # Latest
            "models/gemini-2.0-flash",       # Stable 2.0
            "models/gemini-2.0-flash-001",   # Stable 2.0 with version
            "models/gemini-2.0-flash-lite",  # Lite version
            "gemini-2.5-flash",               # Without prefix
            "gemini-2.0-flash",
            "gemini-2.0-flash-001",
            # Legacy models (may not be available)
            "models/gemini-1.5-flash-001",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro-001",
            "models/gemini-1.5-pro",
            "gemini-pro",
        ]
        
        # Check if any preferred model is in available models
        if available_models:
            for pref in preferred_models:
                # Check exact match or if the model name ends with our preferred name
                for avail in available_models:
                    if pref == avail or avail.endswith(pref.split('/')[-1]):
                        return pref if pref.startswith("models/") else f"models/{pref}"
        
        # If we have available models but none matched, use the first one
        if available_models:
            return available_models[0]
        
        # Default fallback - use latest available
        return "models/gemini-2.5-flash"
    
    def _initialize_model(self, model_name, available_models):
        """Initialize model with fallback options."""
        # List of models to try in order (latest models first)
        models_to_try = []
        
        # Add the requested model with variants
        if model_name:
            # Try with and without models/ prefix
            if not model_name.startswith("models/"):
                models_to_try.append(f"models/{model_name}")
            models_to_try.append(model_name)
            # Try variants
            if "-001" in model_name:
                models_to_try.append(model_name.replace("-001", ""))
            else:
                models_to_try.append(model_name + "-001")
        
        # Add latest models (Gemini 2.5/2.0) - these are what's actually available
        models_to_try.extend([
            "models/gemini-2.5-flash",      # Latest - confirmed working!
            "gemini-2.5-flash",             # Without prefix - also works!
            "models/gemini-2.5-pro",        # Pro version
            "models/gemini-2.0-flash",       # Stable 2.0 (may hit quota)
            "models/gemini-2.0-flash-001",   # With version
            "models/gemini-2.0-flash-lite",  # Lite version
            "gemini-2.0-flash",
            "gemini-2.0-flash-001",
            # Legacy models (deprecated - won't work)
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "gemini-pro",
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]
        
        last_error = None
        for model_variant in models_to_try:
            try:
                model = genai.GenerativeModel(model_variant)
                # Try a simple test to verify the model works
                try:
                    # Just create the model object - don't make a call yet
                    # The model will be tested when first used
                    pass
                except:
                    continue
                return model
            except Exception as e:
                last_error = e
                continue
        
        # If still failing, provide helpful error message with available models
        error_msg = f"Failed to initialize any Gemini model.\n"
        error_msg += f"Last error: {str(last_error)}\n"
        if available_models:
            error_msg += f"\nAvailable models that support generateContent:\n"
            for m in available_models[:10]:
                error_msg += f"  - {m}\n"
        else:
            error_msg += "\nCould not retrieve list of available models. "
            error_msg += "Please check your API key and ensure it's valid.\n"
        error_msg += "\nTried models: " + ", ".join(models_to_try[:5])
        raise Exception(error_msg)

    def generate_questions(self, skill_name: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate diagnostic questions for a skill using Gemini."""
        prompt = f"""Generate {num_questions} diagnostic questions for assessing knowledge in "{skill_name}".

Requirements:
1. Mix of Multiple Choice Questions (MCQ) and Short Answer Questions
2. Questions should be progressively challenging
3. Return ONLY a valid JSON array with this exact structure:
[
  {{
    "type": "mcq" or "short_answer",
    "question": "question text",
    "options": ["option1", "option2", "option3", "option4"] (only for MCQ),
    "correct_answer": "correct answer text"
  }},
  ...
]

For MCQ questions, include 4 options. For short_answer questions, omit the "options" field.
Return ONLY the JSON array, no additional text or markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            
            # Handle different response formats
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                response_text = response.candidates[0].content.parts[0].text.strip()
            else:
                raise Exception("Unexpected response format from Gemini API")
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            questions = json.loads(response_text)
            return questions
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text[:200]}")
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")

    def evaluate_answers(self, skill_name: str, questions: List[Dict], 
                        user_answers: List[str]) -> Dict[str, Any]:
        """Evaluate user answers using Gemini and return structured evaluation."""
        prompt = f"""Evaluate the following quiz answers for the skill "{skill_name}".

Questions and User Answers:
{json.dumps([{"question": q.get("question", ""), "type": q.get("type", ""), "user_answer": ans} 
             for q, ans in zip(questions, user_answers)], indent=2)}

Return ONLY a valid JSON object with this exact structure:
{{
  "overall_score": <number between 0 and 100>,
  "question_wise_breakdown": [
    {{
      "question_index": <0-based index>,
      "score": <number between 0 and 100>,
      "feedback": "detailed feedback for this answer"
    }},
    ...
  ],
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "study_recommendations": ["recommendation1", "recommendation2", ...]
}}

Return ONLY the JSON object, no additional text or markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            
            # Handle different response formats
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                response_text = response.candidates[0].content.parts[0].text.strip()
            else:
                raise Exception("Unexpected response format from Gemini API")
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            evaluation = json.loads(response_text)
            return evaluation
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text[:200]}")
        except Exception as e:
            raise Exception(f"Error evaluating answers: {str(e)}")


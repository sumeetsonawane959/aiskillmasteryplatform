"""
Utility functions for the application.
"""
import json
import os
from typing import List, Dict, Any


def load_skills() -> List[str]:
    """Load skills from skills.json file."""
    if os.path.exists("skills.json"):
        with open("skills.json", "r") as f:
            data = json.load(f)
            return data.get("skills", [])
    return []


def save_skill(skill_name: str) -> bool:
    """Add a new skill to skills.json."""
    skills = load_skills()
    if skill_name not in skills:
        skills.append(skill_name)
        with open("skills.json", "w") as f:
            json.dump({"skills": skills}, f, indent=2)
        return True
    return False


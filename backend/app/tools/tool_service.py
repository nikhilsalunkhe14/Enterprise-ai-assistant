import random
from typing import Dict

class ToolService:

    def generate_project_document(self, project_name: str) -> Dict:
        return {
            "document_type": "Project Plan",
            "project_name": project_name,
            "sections": [
                "Executive Summary",
                "Scope",
                "Timeline",
                "Resources",
                "Risk Management",
                "Deliverables"
            ],
            "status": "Generated Successfully"
        }

    def calculate_risk_score(self, probability: int, impact: int) -> Dict:
        score = probability * impact

        if score >= 15:
            level = "High"
        elif score >= 8:
            level = "Medium"
        else:
            level = "Low"

        return {
            "risk_score": score,
            "risk_level": level
        }

    def estimate_timeline(self, complexity: str, team_size: int) -> Dict:
        base_weeks = {
            "low": 4,
            "medium": 8,
            "high": 16
        }

        weeks = base_weeks.get(complexity.lower(), 8)
        adjusted = max(weeks - team_size // 2, 2)

        return {
            "estimated_duration_weeks": adjusted,
            "complexity": complexity,
            "team_size": team_size
        }

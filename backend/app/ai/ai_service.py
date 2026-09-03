import json
import re
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

from app.ai.ai_client import AIClient, AIClientError, AIConfigurationError

logger = logging.getLogger(__name__)

class AIAnalysisOutput(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    recommended_skills: List[str] = Field(default_factory=list)
    job_readiness: float = Field(default=0.0, ge=0.0, le=100.0)
    summary: str = Field(default="")

class AIService:
    """
    High-level AI Service for SkillPulse.
    Encapsulates prompt engineering, external API communication,
    Pydantic schema validation, and resilient error recovery.
    """

    def __init__(self, client: Optional[AIClient] = None):
        self.client = client or AIClient()

    def analyze_trainee_skill_gap(
        self,
        trainee_skills: List[str],
        course_skills: Optional[List[str]] = None,
        assessment_scores: Optional[Dict[str, float]] = None,
        certifications: Optional[List[str]] = None,
        target_role: str = "Software Engineer",
    ) -> Dict[str, Any]:
        course_skills = course_skills or []
        assessment_scores = assessment_scores or {}
        certifications = certifications or []
        """
        Analyzes trainee skills against industry target role.
        Validates the output through Pydantic.
        Never fabricates results.
        """
        return self._do_analyze(trainee_skills, course_skills, assessment_scores, certifications, target_role)

    def analyze_skill_gap(self, *args, **kwargs):
        return self.analyze_trainee_skill_gap(*args, **kwargs)

    def _do_analyze(
        self,
        trainee_skills: List[str],
        course_skills: List[str],
        assessment_scores: Dict[str, float],
        certifications: List[str],
        target_role: str,
    ) -> Dict[str, Any]:
        if not self.client.is_configured():
            return {
                "available": False,
                "error": "AI API is not configured. Please provide GROQ_API_KEY or AI_API_KEY in the environment.",
                "strengths": [],
                "skill_gaps": [],
                "recommended_skills": [],
                "job_readiness": 0.0,
                "summary": "AI Skill-Gap analysis requires an active GROQ_API_KEY or AI_API_KEY. Configure it to enable automated longitudinal analysis."
            }

        prompt = self._build_prompt(
            trainee_skills=trainee_skills,
            course_skills=course_skills,
            assessment_scores=assessment_scores,
            certifications=certifications,
            target_role=target_role
        )

        try:
            raw_response = self.client.generate_json_response(prompt)
            parsed_data = self._clean_and_parse_json(raw_response)
            validated = AIAnalysisOutput.model_validate(parsed_data)
            result = validated.model_dump()
            result["available"] = True
            return result
        except ValidationError as val_err:
            logger.error("AI response failed Pydantic validation: %s", val_err)
            return {
                "available": False,
                "error": f"AI model response did not conform to required schema: {str(val_err)[:150]}",
                "strengths": [],
                "skill_gaps": [],
                "recommended_skills": [],
                "job_readiness": 0.0,
                "summary": "Unable to validate AI output schema."
            }
        except AIClientError as client_err:
            logger.error("AI Client error occurred: %s", client_err)
            return {
                "available": False,
                "error": str(client_err),
                "strengths": [],
                "skill_gaps": [],
                "recommended_skills": [],
                "job_readiness": 0.0,
                "summary": f"AI service unavailable: {str(client_err)}"
            }

    def _build_prompt(
        self,
        trainee_skills: List[str],
        course_skills: List[str],
        assessment_scores: Dict[str, float],
        certifications: List[str],
        target_role: str
    ) -> str:
        return f"""You are an expert technical workforce evaluator and career skilling architect.
Analyze the following trainee's profile against the industry requirements for the target role: "{target_role}".

Trainee Data:
- Verified / Self-Reported Skills: {json.dumps(trainee_skills)}
- Course Curriculum Skills: {json.dumps(course_skills)}
- Assessment Scores: {json.dumps(assessment_scores)}
- Certifications Acquired: {json.dumps(certifications)}
- Target Role: {target_role}

Instructions:
1. Identify the trainee's actual current strengths relevant to {target_role}.
2. Identify specific missing skills or critical gaps required for {target_role}.
3. Recommend high-priority skills or modules to bridge these gaps.
4. Calculate a realistic job readiness score from 0.0 to 100.0 based solely on the provided skills and scores.
5. Provide a concise, professional summary (2-3 sentences) describing their readiness.

You MUST reply ONLY with valid JSON conforming exactly to this schema:
{{
  "strengths": ["string"],
  "skill_gaps": ["string"],
  "recommended_skills": ["string"],
  "job_readiness": 0.0,
  "summary": "string"
}}
Do NOT wrap your response with conversational markdown. Provide pure JSON only."""

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        cleaned = raw_text.strip()
        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"```$", "", cleaned)
            cleaned = cleaned.strip()

        # Find first { and last }
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start:end+1]

        return json.loads(cleaned)

from __future__ import annotations

from dataclasses import asdict

from apps.core.llm import enhance_rewrites
from apps.core.scoring import analyze_documents
from apps.core.suggestions import build_insights


def run_analysis(resume_text: str, job_text: str, job_title: str = "") -> dict:
    scorecard = analyze_documents(resume_text, job_text, job_title)
    insights = build_insights(scorecard, resume_text, job_text, job_title)
    insights["rewrites"] = enhance_rewrites(
        resume_text,
        job_text,
        insights["rewrites"],
    )
    payload = {
        "overall_score": scorecard.overall,
        "ats_score": scorecard.ats,
        "keyword_score": scorecard.keyword,
        "semantic_score": scorecard.semantic,
        "structure_score": scorecard.structure,
        "impact_score": scorecard.impact,
        "label": scorecard.label,
        "ats_checks": scorecard.ats_checks,
        "matched_keywords": scorecard.matched_keywords,
        "missing_keywords": scorecard.missing_keywords,
        "matched_skills": scorecard.matched_skills,
        "missing_skills": scorecard.missing_skills,
        "resume_parse": scorecard.resume,
        "job_parse": scorecard.job,
        "insights": insights,
    }
    return payload


def serialize_scorecard(scorecard) -> dict:
    return asdict(scorecard)

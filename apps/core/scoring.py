from __future__ import annotations

from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apps.core.extract import extract_keywords, parse_job, parse_resume


@dataclass
class Scorecard:
    overall: int
    ats: int
    keyword: int
    semantic: int
    structure: int
    impact: int
    label: str
    ats_checks: list[dict] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    resume: dict = field(default_factory=dict)
    job: dict = field(default_factory=dict)


def analyze_documents(resume_text: str, job_text: str, job_title: str = "") -> Scorecard:
    resume = parse_resume(resume_text)
    job = parse_job(job_text, job_title)
    resume_hay = resume_text.lower()

    jd_keywords = job["keywords"] or extract_keywords(job_text)
    matched_kw = [k for k in jd_keywords if k.lower() in resume_hay]
    missing_kw = [k for k in jd_keywords if k.lower() not in resume_hay]
    coverage = 0 if not jd_keywords else round(100 * len(matched_kw) / len(jd_keywords))

    job_skills = job["skills"]
    resume_skills = set(resume["skills"])
    matched_skills = [s for s in job_skills if s in resume_skills]
    missing_skills = [s for s in job_skills if s not in resume_skills]
    skill_cov = 0 if not job_skills else round(100 * len(matched_skills) / len(job_skills))

    keyword_score = round((coverage * 0.6) + (skill_cov * 0.4))
    semantic_score = semantic_similarity(resume_text, job_text)
    ats_score, checks = ats_hygiene(resume_text, resume)
    structure_score = structure_quality(resume)
    impact_score = impact_quality(resume)

    overall = weighted(
        [
            (keyword_score, 0.32),
            (semantic_score, 0.23),
            (ats_score, 0.20),
            (structure_score, 0.13),
            (impact_score, 0.12),
        ]
    )
    return Scorecard(
        overall=overall,
        ats=ats_score,
        keyword=keyword_score,
        semantic=semantic_score,
        structure=structure_score,
        impact=impact_score,
        label=band(overall),
        ats_checks=checks,
        matched_keywords=matched_kw[:20],
        missing_keywords=missing_kw[:20],
        matched_skills=matched_skills[:20],
        missing_skills=missing_skills[:20],
        resume=resume,
        job=job,
    )


def semantic_similarity(resume_text: str, job_text: str) -> int:
    docs = [resume_text[:20000], job_text[:20000]]
    if not docs[0].strip() or not docs[1].strip():
        return 0
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1).fit_transform(docs)
        score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:
        return 0
    return max(0, min(100, round(score * 100)))


def ats_hygiene(text: str, parsed: dict) -> tuple[int, list[dict]]:
    contacts = parsed["contacts"]
    sections = set(parsed["present_sections"])
    checks = [
        _check("Contact email", bool(contacts["emails"]), "ATS parsers need a plain-text email."),
        _check("Phone number", bool(contacts["phones"]), "Add a reachable phone number near the header."),
        _check("Professional summary", "summary" in sections or parsed["word_count"] > 200, "Open with a 3–4 line targeted summary."),
        _check("Experience section", "experience" in sections, "Use a clear Experience / Work History heading."),
        _check("Education section", "education" in sections, "Include Education with degree and dates."),
        _check("Skills section", "skills" in sections or len(parsed["skills"]) >= 6, "List skills as plain text, not icons."),
        _check("Readable length", 280 <= parsed["word_count"] <= 1100, "Aim for 1–2 pages (roughly 300–900 words)."),
        _check("Bullet achievements", parsed["bullet_count"] >= 4, "Use bullets hiring systems can parse line by line."),
        _check("Dates present", bool(parsed["years_mentioned"]), "Add start/end years so tenure is parseable."),
        _check("No first person", not _has_first_person(text), "Drop I/me/my; start bullets with verbs."),
        _check("LinkedIn or portfolio", bool(contacts["linkedin"] or contacts["urls"]), "Add LinkedIn or a portfolio URL."),
        _check("File is text-based", parsed["word_count"] > 120, "Avoid scanned image PDFs and text-in-images."),
    ]
    passed = sum(1 for item in checks if item["status"] == "pass")
    warned = sum(1 for item in checks if item["status"] == "warn")
    score = round(100 * (passed + 0.45 * warned) / max(len(checks), 1))
    return score, checks


def structure_quality(parsed: dict) -> int:
    score = 40
    needed = {"experience", "education", "skills"}
    score += 12 * len(needed.intersection(parsed["present_sections"]))
    if parsed["word_count"] >= 350:
        score += 10
    if parsed["estimated_years"]:
        score += 8
    if parsed["education_signals"]:
        score += 6
    return max(0, min(100, score))


def impact_quality(parsed: dict) -> int:
    bullets = max(parsed["bullet_count"], 1)
    quantified = parsed["quantified_bullets"]
    score = 25 + min(40, round(55 * quantified / bullets))
    score += min(20, len(parsed["action_verbs"]) * 4)
    score -= min(20, len(parsed["weak_bullets"]) * 3)
    if quantified == 0:
        score = min(score, 42)
    return max(0, min(100, score))


def weighted(pairs: list[tuple[int, float]]) -> int:
    total = sum(score * weight for score, weight in pairs)
    return max(0, min(100, round(total)))


def band(score: int) -> str:
    if score >= 85:
        return "Interview likely"
    if score >= 72:
        return "Strong match"
    if score >= 58:
        return "Competitive with edits"
    if score >= 42:
        return "Needs targeting"
    return "Low ATS match"


def _check(label: str, ok: bool, hint: str, warn: bool = False) -> dict:
    if ok:
        status = "pass"
    elif warn:
        status = "warn"
    else:
        status = "fail"
    return {"label": label, "status": status, "hint": hint}


def _has_first_person(text: str) -> bool:
    import re

    return bool(re.search(r"\b(i|me|my|myself)\b", text.lower()))

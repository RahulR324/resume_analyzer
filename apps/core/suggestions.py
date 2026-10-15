from __future__ import annotations

import re

from apps.core.extract import STRONG_VERBS, has_metric, verb_of
from apps.core.scoring import Scorecard

WEAK_SWAPS = {
    "helped": "supported",
    "worked": "delivered",
    "did": "executed",
    "made": "built",
    "handled": "owned",
    "assisted": "partnered on",
    "responsible": "owned",
    "involved": "contributed to",
    "participated": "collaborated on",
    "used": "applied",
    "tried": "piloted",
}


def build_insights(scorecard: Scorecard, resume_text: str, job_text: str, job_title: str = "") -> dict:
    resume = scorecard.resume
    name = resume["contacts"].get("name_guess") or "the candidate"
    target = job_title or scorecard.job.get("title") or "this role"

    strengths = []
    if scorecard.matched_skills:
        strengths.append(f"Already shows {', '.join(scorecard.matched_skills[:5])} — keep these visible in the top third.")
    if resume["quantified_bullets"] >= 3:
        strengths.append("Several bullets include metrics, which ATS and recruiters both reward.")
    if resume["contacts"]["emails"] and resume["contacts"]["phones"]:
        strengths.append("Contact details are parseable, so the file will not fail a basic ATS screen.")
    if scorecard.semantic >= 55:
        strengths.append("Language already overlaps the job description; tightening keywords will compound that.")
    if not strengths:
        strengths.append("There is a usable base resume — targeting it to this job will move the score fastest.")

    gaps = []
    if scorecard.missing_skills:
        gaps.append(
            {
                "title": "Skill gaps vs the posting",
                "detail": "Missing: " + ", ".join(scorecard.missing_skills[:8]),
                "action": "Only add skills you can defend in an interview. Put true matches in Skills and one bullet each.",
            }
        )
    if scorecard.missing_keywords:
        gaps.append(
            {
                "title": "Keywords the ATS will hunt for",
                "detail": ", ".join(scorecard.missing_keywords[:10]),
                "action": "Mirror the employer's phrasing in Summary and the most relevant job bullet.",
            }
        )
    if resume["quantified_bullets"] < 3:
        gaps.append(
            {
                "title": "Impact is hard to measure",
                "detail": "Few bullets include numbers, %, time, or scale.",
                "action": "Add team size, latency, revenue, tickets, users, or cycle time even as ranges.",
            }
        )
    failed = [c for c in scorecard.ats_checks if c["status"] == "fail"]
    if failed:
        gaps.append(
            {
                "title": "ATS hygiene failures",
                "detail": ", ".join(item["label"] for item in failed[:6]),
                "action": failed[0]["hint"],
            }
        )

    placements = []
    for keyword in scorecard.missing_keywords[:8]:
        placements.append(
            {
                "keyword": keyword,
                "where": _placement_for(keyword),
                "example": _insertion_example(keyword, target),
            }
        )

    rewrites = rewrite_bullets(resume.get("bullets") or resume.get("weak_bullets") or [], scorecard)

    cover_letter = draft_cover_letter(name, target, scorecard, job_text)
    interview = interview_pack(scorecard, target)

    next_actions = _next_actions(scorecard)
    return {
        "strengths": strengths[:5],
        "gaps": gaps[:6],
        "keyword_placements": placements,
        "rewrites": rewrites[:6],
        "cover_letter": cover_letter,
        "interview_prep": interview,
        "next_actions": next_actions,
        "summary_line": (
            f"{scorecard.label}: {scorecard.overall}/100 overall, "
            f"{scorecard.keyword}/100 keyword coverage, {scorecard.ats}/100 ATS hygiene."
        ),
    }


def rewrite_bullets(bullets: list[str], scorecard: Scorecard) -> list[dict]:
    keywords = (scorecard.missing_keywords or scorecard.matched_keywords)[:6]
    out = []
    for bullet in bullets[:8]:
        improved = _rewrite_line(bullet, keywords)
        if improved.lower() == bullet.lower():
            continue
        out.append({"original": bullet, "improved": improved, "why": _why(bullet)})
    if not out and bullets:
        sample = bullets[0]
        kw = keywords[0] if keywords else "the team's core stack"
        out.append(
            {
                "original": sample,
                "improved": f"Delivered measurable outcomes with {kw}: {sample.rstrip('.')}, improving cycle time by 20%.",
                "why": "Add a tool the posting names and a concrete result.",
            }
        )
    return out


def _rewrite_line(bullet: str, keywords: list[str]) -> str:
    text = bullet.strip()
    verb = verb_of(text)
    if verb in WEAK_SWAPS:
        text = re.sub(r"^\W*" + re.escape(verb), WEAK_SWAPS[verb].capitalize(), text, count=1, flags=re.I)
    elif verb and verb[0].islower():
        text = text[0].upper() + text[1:]
    if not has_metric(text):
        text = text.rstrip(".") + ", cutting turnaround time by 18%."
    injectable = [k for k in keywords if k.lower() not in text.lower()]
    if injectable:
        text = text.rstrip(".") + f" using {injectable[0]}."
    if verb_of(text) not in STRONG_VERBS and verb_of(text) not in WEAK_SWAPS.values():
        text = "Delivered " + text[0].lower() + text[1:]
    return text


def _why(bullet: str) -> str:
    reasons = []
    if verb_of(bullet) in WEAK_SWAPS:
        reasons.append("replaced a weak verb")
    if not has_metric(bullet):
        reasons.append("added a measurable outcome")
    reasons.append("aligned phrasing to the job")
    return "; ".join(reasons)


def draft_cover_letter(name: str, target: str, scorecard: Scorecard, job_text: str) -> str:
    skills = ", ".join((scorecard.matched_skills or scorecard.resume.get("skills") or ["relevant experience"])[:5])
    missing = ", ".join(scorecard.missing_skills[:3])
    company_hook = _first_sentence(job_text)
    closing_gap = (
        f"I am actively deepening {missing} and can speak to how I would ramp in the first 90 days."
        if missing
        else "I can contribute in the first 90 days without a long ramp."
    )
    return (
        f"Dear Hiring Team,\n\n"
        f"I am writing to apply for the {target} role. {company_hook} "
        f"My background in {skills} maps directly to the outcomes in your posting, "
        f"and my resume is structured so both recruiters and ATS systems can read that match clearly.\n\n"
        f"Recently I have focused on work that is easy to staff against your requirements: "
        f"shipping measurable improvements, collaborating across functions, and documenting decisions. "
        f"{closing_gap}\n\n"
        f"I would welcome a conversation about how I can help the team hit the goals in this role.\n\n"
        f"Sincerely,\n{name}"
    )


def interview_pack(scorecard: Scorecard, target: str) -> list[dict]:
    questions = [
        {
            "q": f"Walk me through a project that proves you can do {target}.",
            "hint": "Use STAR. End with a metric and the skill the posting cares about most.",
        },
        {
            "q": "Tell me about a time you improved a process others had accepted as slow.",
            "hint": "Name the baseline, the change, and the before/after number.",
        },
    ]
    for skill in scorecard.missing_skills[:3]:
        questions.append(
            {
                "q": f"How would you ramp on {skill} in your first month?",
                "hint": "Be honest. Map adjacent experience, a 30-day learning plan, and a first deliverable.",
            }
        )
    if scorecard.resume.get("weak_bullets"):
        questions.append(
            {
                "q": "This bullet is vague — what actually happened?",
                "hint": scorecard.resume["weak_bullets"][0][:180],
            }
        )
    return questions[:6]


def _next_actions(scorecard: Scorecard) -> list[str]:
    actions = []
    if scorecard.missing_keywords:
        actions.append(f"Add these exact phrases where true: {', '.join(scorecard.missing_keywords[:5])}.")
    if scorecard.ats < 80:
        failed = [c["label"] for c in scorecard.ats_checks if c["status"] == "fail"][:3]
        if failed:
            actions.append("Fix ATS blockers: " + ", ".join(failed) + ".")
    if scorecard.impact < 70:
        actions.append("Rewrite 3 bullets with a verb + metric + tool from the posting.")
    if scorecard.keyword < 65:
        actions.append("Retarget the summary to the job title and top 5 keywords in the first 4 lines.")
    if not actions:
        actions.append("Export a clean PDF (no tables/icons) and apply — this match is already competitive.")
    return actions[:5]


def _placement_for(keyword: str) -> str:
    techish = any(ch in keyword for ch in ("js", ".", "#")) or keyword in {
        "python", "django", "aws", "sql", "react", "docker", "kubernetes", "java",
    }
    if techish:
        return "Skills + one experience bullet"
    if keyword in {"leadership", "communication", "stakeholder", "agile", "scrum"}:
        return "Summary and a collaboration bullet"
    return "Summary or the most relevant role"


def _insertion_example(keyword: str, target: str) -> str:
    return f"Owned {keyword} workstreams for a {target} team, improving delivery predictability."


def _first_sentence(text: str) -> str:
    chunk = " ".join(text.split())[:280]
    parts = re.split(r"(?<=[.!?])\s+", chunk)
    sentence = parts[0] if parts else chunk
    if len(sentence) < 40:
        return "This role is a strong fit for my background."
    return sentence

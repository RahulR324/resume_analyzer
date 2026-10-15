from __future__ import annotations

import logging

import httpx
from django.conf import settings

logger = logging.getLogger("apps.llm")


def enhance_rewrites(resume_excerpt: str, job_excerpt: str, current_rewrites: list[dict]) -> list[dict]:
    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key or not current_rewrites:
        return current_rewrites

    bullets = "\n".join(f"- {item['original']}" for item in current_rewrites)
    prompt = (
        "Rewrite these resume bullets for ATS and a recruiter. "
        "Keep truthfulness. Start with a strong verb, add a metric if plausible as a placeholder in [brackets], "
        "and naturally include job keywords.\n\n"
        f"JOB:\n{job_excerpt[:2500]}\n\nRESUME EXCERPT:\n{resume_excerpt[:2500]}\n\nBULLETS:\n{bullets}\n\n"
        "Return one improved bullet per line, no numbering."
    )
    try:
        response = httpx.post(
            f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": settings.OPENAI_MODEL,
                "temperature": 0.4,
                "messages": [
                    {"role": "system", "content": "You are a precise resume editor. Never invent employers or tools."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except Exception:
        logger.warning("LLM rewrite skipped; using rule-based suggestions", exc_info=True)
        return current_rewrites

    lines = [line.lstrip("-• ").strip() for line in content.splitlines() if line.strip()]
    upgraded = []
    for index, item in enumerate(current_rewrites):
        improved = lines[index] if index < len(lines) else item["improved"]
        upgraded.append({**item, "improved": improved, "source": "model"})
    return upgraded

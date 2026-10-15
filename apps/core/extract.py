from __future__ import annotations

import re
from collections import Counter

from apps.core.skills import ALL_SKILLS, normalize_skill

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{3}\)?[\s\-.]?)\d{3}[\s\-.]?\d{4}")
URL_RE = re.compile(r"https?://[^\s)]+|www\.[^\s)]+", re.I)
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s)]+", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[^\s)]+", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
DEGREE_RE = re.compile(
    r"\b(b\.?tech|b\.?e\.?|b\.?s\.?|b\.?sc|m\.?tech|m\.?s\.?|m\.?sc|mba|ph\.?d|bachelor|master|associate)\b",
    re.I,
)
SECTION_ALIASES = {
    "summary": "summary",
    "objective": "summary",
    "profile": "summary",
    "about": "summary",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",
    "work history": "experience",
    "education": "education",
    "academic": "education",
    "skills": "skills",
    "technical skills": "skills",
    "core competencies": "skills",
    "projects": "projects",
    "certifications": "certifications",
    "certificates": "certifications",
    "awards": "awards",
    "achievements": "awards",
    "languages": "languages",
}
HEADER_RE = re.compile(
    r"^(summary|objective|profile|about|experience|work experience|professional experience|"
    r"employment|work history|education|academic|skills|technical skills|core competencies|"
    r"projects|certifications|certificates|awards|achievements|languages)\s*:?$",
    re.I,
)
WEAK_VERBS = {
    "helped", "worked", "did", "made", "handled", "assisted", "responsible",
    "involved", "tried", "used", "participated",
}
STRONG_VERBS = {
    "led", "built", "designed", "implemented", "shipped", "launched", "owned",
    "improved", "reduced", "increased", "automated", "migrated", "optimized",
    "architected", "delivered", "scaled", "mentored", "negotiated",
}


def parse_resume(text: str) -> dict:
    contacts = extract_contacts(text)
    sections = split_sections(text)
    skills = extract_skills(text)
    bullets = extract_bullets(text)
    return {
        "contacts": contacts,
        "sections": {key: value[:4000] for key, value in sections.items()},
        "present_sections": sorted(sections.keys()),
        "skills": skills,
        "education_signals": DEGREE_RE.findall(text),
        "years_mentioned": sorted(set(YEAR_RE.findall(text))),
        "estimated_years": estimate_years(text),
        "word_count": len(text.split()),
        "bullet_count": len(bullets),
        "bullets": bullets[:40],
        "weak_bullets": [b for b in bullets if is_weak_bullet(b)][:12],
        "quantified_bullets": sum(1 for b in bullets if has_metric(b)),
        "action_verbs": sorted({verb_of(b) for b in bullets if verb_of(b) in STRONG_VERBS}),
    }


def parse_job(text: str, title: str = "") -> dict:
    skills = extract_skills(text)
    keywords = extract_keywords(text, extra=skills)
    return {
        "title": title.strip(),
        "skills": skills,
        "keywords": keywords,
        "word_count": len(text.split()),
        "seniority": detect_seniority(f"{title}\n{text}"),
    }


def extract_contacts(text: str) -> dict:
    emails = EMAIL_RE.findall(text)
    phones = [p.strip() for p in PHONE_RE.findall(text)]
    return {
        "emails": unique(emails)[:3],
        "phones": unique(phones)[:2],
        "linkedin": unique(LINKEDIN_RE.findall(text))[:1],
        "github": unique(GITHUB_RE.findall(text))[:1],
        "urls": unique(URL_RE.findall(text))[:6],
        "name_guess": guess_name(text),
    }


def split_sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    buckets: dict[str, list[str]] = {"preamble": []}
    current = "preamble"
    for line in lines:
        stripped = line.strip()
        match = HEADER_RE.match(stripped)
        if match:
            current = SECTION_ALIASES[match.group(1).lower()]
            buckets.setdefault(current, [])
            continue
        buckets.setdefault(current, []).append(line)
    return {key: "\n".join(value).strip() for key, value in buckets.items() if "".join(value).strip()}


def extract_skills(text: str) -> list[str]:
    haystack = f" {text.lower()} "
    found: list[str] = []
    for skill in sorted(ALL_SKILLS, key=len, reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, haystack):
            found.append(skill)
    # aliases / short tokens
    tokens = re.findall(r"[a-zA-Z+#.]{2,}", text.lower())
    for token in tokens:
        normalized = normalize_skill(token)
        if normalized in ALL_SKILLS and normalized not in found:
            found.append(normalized)
    return found[:80]


def extract_keywords(text: str, extra: list[str] | None = None, limit: int = 28) -> list[str]:
    stop = STOPWORDS
    counts: Counter[str] = Counter()
    for raw in re.findall(r"[A-Za-z][A-Za-z+\-#.]{2,}", text.lower()):
        token = raw.strip(".-")
        if token in stop or len(token) < 3:
            continue
        counts[token] += 1
    keywords = [word for word, _ in counts.most_common(limit)]
    for skill in extra or []:
        if skill not in keywords:
            keywords.insert(0, skill)
    # de-dupe preserving order
    seen = set()
    ordered = []
    for item in keywords:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered[:limit]


def extract_bullets(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^([\-•*●▪]|o |\d+[.)])\s+", stripped):
            cleaned = re.sub(r"^([\-•*●▪]|o |\d+[.)])\s+", "", stripped).strip()
            if len(cleaned) > 24:
                bullets.append(cleaned)
        elif stripped[:1].isupper() and 40 <= len(stripped) <= 280 and stripped.endswith((".", ";")):
            if any(stripped.lower().startswith(v) for v in STRONG_VERBS | WEAK_VERBS):
                bullets.append(stripped)
    return unique(bullets)


def estimate_years(text: str) -> int | None:
    match = re.search(r"(\d{1,2})\+?\s+years?", text.lower())
    if match:
        return min(int(match.group(1)), 40)
    full_years = [int(m.group(0)) for m in YEAR_RE.finditer(text)]
    if len(full_years) >= 2:
        span = max(full_years) - min(full_years)
        if 0 < span <= 40:
            return span
    return None


def detect_seniority(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("principal", "staff", "director", "head of", "vp ")):
        return "staff+"
    if any(term in lowered for term in ("senior", "sr.", "lead")):
        return "senior"
    if any(term in lowered for term in ("junior", "intern", "entry", "graduate")):
        return "junior"
    return "mid"


def is_weak_bullet(bullet: str) -> bool:
    first = verb_of(bullet)
    return first in WEAK_VERBS or not has_metric(bullet)


def has_metric(text: str) -> bool:
    return bool(re.search(r"\d", text))


def verb_of(bullet: str) -> str:
    first = re.split(r"\s+", bullet.strip().lower(), maxsplit=1)[0]
    return re.sub(r"[^a-z]", "", first)


def guess_name(text: str) -> str:
    for line in text.splitlines()[:8]:
        candidate = line.strip()
        if not candidate or EMAIL_RE.search(candidate) or PHONE_RE.search(candidate):
            continue
        if HEADER_RE.match(candidate):
            continue
        words = candidate.split()
        if 2 <= len(words) <= 4 and all(w[:1].isupper() for w in words if w.isalpha()):
            return candidate
    return ""


def unique(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        key = item.strip()
        if key and key.lower() not in seen:
            seen.add(key.lower())
            out.append(key)
    return out


STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will", "this", "that",
    "from", "have", "has", "not", "but", "all", "any", "can", "able", "into", "onto",
    "job", "role", "work", "team", "using", "used", "plus", "etc", "such", "more",
    "than", "then", "them", "they", "their", "about", "over", "under", "per", "via",
    "including", "include", "required", "requirements", "responsibility", "responsibilities",
    "experience", "years", "year", "strong", "good", "well", "must", "should", "other",
    "skills", "skill", "knowledge", "ability", "preferred", "qualification", "qualifications",
}

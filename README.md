# ResumeLens — AI Resume Analyzer

Production-ready Django app that scores a resume against a job posting the way ATS parsers and recruiters actually read files: **keyword coverage, semantic overlap, ATS hygiene, structure, and proof of impact**.

## What you get

- Accounts, private resume/job storage, and match history
- PDF / DOCX / TXT parsing with file-type and size validation
- Skill extraction, keyword gap map, and placement suggestions
- ATS checklist (contact, headings, dates, length, first person, bullets)
- Bullet rewrites, cover-letter draft, and interview prompts
- Optional OpenAI-compatible rewrite upgrade via `OPENAI_API_KEY`
- Rate-limited analysis, structured logging, WhiteNoise static files, Docker

## Quick start (local)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000`. Default local database is SQLite (`DB_ENGINE=sqlite`).

## PostgreSQL

Set in `.env`:

```
DB_ENGINE=postgres
DB_NAME=ai_project
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=5432
```

Or run the stack:

```bash
docker compose up --build
```

## Tests

```bash
python manage.py test
```

## Production notes

- Set `DEBUG=False`, a long `SECRET_KEY`, real `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.
- Serve behind TLS and set `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE`.
- Run `collectstatic` and `gunicorn config.wsgi:application`.
- Uploaded resumes live in `MEDIA_ROOT` and are scoped to the signed-in user.

Optional model rewrites: set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`, `OPENAI_BASE_URL`).

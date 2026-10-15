from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from apps.core.extract import parse_resume
from apps.core.parsing import extract_text_from_bytes, validate_resume_file
from apps.core.pipeline import run_analysis


RESUME = """
Ada Lovelace
ada@example.com
+1 415 555 0100
https://linkedin.com/in/ada
https://github.com/ada

Summary
Senior Python engineer with 6 years of experience shipping Django APIs and data products.

Skills
Python, Django, PostgreSQL, Docker, AWS, REST, Git, Leadership

Experience
Software Engineer, Analytical Engines, 2019 - 2025
- Built Django services used by 40,000 monthly researchers
- Reduced API latency 35% by introducing Redis caching
- Led a team of 4 engineers delivering machine learning features

Education
B.S. Mathematics, 2018
"""

JOB = """
We are hiring a Senior Python Engineer to own Django microservices on AWS.
Requirements: Python, Django, Docker, Kubernetes, PostgreSQL, CI/CD, REST APIs,
and experience leading engineers. Machine learning familiarity is a plus.
"""


class ParserTests(SimpleTestCase):
    def test_rejects_bad_extension(self):
        class Fake:
            name = "photo.png"
            size = 10

            def read(self, n=None):
                return b"not-an-image"

            def seek(self, n):
                return None

            def tell(self):
                return 0

        with self.assertRaises(ValidationError):
            validate_resume_file(Fake())

    def test_txt_extract(self):
        text = extract_text_from_bytes(RESUME.encode(), ".txt")
        self.assertIn("Ada Lovelace", text)


class ScoringTests(SimpleTestCase):
    def test_strong_resume_scores_well(self):
        payload = run_analysis(RESUME, JOB, "Senior Python Engineer")
        self.assertGreaterEqual(payload["overall_score"], 55)
        self.assertIn("python", payload["matched_skills"])
        self.assertTrue(payload["insights"]["rewrites"] or payload["insights"]["next_actions"])
        contacts = parse_resume(RESUME)["contacts"]
        self.assertTrue(contacts["emails"])
        self.assertTrue(contacts["phones"])

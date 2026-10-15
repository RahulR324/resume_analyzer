from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.core.pipeline import run_analysis
from apps.resumes.models import Resume

User = get_user_model()

RESUME_TEXT = (
    "Jordan Lee\njordan@example.com\n555-222-0101\n\n"
    "Summary\nProduct manager with SQL, analytics, and stakeholder management.\n\n"
    "Experience\nPM, Northwind, 2020-2025\n- Launched a billing workflow used by 120 customers\n"
    "- Improved onboarding completion 22% using A/B testing\n\n"
    "Education\nMBA 2019\n\nSkills\nSQL, Excel, Jira, Agile, Communication"
)


class AnalysisFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("jordan", "jordan@example.com", "a-quite-Long-pass-99")
        self.client.force_login(self.user)
        self.resume = Resume.objects.create(
            user=self.user,
            title="Jordan PM",
            file=SimpleUploadedFile("jordan.txt", RESUME_TEXT.encode(), content_type="text/plain"),
            original_name="jordan.txt",
            file_type=".txt",
            extracted_text=RESUME_TEXT,
            parsed_data={},
            word_count=40,
            is_primary=True,
        )

    def test_dashboard_ok(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_create_analysis(self):
        response = self.client.post(
            reverse("analysis:create"),
            {
                "resume": self.resume.pk,
                "job_title": "Product Manager",
                "job_company": "Acme",
                "job_description": "Seeking a product manager with SQL, agile, roadmap, and stakeholder management. A/B testing required.",
                "save_job": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.analyses.count(), 1)
        analysis = self.user.analyses.first()
        self.assertGreater(analysis.overall_score, 0)
        detail = self.client.get(analysis.get_absolute_url())
        self.assertContains(detail, "Keyword map")

    def test_pipeline_is_deterministic_enough(self):
        first = run_analysis(RESUME_TEXT, "SQL agile roadmap stakeholder A/B testing product manager", "PM")
        second = run_analysis(RESUME_TEXT, "SQL agile roadmap stakeholder A/B testing product manager", "PM")
        self.assertEqual(first["overall_score"], second["overall_score"])

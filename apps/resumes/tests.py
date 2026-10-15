from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ResumeUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("pat", "pat@example.com", "a-quite-Long-pass-99")
        self.client.force_login(self.user)

    def test_upload_txt(self):
        body = (
            "Pat Kim\npat@example.com\n415-555-0199\n\nSummary\nDesigner with Figma and user research.\n\n"
            "Experience\nDesigner, Studio, 2021-2025\n- Designed onboarding used by 8,000 people\n\n"
            "Education\nB.A. 2020\n\nSkills\nFigma, UX, Prototyping, Communication\n"
        ) * 2
        response = self.client.post(
            reverse("resumes:upload"),
            {
                "title": "Pat design resume",
                "file": SimpleUploadedFile("pat.txt", body.encode(), content_type="text/plain"),
                "make_primary": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        resume = self.user.resumes.get()
        self.assertGreater(resume.word_count, 20)
        self.assertIn("figma", resume.parsed_data.get("skills", []))

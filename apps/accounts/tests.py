from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthTests(TestCase):
    def test_register_creates_profile(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "full_name": "New User",
                "password1": "a-quite-Long-pass-99",
                "password2": "a-quite-Long-pass-99",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.full_name, "New User")

    def test_home_ok(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("healthz")).status_code, 200)

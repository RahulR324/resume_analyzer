from django.conf import settings
from django.db import models


def resume_upload_to(instance, filename: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ".-_" else "_" for ch in filename)[:80]
    return f"resumes/{instance.user_id}/{safe}"


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to=resume_upload_to)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=12)
    extracted_text = models.TextField()
    parsed_data = models.JSONField(default=dict, blank=True)
    word_count = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_primary", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("resumes:detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if self.is_primary:
            Resume.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

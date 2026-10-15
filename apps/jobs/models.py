from django.conf import settings
from django.db import models


class JobTarget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=180)
    company = models.CharField(max_length=180, blank=True)
    location = models.CharField(max_length=160, blank=True)
    source_url = models.URLField(blank=True)
    description = models.TextField()
    parsed_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.company:
            return f"{self.title} · {self.company}"
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("jobs:detail", args=[self.pk])

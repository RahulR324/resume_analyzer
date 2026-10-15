from django.conf import settings
from django.db import models


class Analysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analyses")
    resume = models.ForeignKey("resumes.Resume", on_delete=models.CASCADE, related_name="analyses")
    job = models.ForeignKey(
        "jobs.JobTarget",
        on_delete=models.SET_NULL,
        related_name="analyses",
        null=True,
        blank=True,
    )
    job_title = models.CharField(max_length=180)
    job_company = models.CharField(max_length=180, blank=True)
    job_description = models.TextField()
    overall_score = models.PositiveSmallIntegerField(default=0)
    ats_score = models.PositiveSmallIntegerField(default=0)
    keyword_score = models.PositiveSmallIntegerField(default=0)
    semantic_score = models.PositiveSmallIntegerField(default=0)
    structure_score = models.PositiveSmallIntegerField(default=0)
    impact_score = models.PositiveSmallIntegerField(default=0)
    label = models.CharField(max_length=64, blank=True)
    report = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "analyses"

    def __str__(self) -> str:
        return f"{self.job_title} ({self.overall_score})"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("analysis:detail", args=[self.pk])

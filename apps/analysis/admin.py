from django.contrib import admin

from .models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("job_title", "user", "overall_score", "ats_score", "keyword_score", "created_at")
    list_filter = ("label",)
    search_fields = ("job_title", "job_company", "user__username")
    readonly_fields = ("report",)

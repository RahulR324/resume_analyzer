from django.contrib import admin

from .models import JobTarget


@admin.register(JobTarget)
class JobTargetAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "user", "created_at")
    search_fields = ("title", "company", "description")

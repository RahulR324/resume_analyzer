from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "file_type", "word_count", "is_primary", "created_at")
    search_fields = ("title", "original_name", "user__username")
    list_filter = ("file_type", "is_primary")
    readonly_fields = ("extracted_text", "parsed_data", "word_count")

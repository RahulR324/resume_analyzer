from django import forms

from apps.core.extract import parse_resume
from apps.core.parsing import extract_text_from_upload, validate_resume_file

from .models import Resume


class ResumeUploadForm(forms.ModelForm):
    file = forms.FileField()
    make_primary = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Resume
        fields = ("title", "file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "input", "placeholder": "e.g. Product manager — 2026"})
        self.fields["file"].widget.attrs.update({"class": "input", "accept": ".pdf,.docx,.txt"})

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        self._suffix = validate_resume_file(uploaded)
        self._text = extract_text_from_upload(uploaded, self._suffix)
        return uploaded

    def save(self, user, commit=True):
        resume = super().save(commit=False)
        resume.user = user
        resume.original_name = self.cleaned_data["file"].name
        resume.file_type = self._suffix
        resume.extracted_text = self._text
        parsed = parse_resume(self._text)
        resume.parsed_data = parsed
        resume.word_count = parsed["word_count"]
        if not resume.title:
            resume.title = parsed["contacts"].get("name_guess") or "Untitled resume"
        resume.is_primary = bool(self.cleaned_data.get("make_primary")) or not user.resumes.exists()
        if commit:
            resume.save()
        return resume

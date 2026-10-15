from django import forms

from apps.core.extract import parse_job

from .models import JobTarget


class JobTargetForm(forms.ModelForm):
    class Meta:
        model = JobTarget
        fields = ("title", "company", "location", "source_url", "description")
        widgets = {
            "title": forms.TextInput(attrs={"class": "input", "placeholder": "Role title"}),
            "company": forms.TextInput(attrs={"class": "input", "placeholder": "Company"}),
            "location": forms.TextInput(attrs={"class": "input", "placeholder": "Location or Remote"}),
            "source_url": forms.URLInput(attrs={"class": "input", "placeholder": "https://..."}),
            "description": forms.Textarea(
                attrs={"class": "input input--area", "rows": 12, "placeholder": "Paste the full job description"}
            ),
        }

    def save(self, user, commit=True):
        job = super().save(commit=False)
        job.user = user
        job.parsed_data = parse_job(job.description, job.title)
        if commit:
            job.save()
        return job

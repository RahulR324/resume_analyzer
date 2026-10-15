from django import forms

from apps.jobs.models import JobTarget
from apps.resumes.models import Resume


class AnalysisForm(forms.Form):
    resume = forms.ModelChoiceField(queryset=Resume.objects.none())
    job = forms.ModelChoiceField(queryset=JobTarget.objects.none(), required=False)
    job_title = forms.CharField(max_length=180, required=False)
    job_company = forms.CharField(max_length=180, required=False)
    job_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "input input--area", "rows": 10, "placeholder": "Or paste a new job description"}),
    )
    save_job = forms.BooleanField(required=False, initial=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["resume"].queryset = user.resumes.all()
        self.fields["job"].queryset = user.jobs.all()
        self.fields["job"].required = False
        self.fields["resume"].widget.attrs["class"] = "input"
        self.fields["job"].widget.attrs["class"] = "input"
        self.fields["job_title"].widget.attrs.update({"class": "input", "placeholder": "Role title"})
        self.fields["job_company"].widget.attrs.update({"class": "input", "placeholder": "Company (optional)"})

    def clean(self):
        cleaned = super().clean()
        job = cleaned.get("job")
        description = (cleaned.get("job_description") or "").strip()
        title = (cleaned.get("job_title") or "").strip()
        if job:
            cleaned["job_title"] = job.title
            cleaned["job_company"] = job.company
            cleaned["job_description"] = job.description
            return cleaned
        if not description or not title:
            raise forms.ValidationError("Choose a saved job or paste a title plus the full description.")
        cleaned["job_description"] = description
        cleaned["job_title"] = title
        return cleaned

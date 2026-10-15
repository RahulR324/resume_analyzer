from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, FormView, ListView, View

from apps.core.extract import parse_job
from apps.core.pipeline import run_analysis
from apps.jobs.models import JobTarget

from .forms import AnalysisForm
from .models import Analysis


class AnalysisListView(LoginRequiredMixin, ListView):
    template_name = "analysis/list.html"
    context_object_name = "analyses"

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user).select_related("resume", "job")


class AnalysisCreateView(LoginRequiredMixin, FormView):
    template_name = "analysis/form.html"
    form_class = AnalysisForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        resume_id = self.request.GET.get("resume")
        job_id = self.request.GET.get("job")
        if resume_id:
            initial["resume"] = resume_id
        if job_id:
            initial["job"] = job_id
        elif not resume_id:
            primary = self.request.user.resumes.filter(is_primary=True).first()
            if primary:
                initial["resume"] = primary.pk
        return initial

    def form_valid(self, form):
        if not _allow_analysis(self.request.user.id):
            messages.error(self.request, "Hourly analysis limit reached. Try again later.")
            return self.form_invalid(form)

        data = form.cleaned_data
        resume = data["resume"]
        job = data.get("job")
        title = data["job_title"]
        company = data.get("job_company") or ""
        description = data["job_description"]

        if not job and data.get("save_job"):
            job = JobTarget.objects.create(
                user=self.request.user,
                title=title,
                company=company,
                description=description,
                parsed_data=parse_job(description, title),
            )

        payload = run_analysis(resume.extracted_text, description, title)
        analysis = Analysis.objects.create(
            user=self.request.user,
            resume=resume,
            job=job,
            job_title=title,
            job_company=company or (job.company if job else ""),
            job_description=description,
            overall_score=payload["overall_score"],
            ats_score=payload["ats_score"],
            keyword_score=payload["keyword_score"],
            semantic_score=payload["semantic_score"],
            structure_score=payload["structure_score"],
            impact_score=payload["impact_score"],
            label=payload["label"],
            report=payload,
        )
        messages.success(self.request, "Match complete. Review gaps before you apply.")
        return redirect(analysis)


class AnalysisDetailView(LoginRequiredMixin, DetailView):
    template_name = "analysis/detail.html"
    context_object_name = "analysis"

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user).select_related("resume", "job")


class AnalysisReportView(LoginRequiredMixin, DetailView):
    template_name = "analysis/report.html"
    context_object_name = "analysis"

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user).select_related("resume", "job")


class AnalysisRerunView(LoginRequiredMixin, View):
    def post(self, request, pk):
        original = get_object_or_404(Analysis, pk=pk, user=request.user)
        if not _allow_analysis(request.user.id):
            messages.error(request, "Hourly analysis limit reached.")
            return redirect(original)
        payload = run_analysis(original.resume.extracted_text, original.job_description, original.job_title)
        original.overall_score = payload["overall_score"]
        original.ats_score = payload["ats_score"]
        original.keyword_score = payload["keyword_score"]
        original.semantic_score = payload["semantic_score"]
        original.structure_score = payload["structure_score"]
        original.impact_score = payload["impact_score"]
        original.label = payload["label"]
        original.report = payload
        original.save()
        messages.success(request, "Scores refreshed from the latest resume text.")
        return redirect(original)


def healthz(request):
    return render(request, "healthz.txt", content_type="text/plain")


def _allow_analysis(user_id: int) -> bool:
    key = f"analysis-limit:{user_id}"
    used = cache.get(key, 0)
    limit = getattr(settings, "ANALYSIS_HOURLY_LIMIT", 30)
    if used >= limit:
        return False
    cache.set(key, used + 1, timeout=3600)
    return True

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from .forms import ResumeUploadForm
from .models import Resume


class OwnedQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class ResumeListView(OwnedQuerysetMixin, ListView):
    template_name = "resumes/list.html"
    context_object_name = "resumes"


class ResumeDetailView(OwnedQuerysetMixin, DetailView):
    template_name = "resumes/detail.html"
    context_object_name = "resume"


class ResumeUploadView(LoginRequiredMixin, CreateView):
    form_class = ResumeUploadForm
    template_name = "resumes/upload.html"
    success_url = reverse_lazy("resumes:list")

    def form_valid(self, form):
        form.save(user=self.request.user)
        messages.success(self.request, "Resume parsed. Run a job match to see ATS and skill gaps.")
        return redirect(self.success_url)


class ResumeDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        resume.delete()
        messages.info(request, "Resume removed.")
        return redirect("resumes:list")


class ResumePrimaryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk, user=request.user)
        resume.is_primary = True
        resume.save(update_fields=["is_primary"])
        messages.success(request, "Primary resume updated.")
        return redirect(resume)

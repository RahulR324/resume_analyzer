from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from .forms import JobTargetForm
from .models import JobTarget


class JobQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return JobTarget.objects.filter(user=self.request.user)


class JobListView(JobQuerysetMixin, ListView):
    template_name = "jobs/list.html"
    context_object_name = "jobs"


class JobDetailView(JobQuerysetMixin, DetailView):
    template_name = "jobs/detail.html"
    context_object_name = "job"


class JobCreateView(LoginRequiredMixin, CreateView):
    form_class = JobTargetForm
    template_name = "jobs/form.html"
    success_url = reverse_lazy("jobs:list")

    def form_valid(self, form):
        form.save(user=self.request.user)
        messages.success(self.request, "Job saved. Analyze it against a resume.")
        return redirect("analysis:create")


class JobUpdateView(JobQuerysetMixin, UpdateView):
    form_class = JobTargetForm
    template_name = "jobs/form.html"

    def form_valid(self, form):
        form.save(user=self.request.user)
        messages.success(self.request, "Job updated.")
        return redirect(self.object)


class JobDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        job = get_object_or_404(JobTarget, pk=pk, user=request.user)
        job.delete()
        messages.info(request, "Job removed.")
        return redirect("jobs:list")

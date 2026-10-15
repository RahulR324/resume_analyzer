from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from apps.analysis.models import Analysis

from .forms import LoginForm, ProfileForm, RegisterForm


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Welcome to ResumeLens. Upload a resume to run your first match.")
        return super().form_valid(form)


class SignedInLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class SignedOutLogoutView(LogoutView):
    next_page = reverse_lazy("home")


def home(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return render(request, "landing.html")


@login_required
def dashboard(request):
    from .models import Profile

    Profile.objects.get_or_create(user=request.user)
    resumes = request.user.resumes.all()[:6]
    jobs = request.user.jobs.all()[:6]
    analyses = request.user.analyses.select_related("resume", "job")[:8]
    latest = analyses[0] if analyses else None
    return render(
        request,
        "accounts/dashboard.html",
        {
            "resumes": resumes,
            "jobs": jobs,
            "analyses": analyses,
            "latest": latest,
            "resume_count": request.user.resumes.count(),
            "job_count": request.user.jobs.count(),
            "analysis_count": request.user.analyses.count(),
            "avg_score": _avg_score(request.user),
        },
    )


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/profile.html", {"form": form})


def _avg_score(user) -> int:
    values = Analysis.objects.filter(user=user).values_list("overall_score", flat=True)
    values = list(values)
    if not values:
        return 0
    return round(sum(values) / len(values))

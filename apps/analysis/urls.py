from django.urls import path

from . import views

app_name = "analysis"

urlpatterns = [
    path("", views.AnalysisListView.as_view(), name="list"),
    path("new/", views.AnalysisCreateView.as_view(), name="create"),
    path("<int:pk>/", views.AnalysisDetailView.as_view(), name="detail"),
    path("<int:pk>/report/", views.AnalysisReportView.as_view(), name="report"),
    path("<int:pk>/rerun/", views.AnalysisRerunView.as_view(), name="rerun"),
]

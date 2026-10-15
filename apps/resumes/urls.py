from django.urls import path

from . import views

app_name = "resumes"

urlpatterns = [
    path("", views.ResumeListView.as_view(), name="list"),
    path("upload/", views.ResumeUploadView.as_view(), name="upload"),
    path("<int:pk>/", views.ResumeDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.ResumeDeleteView.as_view(), name="delete"),
    path("<int:pk>/primary/", views.ResumePrimaryView.as_view(), name="primary"),
]

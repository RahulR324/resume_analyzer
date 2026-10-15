from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from apps.accounts.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("healthz", lambda request: HttpResponse("ok", content_type="text/plain"), name="healthz"),
    path("accounts/", include("apps.accounts.urls")),
    path("resumes/", include("apps.resumes.urls")),
    path("jobs/", include("apps.jobs.urls")),
    path("analysis/", include("apps.analysis.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"

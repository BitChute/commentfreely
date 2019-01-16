from django.conf import settings

from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView

from django.contrib import admin


urlpatterns = [
    path("", TemplateView.as_view(template_name="homepage.html"), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("account.urls")),
    path("dashboard/", include('core.urls')),
    path("api/", include('core.api_urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

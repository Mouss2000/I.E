from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('platform/', include('customers.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    # Root serves the frontend SPA
    path("", TemplateView.as_view(template_name="index.html"), name="frontend"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

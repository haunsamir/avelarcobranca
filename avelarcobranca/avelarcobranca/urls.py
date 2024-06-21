from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('colaboradores/', include('colaboradores.urls')),  # Include the colaboradores app URLs
    path('', RedirectView.as_view(url='/colaboradores/login/')),  # Redirect root to the login page
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
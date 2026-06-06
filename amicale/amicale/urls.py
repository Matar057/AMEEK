from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

admin.site.site_header = 'Administration'
admin.site.site_title = 'Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard:index'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('mentorship/', include('mentorship.urls')),
    path('payments/', include('payments.urls')),
    path('events/', include('events.urls')),
    path('documents/', include('documents.urls')),
    path('forum/', include('forum.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('communication/', include('communication.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.views.static import serve

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
    path('opportunites/', include('opportunites.urls')),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

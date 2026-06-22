import os

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication
    path('accounts/', include('accounts.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    # Main Site
    path('', include('bandhuapp.urls')),
    path('anandakendra/', include('applications.anandakendra.urls')),
    path('ankurayan/', include('applications.ankurayan.urls')),
    path('bandhughar/', include('applications.ashram.urls')),
    path('other_activities/', include('applications.charitywork.urls')),
    path('prasanta-raktadan-shibir/', include('applications.prasantaraktadan.urls')),
    path('patriotism-in-action/', include('applications.patriotism.urls')),
    path('odisha-satabdi-sevavrata/', include('applications.sevavrata.urls')),
    path('sanskarbarga/', include('applications.sanskarbarga.urls')),
    path('madh_mukti/', include('applications.madhmukti.urls')),
    path('publications/', include('applications.publications.urls')),
    path('swabalamban/', include('applications.swabalamban.urls')),
]

# Serve static and media files so CSS, JS, and images load (local development)
img_root = os.path.join(settings.BASE_DIR, 'img')
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL + 'img/', document_root=img_root)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
else:
    # When DEBUG=False (e.g. production-style run), still serve static/media for local testing
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL + 'img/', document_root=img_root)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
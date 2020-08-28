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
    path('sanskarbarga/', include('applications.sanskarbarga.urls')),
    path('madh_mukti/', include('applications.madhmukti.urls')),
    path('publications/', include('applications.publications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

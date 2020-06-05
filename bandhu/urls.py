from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication
    path('accounts/', include('accounts.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    # Main Site
    path('', include('bandhuapp.urls')),
    path('anandakendra/', include('applications.anandakendra.urls')),
    path('ankurayan/', include('applications.ankurayan.urls')),
    path('ashram/', include('applications.ashram.urls')),
    path('charitywork/', include('applications.charitywork.urls')),
    path('sanskarbarga/', include('applications.sanskarbarga.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
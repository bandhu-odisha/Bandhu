from django.urls import path

from . import views

app_name = 'publications'
urlpatterns = [
    path('', views.index, name='index'),
    path('<slug>/', views.PublicationDetail.as_view(), name='publication'),
    #url(r'^(?P<slug>[-\w]+)/download$', views.download_pdf, name='download_pdf'),
    
]
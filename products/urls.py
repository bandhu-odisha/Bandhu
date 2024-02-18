from django.urls import path
from django.conf import settings
from .views import ProductViewSet
urlpatterns = [
    path('', ProductViewSet.as_view())
]

from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import HomePage

from products.models import Product
# Create your views here.


class ProductViewSet(TemplateView):
    template_name = 'products.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        query_set = Product.objects.all()
        return render(request, 'products.html', {
            "data": query_set,
            "content": HomePage.objects.all().first()
        })

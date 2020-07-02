from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Publication

def index(request):
    publication_list = Publication.objects.filter(is_visible=True).order_by('-created')

    return render(request, "publications.html", { 'publications': publication_list })

def publication_detail(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_visible=True)

    return render(request, "publication_detail.html", { 'publication': publication })

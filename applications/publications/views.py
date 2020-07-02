from django.shortcuts import render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site

from .models import Publication

def index(request):
    publication_list = Publication.objects.filter(is_visible=True).order_by('-created')

    return render(request, "publications.html", { 'publications': publication_list })

def publication_detail(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_visible=True)
    current_site = get_current_site(request)

    context = {
        'publication': publication,
        'domain': current_site.domain,
    }

    return render(request, "publication_detail.html", context)

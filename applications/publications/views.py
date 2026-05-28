import os

from django.contrib.sites.shortcuts import get_current_site
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from .models import Publication, HomePage

def index(request):
    context = {
        'publications': Publication.objects.filter(is_visible=True).order_by('-created'),
        'content': HomePage.objects.all().first(),
    }

    return render(request, "publications.html", context)

def publication_detail(request, slug):
    publication = get_object_or_404(Publication, slug=slug, is_visible=True)
    current_site = get_current_site(request)

    context = {
        'publication': publication,
        'domain': current_site.domain,
        'content': HomePage.objects.all().first(),
    }

    return render(request, "publication_detail.html", context)


def download_publication(request, slug):
    """Serve publication file as an attachment so browsers save it instead of only previewing."""
    publication = get_object_or_404(Publication, slug=slug, is_visible=True)
    if not publication.media:
        raise Http404
    try:
        file_handle = publication.media.open('rb')
    except (FileNotFoundError, OSError):
        raise Http404
    filename = os.path.basename(publication.media.name)
    return FileResponse(file_handle, as_attachment=True, filename=filename)

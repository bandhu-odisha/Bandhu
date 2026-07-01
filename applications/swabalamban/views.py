from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from bandhuapp.pillar_pages import build_swabalamban_context
from bandhuapp.templatetags.permissions import is_admin

from .models import Product


def index(request):
    products = Product.objects.filter(is_published=True).order_by('sort_order', 'name')
    ctx = build_swabalamban_context(check_admin=is_admin(request.user))
    ctx['products'] = products
    return render(request, 'pillar_page.html', ctx)


@login_required
def create_product(request):
    if not is_admin(request.user):
        return redirect('pillar_swabalamban')
    if request.method != 'POST':
        return redirect('pillar_swabalamban')

    name = (request.POST.get('name') or '').strip()
    label = (request.POST.get('label') or name).strip()
    intro_lead = (request.POST.get('intro_lead') or '').strip()
    intro_text = (request.POST.get('intro_text') or '').strip()
    nutritional_highlights = (request.POST.get('nutritional_highlights') or '').strip()
    quality_promise = (request.POST.get('quality_promise') or '').strip()
    image = request.FILES.get('image')

    if not name or not label or not intro_text or not image:
        messages.error(request, 'Product name, label, description, and image are required.')
        return HttpResponseRedirect(reverse('pillar_swabalamban') + '#our-products')

    if Product.objects.filter(name__iexact=name).exists():
        messages.warning(request, f'A product named "{name}" already exists.')
        return HttpResponseRedirect(reverse('pillar_swabalamban') + '#our-products')

    next_sort = (
        Product.objects.order_by('-sort_order').values_list('sort_order', flat=True).first() or 0
    ) + 1
    Product.objects.create(
        name=name,
        label=label,
        image=image,
        intro_lead=intro_lead,
        intro_text=intro_text,
        nutritional_highlights=nutritional_highlights,
        quality_promise=quality_promise,
        sort_order=next_sort,
        is_published=True,
    )
    messages.success(request, f'Product "{name}" added.')
    return HttpResponseRedirect(reverse('pillar_swabalamban') + '#our-products')

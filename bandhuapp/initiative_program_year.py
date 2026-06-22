"""Shared year/detail page logic for initiative program apps (Bandhughar clones)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from bandhuapp.templatetags.permissions import is_admin


PROGRAMS = {
    'prasantaraktadan': {
        'name': 'Prasanta Raktadan Shibir',
        'default_desc': 'Voluntary blood donation camps across Odisha.',
        'quote_en': '"Every drop donated is a gift of life."',
        'quote_or': '"ପ୍ରତ୍ୟେକ ରକ୍ତଦାନ ଜୀବନର ଉପହାର।"',
        'list_url': 'prasantaraktadan:prasantaraktadan',
        'detail_url': 'prasantaraktadan:AshramDetail',
        'approval_url': 'prasantaraktadan:ImageAdminApprovalPrasantaraktadan',
        'approval_field': 'prasantaraktadan',
        'gallery_url': 'prasantaraktadan:AddToGallery',
        'create_activity_url': 'prasantaraktadan:CreateActivity',
        'add_activity_category_url': 'prasantaraktadan:AddActivityCategory',
        'create_event_url': 'prasantaraktadan:CreateEventPrasantaraktadan',
        'create_ashram_url': 'prasantaraktadan:CreateAshram',
        'home_gallery_url': 'prasantaraktadan:AddHomeGallery',
    },
    'patriotism': {
        'name': 'Patriotism in Action',
        'default_desc': 'Quizzes, camps, and programs that nurture love for the nation.',
        'quote_en': '"Patriotism grows through action and learning."',
        'quote_or': '"କାର୍ଯ୍ୟ ଓ ଶିକ୍ଷା ମାଧ୍ୟମରେ ଦେଶପ୍ରେମ ବୃଦ୍ଧି ପାଏ।"',
        'list_url': 'patriotism:patriotism',
        'detail_url': 'patriotism:AshramDetail',
        'approval_url': 'patriotism:ImageAdminApprovalPatriotism',
        'approval_field': 'patriotism',
        'gallery_url': 'patriotism:AddToGallery',
        'create_activity_url': 'patriotism:CreateActivity',
        'add_activity_category_url': 'patriotism:AddActivityCategory',
        'create_event_url': 'patriotism:CreateEventPatriotism',
        'create_ashram_url': 'patriotism:CreateAshram',
        'home_gallery_url': 'patriotism:AddHomeGallery',
    },
    'sevavrata': {
        'name': 'Odisha Satabdi Sevavrata',
        'default_desc': 'A service pledge for Odisha\'s centenary.',
        'quote_en': '"Service is the finest tribute to our land."',
        'quote_or': '"ସେବା ହିଁ ଆମ ମାଟିକୁ ଶ୍ରେଷ୍ଠ ଶ୍ରଦ୍ଧାଞ୍ଜଳି।"',
        'list_url': 'sevavrata:sevavrata',
        'detail_url': 'sevavrata:AshramDetail',
        'approval_url': 'sevavrata:ImageAdminApprovalSevavrata',
        'approval_field': 'sevavrata',
        'gallery_url': 'sevavrata:AddToGallery',
        'create_activity_url': 'sevavrata:CreateActivity',
        'add_activity_category_url': 'sevavrata:AddActivityCategory',
        'create_event_url': 'sevavrata:CreateEventSevavrata',
        'create_ashram_url': 'sevavrata:CreateAshram',
        'home_gallery_url': 'sevavrata:AddHomeGallery',
    },
}


def _detail_url(program_key, slug, fragment=''):
    url = reverse(PROGRAMS[program_key]['detail_url'], kwargs={'slug': slug})
    return url + fragment


def entry_has_public_content(ashram, models):
    """True when a year entry has content worth showing to public visitors."""
    if (ashram.reports or '').strip():
        return True
    if ashram.report_files.exists() or ashram.report_links.exists():
        return True
    if models.AshramInvitationLetter.objects.filter(ashram=ashram).exists():
        return True
    if models.Activity.objects.filter(ashram=ashram).exists():
        return True
    if models.Event.objects.filter(ashram=ashram).exists():
        return True
    if models.Photo.objects.filter(ashram=ashram, activity__isnull=True, approved=True).exists():
        return True
    return False


def maybe_publish_entry(ashram, models):
    if ashram.is_published or not entry_has_public_content(ashram, models):
        return
    ashram.is_published = True
    ashram.save(update_fields=['is_published'])


def reconcile_publish_states(models):
    """Keep is_published aligned with whether an entry actually has public content."""
    for ashram in models.Ashram.objects.all():
        should_publish = entry_has_public_content(ashram, models)
        if ashram.is_published != should_publish:
            ashram.is_published = should_publish
            ashram.save(update_fields=['is_published'])


def build_initiative_nav_visibility(request):
    """Nav/API flags: show new initiative links only when a program has published entries."""
    from applications import patriotism, prasantaraktadan, sevavrata

    admin = is_admin(request.user)
    programs = (
        ('show_initiative_patriotism', patriotism.models),
        ('show_initiative_raktadan', prasantaraktadan.models),
        ('show_initiative_sevavrata', sevavrata.models),
    )
    ctx = {}
    for key, models in programs:
        reconcile_publish_states(models)
        has_public = models.Ashram.objects.filter(is_published=True).exists()
        ctx[key] = has_public or admin
    return ctx


def get_visible_entries(request, models):
    qs = models.Ashram.objects.all().order_by('name')
    if not is_admin(request.user):
        qs = qs.filter(is_published=True)
    return qs


def _program_presentation_context(program_key):
    meta = PROGRAMS[program_key]
    return {
        'program_key': program_key,
        'program_name': meta['name'],
        'program_list_url': meta['list_url'],
        'program_detail_url': meta['detail_url'],
        'program_create_entry_url': meta['create_ashram_url'],
        'program_default_desc': meta.get('default_desc', ''),
        'program_quote_en': meta.get('quote_en', ''),
        'program_quote_or': meta.get('quote_or', ''),
        'hero_title': meta['name'],
        'carousel_glide_class': f'{program_key}_programs',
    }


def build_index_context(request, program_key, models):
    reconcile_publish_states(models)
    return {
        **_program_presentation_context(program_key),
        'ashrams': get_visible_entries(request, models),
        'content': models.HomePage.objects.all().first(),
        'check_admin': is_admin(request.user),
    }


def build_year_detail_context(request, slug, program_key, models):
    """Build template context for initiative program year/detail pages."""
    meta = PROGRAMS[program_key]
    Ashram = models.Ashram
    Activity = models.Activity
    Event = models.Event
    Photo = models.Photo
    InvitationLetter = models.AshramInvitationLetter

    ashram = get_object_or_404(Ashram, slug=slug)
    check_admin = is_admin(request.user)

    photos_qs = Photo.objects.filter(ashram=ashram, activity__isnull=True)
    unapproved_photos = photos_qs.filter(approved=False)
    photos = photos_qs.filter(approved=True).order_by('-id')
    activity_photo_qs = Photo.objects.order_by('id')
    if not check_admin:
        activity_photo_qs = activity_photo_qs.filter(approved=True)
    year_activities = Activity.objects.filter(ashram=ashram).select_related('category').prefetch_related(
        Prefetch('photo_set', queryset=activity_photo_qs),
    )
    categories = models.ActivityCategory.objects.filter(
        activities__ashram=ashram,
    ).distinct().prefetch_related(
        Prefetch('activities', queryset=year_activities.order_by('id')),
    )
    activities = year_activities
    has_activities = activities.exists()
    all_activity_categories = models.ActivityCategory.objects.all().order_by('name')
    events = Event.objects.filter(ashram=ashram).order_by('-date')
    other_entries_qs = Ashram.objects.exclude(pk=ashram.pk)
    if not check_admin:
        other_entries_qs = other_entries_qs.filter(is_published=True)
    other_entries = other_entries_qs.order_by('name')
    show_gallery = photos.exists() or unapproved_photos.exists()
    invitation_letter = InvitationLetter.objects.filter(ashram=ashram).first()

    return {
        **_program_presentation_context(program_key),
        'hero_title': f'{ashram.name} - {ashram.locality}',
        'program_gallery_url': meta['gallery_url'],
        'program_create_activity_url': meta['create_activity_url'],
        'program_add_activity_category_url': meta['add_activity_category_url'],
        'program_create_event_url': meta['create_event_url'],
        'program_approval_url': meta['approval_url'],
        'program_approval_field': meta['approval_field'],
        'ashram': ashram,
        'other_entries': other_entries,
        'categories': categories,
        'all_activity_categories': all_activity_categories,
        'activities': activities,
        'has_activities': has_activities,
        'events': events,
        'has_events': events.exists(),
        'photos': photos,
        'unapproved_photos': unapproved_photos,
        'check_admin': check_admin,
        'show_gallery': show_gallery,
        'gallery_is_home': False,
        'gallery_section_id': 'gallery',
        'report_files': ashram.report_files.all(),
        'report_links': ashram.report_links.all(),
        'invitation_letter': invitation_letter,
        'content': models.HomePage.objects.all().first(),
    }


def render_year_detail(request, slug, program_key, models):
    reconcile_publish_states(models)
    ashram = get_object_or_404(models.Ashram, slug=slug)
    if not ashram.is_published and not is_admin(request.user):
        raise Http404()
    context = build_year_detail_context(request, slug, program_key, models)
    context['entry_is_draft'] = not ashram.is_published
    return render(request, 'initiative_program/year_detail.html', context)


def _admin_required(view):
    return login_required(user_passes_test(is_admin, redirect_field_name=None, login_url='/accounts/login/')(view))


def make_upload_report_file(program_key, models):
    @_admin_required
    def upload_report_file(request, slug):
        ashram = get_object_or_404(models.Ashram, slug=slug)
        if request.method != 'POST':
            return redirect(PROGRAMS[program_key]['detail_url'], slug=slug)
        uploaded = request.FILES.get('report_file')
        title = (request.POST.get('title') or '').strip()
        if uploaded:
            models.AshramReportFile.objects.create(
                ashram=ashram,
                file=uploaded,
                title=title or uploaded.name or '',
            )
            messages.success(request, 'Report file uploaded.')
        else:
            messages.error(request, 'Please select a file.')
        maybe_publish_entry(ashram, models)
        return HttpResponseRedirect(_detail_url(program_key, slug, '#reports'))

    return upload_report_file


def make_add_report_link(program_key, models):
    @_admin_required
    def add_report_link(request, slug):
        ashram = get_object_or_404(models.Ashram, slug=slug)
        if request.method != 'POST':
            return redirect(PROGRAMS[program_key]['detail_url'], slug=slug)
        title = (request.POST.get('title') or '').strip()
        url = (request.POST.get('url') or '').strip()
        if title and url:
            models.AshramReportLink.objects.create(ashram=ashram, title=title, url=url)
            messages.success(request, 'Report link added.')
        else:
            messages.error(request, 'Title and URL are required.')
        maybe_publish_entry(ashram, models)
        return HttpResponseRedirect(_detail_url(program_key, slug, '#reports'))

    return add_report_link


def make_delete_report_file(program_key, models):
    @_admin_required
    def delete_report_file(request, pk):
        report_file = get_object_or_404(models.AshramReportFile, pk=pk)
        slug = report_file.ashram.slug
        if request.method == 'POST':
            report_file.file.delete(save=False)
            report_file.delete()
            messages.success(request, 'Report file removed.')
        return HttpResponseRedirect(_detail_url(program_key, slug, '#reports'))

    return delete_report_file


def make_delete_report_link(program_key, models):
    @_admin_required
    def delete_report_link(request, pk):
        report_link = get_object_or_404(models.AshramReportLink, pk=pk)
        slug = report_link.ashram.slug
        if request.method == 'POST':
            report_link.delete()
            messages.success(request, 'Report link removed.')
        return HttpResponseRedirect(_detail_url(program_key, slug, '#reports'))

    return delete_report_link


def make_upload_invitation(program_key, models):
    @_admin_required
    def upload_invitation(request, slug):
        ashram = get_object_or_404(models.Ashram, slug=slug)
        if request.method != 'POST':
            return redirect(PROGRAMS[program_key]['detail_url'], slug=slug)
        uploaded = request.FILES.get('invitation_file')
        if not uploaded:
            messages.error(request, 'Please select a file.')
        else:
            letter, _created = models.AshramInvitationLetter.objects.get_or_create(ashram=ashram)
            if letter.file:
                letter.file.delete(save=False)
            letter.file = uploaded
            letter.save()
            messages.success(request, 'Invitation letter uploaded.')
        maybe_publish_entry(ashram, models)
        return HttpResponseRedirect(_detail_url(program_key, slug, '#invitation'))

    return upload_invitation


def make_delete_invitation(program_key, models):
    @_admin_required
    def delete_invitation(request, slug):
        ashram = get_object_or_404(models.Ashram, slug=slug)
        if request.method == 'POST':
            letter = models.AshramInvitationLetter.objects.filter(ashram=ashram).first()
            if letter:
                letter.file.delete(save=False)
                letter.delete()
                messages.success(request, 'Invitation letter removed.')
        return HttpResponseRedirect(_detail_url(program_key, slug, '#invitation'))

    return delete_invitation


def make_update_description(program_key, models):
    @_admin_required
    def update_description(request, slug):
        ashram = get_object_or_404(models.Ashram, slug=slug)
        if request.method != 'POST':
            return redirect(PROGRAMS[program_key]['detail_url'], slug=slug)
        ashram.description = request.POST.get('description', '')
        ashram.save(update_fields=['description'])
        messages.success(request, 'Description updated.')
        maybe_publish_entry(ashram, models)
        return HttpResponseRedirect(_detail_url(program_key, slug, '#description'))

    return update_description


def build_index_gallery_context(request, program_key, models):
    """Gallery on main pages: all approved photos from every year entry."""
    meta = PROGRAMS[program_key]
    check_admin = is_admin(request.user)
    photos_qs = models.Photo.objects.filter(activity__isnull=True)
    if not check_admin:
        photos_qs = photos_qs.filter(ashram__is_published=True)
    photos = photos_qs.filter(approved=True).select_related('ashram').order_by('-id')
    show_gallery = photos.exists()
    return {
        'program_key': program_key,
        'program_name': meta['name'],
        'photos': photos,
        'unapproved_photos': photos_qs.none(),
        'check_admin': check_admin,
        'show_gallery': show_gallery,
        'gallery_is_home': True,
        'gallery_section_id': 'gallery',
    }


def make_add_to_gallery(program_key, models):
    @login_required
    def add_to_gallery(request):
        if request.method != 'POST':
            return HttpResponseRedirect('/')
        slug = (request.POST.get('slug') or '').strip()
        if not slug:
            return redirect(PROGRAMS[program_key]['list_url'])
        ashram = get_object_or_404(models.Ashram, slug=slug)
        images = request.FILES.getlist('gallery_images')
        if not images:
            messages.error(request, 'Please select at least one image.')
        else:
            seen = set()
            created = 0
            for image in images:
                key = (image.name, image.size)
                if key in seen:
                    continue
                seen.add(key)
                models.Photo.objects.create(
                    ashram=ashram,
                    picture=image,
                    approved=is_admin(request.user),
                )
                created += 1
            if created:
                messages.success(request, 'Gallery images uploaded.')
                maybe_publish_entry(ashram, models)
            else:
                messages.error(request, 'No images were uploaded.')
        return HttpResponseRedirect(_detail_url(program_key, slug, '#gallery'))

    return add_to_gallery


def make_add_activity_category(program_key, models):
    @login_required
    def add_activity_category(request):
        if request.method != 'POST':
            return HttpResponseRedirect('/')
        slug = (request.POST.get('slug') or '').strip()
        name = (request.POST.get('name') or '').strip()
        if not name:
            messages.error(request, 'Category name is required.')
        else:
            _, created = models.ActivityCategory.objects.get_or_create(name=name)
            if created:
                messages.success(request, f'Category "{name}" added.')
            else:
                messages.info(request, f'Category "{name}" already exists.')
        if slug:
            return HttpResponseRedirect(_detail_url(program_key, slug, '#activities'))
        return redirect(PROGRAMS[program_key]['list_url'])

    return add_activity_category


def make_create_activity(program_key, models):
    @login_required
    def create_activity(request):
        if request.method != 'POST':
            return HttpResponseRedirect('/')
        slug = (request.POST.get('slug') or '').strip()
        name = (request.POST.get('activity_name') or '').strip()
        category_id = (request.POST.get('category') or '').strip()
        category_name = (request.POST.get('category_name') or '').strip() or 'General'
        description = request.POST.get('description') or ''
        activity_images = request.FILES.getlist('activity_images')

        if not slug or not name:
            messages.error(request, 'Activity name is required.')
            return HttpResponseRedirect(_detail_url(program_key, slug, '#activities') if slug else PROGRAMS[program_key]['list_url'])

        if not activity_images:
            messages.error(request, 'An activity image is required.')
            return HttpResponseRedirect(_detail_url(program_key, slug, '#description') if slug else PROGRAMS[program_key]['list_url'])

        ashram = get_object_or_404(models.Ashram, slug=slug)
        if category_id:
            activity_category = get_object_or_404(models.ActivityCategory, pk=category_id)
        else:
            activity_category, _created = models.ActivityCategory.objects.get_or_create(name=category_name)
        activity = models.Activity.objects.create(
            ashram=ashram,
            category=activity_category,
            name=name,
            description=description,
        )
        for image in activity_images:
            models.Photo.objects.create(
                ashram=ashram,
                picture=image,
                activity=activity,
                approved=is_admin(request.user),
            )
        messages.success(request, 'Activity added.')
        maybe_publish_entry(ashram, models)
        return HttpResponseRedirect(_detail_url(program_key, slug, '#activities'))

    return create_activity


def make_create_event(program_key, models):
    @login_required
    def create_event(request):
        if request.method != 'POST':
            return HttpResponseRedirect('/')
        slug = (request.POST.get('slug') or '').strip()
        name = (request.POST.get('event_name') or '').strip()
        date = request.POST.get('event_date')
        description = request.POST.get('description') or ''
        thumb = request.FILES.get('event_thumb')

        if not slug or not name or not date or not thumb:
            messages.error(request, 'Event name, date, and thumbnail are required.')
            return HttpResponseRedirect(_detail_url(program_key, slug, '#activities') if slug else PROGRAMS[program_key]['list_url'])

        ashram = get_object_or_404(models.Ashram, slug=slug)
        models.Event.objects.create(
            name=name,
            ashram=ashram,
            date=date,
            description=description,
            thumb=thumb,
        )
        messages.success(request, 'Event added.')
        maybe_publish_entry(ashram, models)
        return HttpResponseRedirect(_detail_url(program_key, slug, '#events'))

    return create_event

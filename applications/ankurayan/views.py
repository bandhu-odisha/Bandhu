from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse
from datetime import datetime
from django.core import serializers
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.template.defaultfilters import slugify
from bandhuapp.models import Profile
from bandhuapp.templatetags.permissions import is_admin
from accounts.forms import RegisterForm
from .models import (
    Ankurayan, Activity, Photo, Guest, Participant,
    ActivityCategory, HomePage, AnkurayanReportFile, AnkurayanPublicationFile,
    AnkurayanInvitationLetter,
)

# Create your views here.

def index(request):
    context = {
        'ankurayans': Ankurayan.objects.all().order_by('-year'),
        'content': HomePage.objects.all().first(),
    }
    return render(request, 'ankurayan.html', context)

@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/ankurayan/")
def create_ankurayan(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        title = request.POST.get('title')
        theme = request.POST.get('theme')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        logo = request.FILES.get('logo')
        description = request.POST.get('description')

        # admin = request.POST.get('admin')
        # admin_profile = get_object_or_404(Profile,pk=int(admin))

        if Ankurayan.objects.filter(year=year).exists():
            messages.error(request, "Ankurayan with entered year already exists.")
            return redirect('ankurayan:ankurayan')

        slug = slugify(year)
        Ankurayan.objects.create(year=year, title=title, theme=theme, slug=slug,
                                 start_date=start_date, end_date=end_date,
                                 logo=logo, description=description)
        return redirect('ankurayan:AnkurayanDetail', slug)

    return redirect('ankurayan:ankurayan')

def ankurayan_detail(request, slug):
    ankurayan = get_object_or_404(Ankurayan, slug=slug)

    categories = ActivityCategory.objects.filter(ankurayan=ankurayan, activities__isnull=False).distinct()
    participants = Participant.objects.filter(ankurayan=ankurayan)
    guests = Guest.objects.filter(ankurayan=ankurayan)
    check_admin = is_admin(request.user)

    # if ankurayan.admin is not None and ankurayan.admin.user == request.user:
    #     # photos = Photo.objects.filter(ankurayan=ankurayan)
    #     check_admin = True
    # else:
    #     photos = Photo.objects.filter(ankurayan=ankurayan).filter(approved=True)

    photos = Photo.objects.filter(ankurayan=ankurayan)
    unapproved_photos = photos.filter(approved=False)
    photos = photos.filter(approved=True)

    ankurayans = Ankurayan.objects.all().exclude(slug=slug).order_by('-year')
    activity_img = []
    for i in categories:
        for j in i.activities.all():
            activity_img.append(Photo.objects.filter(activity=j))

    signup_initial = {}
    prefill_email = request.session.pop('signup_modal_prefill_email', None)
    if prefill_email:
        signup_initial['email'] = prefill_email

    context = {
        'ankurayan': ankurayan,
        'categories': categories,
        'participants': participants,
        'photos': photos,
        'unapproved_photos': unapproved_photos,
        'check_admin': check_admin,
        'ankurayans': ankurayans,
        'activity_img': activity_img,
        'content': HomePage.objects.all().first(),
        'report_files': ankurayan.report_files.all(),
        'publication_files': ankurayan.publication_files.all(),
        'guests': guests,
        'signup_form': RegisterForm(initial=signup_initial),
        'open_signup_modal': request.GET.get('signup_modal') == '1',
        'invitation_letter': AnkurayanInvitationLetter.objects.filter(ankurayan=ankurayan).first(),
    }
    return render(request,'ankurayan_detail.html', context)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def update_ankurayan_section(request, slug):
    """Update description, reports, publications, or visitors (admin only)."""
    ankurayan = get_object_or_404(Ankurayan, slug=slug)
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=slug)
    field = request.POST.get('field')
    content = request.POST.get('content', '')
    if field in ('description', 'reports', 'publications', 'visitors'):
        setattr(ankurayan, field, content)
        ankurayan.save()
        messages.success(request, f'{field.capitalize()} updated.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug})
    fragment = {'description': 'modalDescription', 'reports': 'modalReports',
                'publications': 'modalPublications', 'visitors': 'modalVisitors'}.get(field, '')
    if fragment:
        url += f'#{fragment}'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def upload_ankurayan_report(request, slug):
    """Upload a report file (any type) for this Ankurayan (admin only)."""
    ankurayan = get_object_or_404(Ankurayan, slug=slug)
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=slug)
    f = request.FILES.get('report_file')
    title = (request.POST.get('title') or '').strip()
    if f:
        # Use title or filename; never pass None (DB column may be NOT NULL)
        AnkurayanReportFile.objects.create(ankurayan=ankurayan, file=f, title=title or f.name or '')
        messages.success(request, 'File uploaded.')
    else:
        messages.error(request, 'Please select a file.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalReports'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def upload_ankurayan_publication(request, slug):
    """Upload a publication file (any type) for this Ankurayan (admin only)."""
    ankurayan = get_object_or_404(Ankurayan, slug=slug)
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=slug)
    f = request.FILES.get('publication_file')
    title = (request.POST.get('title') or '').strip()
    if f:
        # Use title or filename; never pass None (DB column may be NOT NULL)
        AnkurayanPublicationFile.objects.create(ankurayan=ankurayan, file=f, title=title or f.name or '')
        messages.success(request, 'File uploaded.')
    else:
        messages.error(request, 'Please select a file.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalPublications'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def upload_ankurayan_invitation(request, slug):
    """Upload or replace the one-page invitation letter for this Ankurayan (admin only)."""
    ankurayan = get_object_or_404(Ankurayan, slug=slug)
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=slug)
    f = request.FILES.get('invitation_file')
    if not f:
        messages.error(request, 'Please select a file.')
    else:
        letter, _created = AnkurayanInvitationLetter.objects.get_or_create(ankurayan=ankurayan)
        if letter.file:
            letter.file.delete(save=False)
        letter.file = f
        letter.save()
        messages.success(request, 'Invitation letter uploaded.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalInvitationLetter'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def delete_ankurayan_invitation(request, slug):
    """Remove the invitation letter for this Ankurayan (admin only). POST only."""
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=slug)
    ankurayan = get_object_or_404(Ankurayan, slug=slug)
    letter = AnkurayanInvitationLetter.objects.filter(ankurayan=ankurayan).first()
    if letter:
        letter.file.delete(save=False)
        letter.delete()
        messages.success(request, 'Invitation letter removed.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalInvitationLetter'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def delete_ankurayan_publication_file(request, pk):
    """Delete a publication file (admin only). POST only."""
    if request.method != 'POST':
        return redirect('ankurayan:ankurayan')
    pub_file = get_object_or_404(AnkurayanPublicationFile, pk=pk)
    slug = pub_file.ankurayan.slug
    pub_file.file.delete(save=False)
    pub_file.delete()
    messages.success(request, 'File removed.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalPublications'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def update_ankurayan_publication_file(request, pk):
    """Update a publication file title (admin only). POST only."""
    if request.method != 'POST':
        return redirect('ankurayan:ankurayan')
    pub_file = get_object_or_404(AnkurayanPublicationFile, pk=pk)
    slug = pub_file.ankurayan.slug
    title = (request.POST.get('title') or '').strip()
    pub_file.title = title
    pub_file.save(update_fields=['title'])
    messages.success(request, 'Publication title updated.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalPublications'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def delete_ankurayan_report_file(request, pk):
    """Delete a report file (admin only). POST only."""
    if request.method != 'POST':
        return redirect('ankurayan:ankurayan')
    report_file = get_object_or_404(AnkurayanReportFile, pk=pk)
    slug = report_file.ankurayan.slug
    report_file.file.delete(save=False)
    report_file.delete()
    messages.success(request, 'File removed.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalReports'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def update_ankurayan_report_file(request, pk):
    """Update a report file title (admin only). POST only."""
    if request.method != 'POST':
        return redirect('ankurayan:ankurayan')
    report_file = get_object_or_404(AnkurayanReportFile, pk=pk)
    slug = report_file.ankurayan.slug
    title = (request.POST.get('title') or '').strip()
    report_file.title = title
    report_file.save(update_fields=['title'])
    messages.success(request, 'Report title updated.')
    url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': slug}) + '#modalReports'
    return HttpResponseRedirect(url)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def add_participant(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        school_class = request.POST.get('school_class')
        contact_no = request.POST.get('contact_no')
        address = request.POST.get('address')

        ankurayan = get_object_or_404(Ankurayan,slug=slug)
        Participant.objects.create(ankurayan=ankurayan,name=name,
                                gender=gender,school_class=school_class,
                                contact_no=contact_no,address=address)
        
        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')
  
@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def add_guest(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        ankurayan = get_object_or_404(Ankurayan,slug=slug)

        name = request.POST.get('name')
        about = request.POST.get('about')
        profession = request.POST.get('profession')
        contact_no = request.POST.get('contact_no') or ''
        email = request.POST.get('email') or ''
        facebook_url = request.POST.get('facebook_url') or ''
        linkedin_url = request.POST.get('linkedin_url') or ''
        avatar = request.POST.get('avatar') or 'man'
        if avatar not in ('man', 'woman'):
            avatar = 'man'
        photo = request.FILES.get('photo')

        Guest.objects.create(
            email=email,
            name=name,
            about=about,
            profession=profession,
            contact_no=contact_no,
            facebook_url=facebook_url,
            linkedin_url=linkedin_url,
            avatar=avatar,
            photo=photo,
            ankurayan=ankurayan,
        )

        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def update_guest(request, pk):
    """Update a guest's details (admin only). POST only. Returns JSON for AJAX or redirects."""
    guest = get_object_or_404(Guest, pk=pk)
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=guest.ankurayan.slug)
    name = (request.POST.get('name') or '').strip()
    profession = (request.POST.get('profession') or '').strip()
    about = (request.POST.get('about') or '').strip()
    quote = (request.POST.get('quote') or '').strip()
    facebook_url = (request.POST.get('facebook_url') or '').strip()
    linkedin_url = (request.POST.get('linkedin_url') or '').strip()
    # Required fields
    if not name:
        err = 'Name is required.'
    elif not profession:
        err = 'Profession is required.'
    elif not about:
        err = 'About is required.'
    else:
        err = None
    if err:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': err}, status=400)
        from django.contrib import messages
        messages.error(request, err)
        return redirect('ankurayan:AnkurayanDetail', slug=guest.ankurayan.slug)
    guest.name = name
    guest.profession = profession
    guest.about = about or ''
    guest.quote = quote or ''
    guest.facebook_url = facebook_url or ''
    guest.linkedin_url = linkedin_url or ''
    avatar = (request.POST.get('avatar') or guest.avatar or 'man').strip()
    if avatar in ('man', 'woman'):
        guest.avatar = avatar
    if request.FILES.get('photo'):
        guest.photo = request.FILES['photo']
    guest.save()
    photo_url = guest.photo.url if guest.photo else ''
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'guest': {
                'name': guest.name,
                'profession': guest.profession,
                'about': guest.about or '',
                'quote': guest.quote or '',
                'facebook_url': guest.facebook_url or '',
                'linkedin_url': guest.linkedin_url or '',
                'avatar': guest.avatar,
                'photo_url': photo_url,
            }
        })
    return redirect('ankurayan:AnkurayanDetail', slug=guest.ankurayan.slug)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def delete_guest(request, pk):
    """Remove a guest (admin only). POST only. JSON for AJAX."""
    guest = get_object_or_404(Guest, pk=pk)
    slug = guest.ankurayan.slug
    if request.method != 'POST':
        return redirect('ankurayan:AnkurayanDetail', slug=slug)
    guest.delete()
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, 'Guest removed.')
    return redirect('ankurayan:AnkurayanDetail', slug=slug)


@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def add_activity_category(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('name')

        ankurayan = get_object_or_404(Ankurayan, slug=slug)

        ActivityCategory.objects.create(ankurayan=ankurayan, name=name)

        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def create_activity(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('activity_name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date = request.POST.get('date')
        activity_images = request.FILES.getlist('activity_images')

        ankurayan = get_object_or_404(Ankurayan,slug=slug)
        activity_category = get_object_or_404(ActivityCategory,pk=int(category))

        print(ankurayan,activity_category,category)
        activity = Activity.objects.create(category=activity_category,
                                name=name,description=description,date=date)

        for i in activity_images:
            Photo.objects.create(ankurayan=ankurayan,picture=i,activity=activity,approved=True)

        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def add_winners(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        activity_pk = request.POST.get('pk')
        name = request.POST.get('activity_name')
        winner = request.POST.get('pk_winner')
        runner_up1 = request.POST.get('pk_runner_up1')
        runner_up2 = request.POST.get('pk_runner_up2')
        activity_images = request.FILES.getlist('activity_images')

        winner_profile = get_object_or_404(Participant,pk=int(winner))
        print(1, winner_profile)
        runner_up1_profile = get_object_or_404(Participant,pk=int(runner_up1))
        print(2, runner_up1_profile)
        runner_up2_profile = get_object_or_404(Participant,pk=int(runner_up2))
        print(3, runner_up2_profile)
        print(activity_pk)
        ankurayan = get_object_or_404(Ankurayan,slug=slug)
        # category = get_object_or_404(ActivityCategory, ankurayan=ankurayan)  # Modify this
        activity = get_object_or_404(Activity, pk=int(activity_pk))
        activity.winner = winner_profile
        activity.runner_up1 = runner_up1_profile
        activity.runner_up2 = runner_up2_profile
        activity.save()

        for i in activity_images:
            Photo.objects.create(ankurayan=ankurayan,picture=i,activity=activity)
        
        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def add_to_gallery(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        activity_images = request.FILES.getlist('gallery_images')
        ankurayan = get_object_or_404(Ankurayan,slug=slug)
        print("image =",activity_images)

        for i in activity_images:
            Photo.objects.create(
                ankurayan=ankurayan,
                picture=i,
                approved=is_admin(request.user),
            )

        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
@user_passes_test(is_admin, redirect_field_name=None, login_url="/accounts/login/")
def admin_approval(request):
    if request.method == 'POST':
        slug = request.POST.get('ankurayan')
        image_pk = request.POST.get('image')
        status = request.POST.get('status')

        ankurayan = get_object_or_404(Ankurayan,slug=slug)
        photo = get_object_or_404(Photo,pk=int(image_pk))
        print(photo)
        if status == "approve":
            photo.approved = True
            photo.save()
        else:
            photo.picture.delete()
            photo.delete()

        # If form POST (e.g. delete button), redirect back to detail page; if AJAX (Approve modal), return JSON
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return redirect('ankurayan:AnkurayanDetail', slug=slug)
        photos = Photo.objects.filter(ankurayan=ankurayan)
        data = serializers.serialize('json', photos)
        return JsonResponse(data, safe=False)
    return HttpResponseRedirect('/')
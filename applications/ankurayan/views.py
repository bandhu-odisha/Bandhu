from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,JsonResponse
from datetime import datetime
from django.core import serializers
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.template.defaultfilters import slugify
from bandhuapp.models import Profile
from bandhuapp.templatetags.permissions import is_admin
from .models import (
    Ankurayan, Activity, Photo, Guest, Participant,
    ActivityCategory, HomePage,
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
    }
    return render(request,'ankurayan_detail.html', context)

@login_required
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
def add_guest(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        ankurayan = get_object_or_404(Ankurayan,slug=slug)

        name = request.POST.get('name')
        about = request.POST.get('about')
        profession = request.POST.get('profession')
        contact_no = request.POST.get('contact_no')
        email = request.POST.get('email')

        Guest.objects.create(email=email,name=name,about=about,
                                    profession=profession,contact_no=contact_no,
                                    ankurayan=ankurayan)

        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
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
def add_to_gallery(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        activity_images = request.FILES.getlist('gallery_images')
        ankurayan = get_object_or_404(Ankurayan,slug=slug)
        print("image =",activity_images)

        for i in activity_images:
            if ankurayan.admin is not None and ankurayan.admin.user == request.user:
                Photo.objects.create(ankurayan=ankurayan,picture=i,approved=True)
            else:
                Photo.objects.create(ankurayan=ankurayan,picture=i)

        url = '/ankurayan/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
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
        
        print(photo.approved)
        photos = Photo.objects.filter(ankurayan=ankurayan)

        data = serializers.serialize('json', photos)
        return JsonResponse(data,safe=False)
    return HttpResponseRedirect('/')
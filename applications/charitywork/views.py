from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from datetime import datetime
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from bandhuapp.models import Profile
from accounts.models import User
from bandhuapp.templatetags.permissions import is_admin
from .models import (
    Charity, Volunteer, Activity, Photo, HomePage,
)

# Create your views here.

def index(request):
    context = {
        'charity_works': Charity.objects.all(),
        'content': HomePage.objects.all().first(),
    }
    return render(request, 'charity.html', context)

@login_required
def create_charity(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        purpose = request.POST.get('purpose')
        location = request.POST.get('location')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # admin = request.POST.get('admin')
        # admin_profile = get_object_or_404(Profile,pk=int(admin))

        if Charity.objects.filter(title=title, purpose=purpose, location=location).exists():
            messages.error(request, "Activity with entered title, purpose and location already exists.")
            return redirect('charitywork:charity_work')

        slug = slugify(f'{title} {purpose} {location}')
        Charity.objects.create(title=title, purpose=purpose, location=location,
                               slug=slug, start_date=start_date, end_date=end_date,
                               description=description, image=image)
        return redirect('charitywork:CharityDetail', slug)

    return redirect('charitywork:charity_work')

def charity_detail(request,slug):
    charity = get_object_or_404(Charity,slug=slug)
    activities = Activity.objects.filter(charity=charity)
    check_admin = is_admin(request.user)

    # if charity.admin is not None and charity.admin.user == request.user:
    #     photos = Photo.objects.filter(charity=charity)
    #     check_admin = True
    # else:
    #     photos = Photo.objects.filter(charity=charity).filter(approved=True)

    photos = Photo.objects.filter(charity=charity)
    unapproved_photos = photos.filter(approved=False)
    photos = photos.filter(approved=True)

    context = {
        'charity': charity,
        'activities': activities,
        'photos':photos,
        'unapproved_photos': unapproved_photos,
        'check_admin':check_admin,
        'content': HomePage.objects.all().first(),
    }

    return render(request,'charity_detail.html', context)

@login_required
def add_volunteers(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        print(slug)

        name = request.POST.get('name')
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')

        volunteer = request.POST.get('volunteers')
        volunteers = volunteer.split(",")
        print(volunteers)

        charity = get_object_or_404(Charity,slug=slug)

        if name:
            Volunteer.objects.create(charity=charity,name=name,
                                contact_no=contact_no,email=email)
        else:
            for i in volunteers:
                profile = Profile.objects.filter(user__email=i).first()
                Volunteer.objects.create(charity=charity,profile=profile)
        
        url = '/other_activities/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def create_activity(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('activity_name')
        description = request.POST.get('description')
        date = request.POST.get('date')
        activity_images = request.FILES.getlist('activity_images')

        charity = get_object_or_404(Charity,slug=slug)

        activity = Activity.objects.create(charity=charity,name=name,description=description,
                                            date=date)

        for i in activity_images:
            Photo.objects.create(charity=charity,picture=i,activity=activity,approved=True)

        url = '/other_activities/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def add_to_gallery(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        activity_images = request.FILES.getlist('gallery_images')
        charity = get_object_or_404(Charity,slug=slug)
        print("image =",activity_images)

        for i in activity_images:
            if charity.admin is not None and charity.admin.user == request.user:
                Photo.objects.create(charity=charity,picture=i,approved=True)
            else:
                Photo.objects.create(charity=charity,picture=i)

        url = '/other_activities/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def admin_approval(request):
    if request.method == 'POST':
        slug = request.POST.get('charity')
        image_pk = request.POST.get('image')
        status = request.POST.get('status')

        charity = get_object_or_404(Charity,slug=slug)
        photo = get_object_or_404(Photo,pk=int(image_pk))
        print(photo)
        if status == "approve":
            photo.approved = True
            photo.save()
        else:
            photo.delete()
        
        print(photo.approved)
        photos = Photo.objects.filter(charity=charity)

        data = serializers.serialize('json', photos)
        return JsonResponse(data,safe=False)
    return HttpResponseRedirect('/')
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,JsonResponse
from datetime import datetime
from django.core import serializers
from django.contrib.auth.decorators import login_required

from bandhuapp.models import Profile
from accounts.models import User
from .models import Charity,Activity,Photo,Volunteer

# Create your views here.

def index(request):
    charity = Charity.objects.all()
    photos = Photo.objects.all()
    return render(request, 'charity.html',{'charity':charity,'photos':photos})

@login_required
def create_charity(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        location = request.POST.get('location')
        description = request.POST.get('description')
        disaster_type = request.POST.get('disaster_type')
        admin = request.POST.get('admin')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        admin_profile = get_object_or_404(Profile,pk=int(admin))

        Charity.objects.create(title=title,location=location,
                                start_date=start_date,disaster_type=disaster_type,
                                description=description,end_date=end_date,
                                admin=admin_profile)
        
        return HttpResponseRedirect('/charity_work/')
        
def charity_detail(request,slug):
    charity = get_object_or_404(Charity,slug=slug)
    activities = Activity.objects.filter(charity=charity)
    check_admin = False

    if charity.admin is not None and charity.admin.user == request.user:
        photos = Photo.objects.filter(charity=charity)
        check_admin = True
    else:
        photos = Photo.objects.filter(charity=charity).filter(approved=True)

    return render(request,'charity_detail.html',{'charity':charity,'activities':activities,
                                                    'photos':photos,'check_admin':check_admin})

@login_required
def add_volunteers(request):
    if request.method == 'POST':
        activity_date = request.POST.get('activity_date')
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
        
        url = '/charity_work/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def create_activity(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('activity_name')
        description = request.POST.get('description')
        activity_date = request.POST.get('activity_date')
        activity_images = request.FILES.getlist('activity_images')

        charity = get_object_or_404(Charity,slug=slug)

        activity = Activity.objects.create(charity=charity,name=name,description=description,
                                            activity_date=activity_date)

        for i in activity_images:
            Photo.objects.create(charity=charity,picture=i,activity=activity,approved=True)

        url = '/charity_work/detail/' + slug +'/'
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

        url = '/charity_work/detail/' + slug +'/'
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
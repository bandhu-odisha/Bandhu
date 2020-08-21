from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required

from bandhuapp.models import Profile
from .models import AnandaKendra,Activity,Photo,Acharya,Student,ActivityCategory, Event

# Create your views here.

def index(request):
    kendras = AnandaKendra.objects.all()
    return render(request, 'anandakendra.html',{'kendras':kendras})

@login_required
def create_anandakendra(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        locality = request.POST.get('locality')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        # admin = request.POST.get('admin')
        description = request.POST.get('description')

        # admin_profile = get_object_or_404(Profile,pk=int(admin))
        AnandaKendra.objects.create(name=name,locality=locality,
                                address=address,image=image,
                                description=description)
        
        return HttpResponseRedirect('/anandakendra/')

def anandkendra_detail(request, slug):
    kendra = get_object_or_404(AnandaKendra, slug=slug)
    categories = ActivityCategory.objects.filter(kendra=kendra)
    events = Event.objects.filter(kendra=kendra)
    students = Student.objects.filter(kendra=kendra)
    check_admin = False

    if kendra.admin is not None and kendra.admin.user == request.user:
        # photos = Photo.objects.filter(kendra=kendra)
        check_admin = True
    # else:
    #     photos = Photo.objects.filter(kendra=kendra).filter(approved=True)

    photos = Photo.objects.filter(kendra=kendra)
    unapproved_photos = photos.filter(approved=False)
    photos = photos.filter(approved=True)

    activities_list = []

    # activities = Activity.objects.filter(category__kendra=kendra)
    # for activity in activities:
    #     photos = Photo.objects.filter(activity=activity).filter(approved=True)
    #     activities_list.append([activity,photos])

    context = {
        'kendra': kendra,
        'categories': categories,
        'activities': activities_list,
        'events': events,
        'students': students,
        'photos': photos,
        'check_admin': check_admin,
    }

    return render(request,'anandkendra_detail.html', context)

@login_required
def enroll_student(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        guardian_name = request.POST.get('guardian_name')
        school_class = request.POST.get('school_class')
        contact_no = request.POST.get('contact_no')
        address = request.POST.get('address')

        kendra = get_object_or_404(AnandaKendra,slug=slug)
        Student.objects.create(kendra=kendra,name=name,
                                gender=gender,guardian_name=guardian_name,
                                school_class=school_class,
                                contact_no=contact_no,address=address)
        
        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required       
def add_acharya(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        kendra = get_object_or_404(AnandaKendra,slug=slug)
        acharya = request.POST.get('acharyas')
        acharyas = acharya.split(",")

        for i in acharyas:
            profile = Profile.objects.filter(user__email=i).first()
            Acharya.objects.create(kendra=kendra,acharya_id=profile)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def add_activity_category(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('name')

        kendra = get_object_or_404(AnandaKendra, slug=slug)

        ActivityCategory.objects.create(kendra=kendra, name=name)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def create_activity(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('activity_name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        activity_time = request.POST.get('activity_time')
        activity_images = request.FILES.getlist('activity_images')

        kendra = get_object_or_404(AnandaKendra, slug=slug)
        activity_category = get_object_or_404(ActivityCategory, pk=int(category))

        print(kendra,activity_category,category)
        activity = Activity.objects.create(category=activity_category,
                                name=name,description=description,activity_time=activity_time)

        for i in activity_images:
            Photo.objects.create(kendra=kendra,picture=i,activity=activity,approved=True)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def add_to_gallery(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        activity_images = request.FILES.getlist('gallery_images')
        kendra = get_object_or_404(AnandaKendra,slug=slug)
        print("image =",activity_images)
        for i in activity_images:
            if kendra.admin is not None and kendra.admin.user == request.user:
                Photo.objects.create(kendra=kendra,picture=i,approved=True)
            else:
                Photo.objects.create(kendra=kendra,picture=i)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

@login_required
def admin_approval(request):
    if request.method == 'POST':
        slug = request.POST.get('kendra')
        image_pk = request.POST.get('image')
        status = request.POST.get('status')

        kendra = get_object_or_404(AnandaKendra,slug=slug)
        photo = get_object_or_404(Photo,pk=int(image_pk))
        if status == "approve":
            photo.approved = True
            photo.save()
        else:
            photo.delete()
        
        photos = Photo.objects.filter(kendra=kendra)

        data = serializers.serialize('json', photos)
        return JsonResponse(data,safe=False)
    return HttpResponseRedirect('/')

@login_required
def create_event(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        thumb = request.FILES.get('event_thumb')
        name = request.POST.get('event_name')
        date = request.POST.get('event_date')
        description = request.POST.get('description')
        
        kendra = get_object_or_404(AnandaKendra,slug=slug)
        Event.objects.create(name=name,kendra=kendra,date=date,
                            description=description,thumb=thumb)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')
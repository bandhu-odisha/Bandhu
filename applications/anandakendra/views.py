from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from bandhuapp.models import Profile
from .models import AnandaKendra,Activity,Photo,Acharya,Student,ActivityCategory

# Create your views here.

def index(request):
    kendras = AnandaKendra.objects.all()
    return render(request, 'index.html',{'kendras':kendras})

def create_anandakendra(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        locality = request.POST.get('locality')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        description = request.POST.get('description')

        Ankurayan.objects.create(name=name,locality=locality,
                                address=address,image=image,
                                description=description)
        
        return HttpResponseRedirect('/ankurayan/')

def anandkendra_detail(request,slug):
    kendra = get_object_or_404(AnandaKendra,slug=slug)
    activities = Activity.objects.filter(kendra=kendra)
    photos = Photo.objects.filter(kendra=kendra)
    categories = ActivityCategory.objects.all()
    students = Student.objects.all()
    return render(request,'anandkendra_detail.html',{'kendra':kendra,'activities':activities,
                                                    'photos':photos,'categories':categories,
                                                    'students':students})

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
        
def add_acharya(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        kendra = get_object_or_404(AnandaKendra,slug=slug)
        acharyas = request.POST.getlist('acharyas')

        for i in acharyas:
            profile = Profile.objects.filter(user__email=i).first()
            Acharya.objects.create(kendra=kendra,acharya_id=profile)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

def add_activity(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('name')
        category = request.POST.get('category')

        ActivityCategory.objects.create(name=name,category=category)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

def create_activity(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        name = request.POST.get('activity_name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        activity_date = request.POST.get('activity_date')
        activity_images = request.FILES.getlist('activity_images')

        kendra = get_object_or_404(AnandaKendra,slug=slug)
        activity_category = get_object_or_404(ActivityCategory,pk=int(category))

        print(kendra,activity_category,category)
        activity = Activity.objects.create(kendra=kendra,category=activity_category,
                                name=name,description=description,activity_date=activity_date)

        for i in activity_images:
            Photo.objects.create(kendra=kendra,picture=i,activity=activity)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

# def add_winners(request):
#     if request.method == 'POST':
#         slug = request.POST.get('slug')
#         name = request.POST.get('activity_name')
#         date = request.POST.get('date')
#         winner = request.POST.get('pk_winner')
#         runner_up1 = request.POST.get('pk_runner_up1')
#         runner_up2 = request.POST.get('pk_runner_up2')
#         activity_images = request.FILES.getlist('activity_images')

#         winner_profile = get_object_or_404(Student,pk=int(winner))
#         runner_up1_profile = get_object_or_404(Student,pk=int(runner_up1))
#         runner_up2_profile = get_object_or_404(Student,pk=int(runner_up2))

#         kendra = get_object_or_404(AnandaKendra,slug=slug)

#         activity = Activity.objects.filter(kendra=kendra).filter(name=name).filter(activity_date=date).first()
#         activity.winner = winner_profile
#         activity.runner_up1 = runner_up1_profile
#         activity.runner_up2 = runner_up2_profile
#         activity.save()

#         for i in activity_images:
#             Photo.objects.create(kendra=kendra,picture=i,activity=activity)

#         url = '/anandakendra/detail/' + slug +'/'
#         return HttpResponseRedirect(url)
#     return HttpResponseRedirect('/')

def add_to_gallery(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        activity_images = request.FILES.getlist('gallery_images')
        kendra = get_object_or_404(AnandaKendra,slug=slug)
        print("image =",activity_images)
        for i in activity_images:
            Photo.objects.create(kendra=kendra,picture=i)

        url = '/anandakendra/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')
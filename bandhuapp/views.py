from django.shortcuts import render
from accounts.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,Http404
from social_django.models import UserSocialAuth
from .models import Profile
# Create your views here.

def index(request):
    obj = UserSocialAuth.objects.all()
    obj1 = User.objects.all()
    print(obj,obj1)
    return render(request, 'landing_page.html')

def cause1(request):
    return render(request, 'cause1.html')

def cause2(request):
    return render(request, 'cause2.html')

def cause3(request):
    return render(request, 'cause3.html')

def cause4(request):
    return render(request, 'cause4.html')

def cause5(request):
    return render(request, 'cause5.html')

@login_required
def create_profile(request):
    user = request.user.email
    obj = Profile.objects.filter(email=user).first()
    full_name = ""
    contact = ""
    address = ""
    city = ""
    profession = ""
    date_of_birth = ""
    if obj:
        full_name = obj.full_name
        contact = obj.phone
        address = obj.address
        city = obj.city
        profession = obj.profession
        date_of_birth = obj.dob
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        city = request.POST.get('city')
        profession = request.POST.get('profession')
        date_of_birth = request.POST.get('date_of_birth')
        Profile.objects.create(full_name=full_name,email=request.user.email,phone=contact,address=address,city=city,profession=profession,dob=date_of_birth)
        return HttpResponseRedirect('/')
    return render(request,'profile.html',{'full_name':full_name,'contact':contact,'address':address,'city':city,'prof':profession,'date_of_birth':date_of_birth})
















        #

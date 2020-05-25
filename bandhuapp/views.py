from django.shortcuts import render
from accounts.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,Http404
from social_django.models import UserSocialAuth
from django.contrib import messages
from django.urls import reverse
from .models import Profile
from datetime import datetime 
from django.core.files.storage import FileSystemStorage


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
def profilePage(request):
    pro_obj = Profile.objects.filter(user=request.user).first()
    first_name = pro_obj.first_name 
    last_name = pro_obj.last_name
    gender = pro_obj.gender 
    dob = pro_obj.dob 
    profession = pro_obj.profession 
    contact_no = pro_obj.contact_no 
    street_address1 = pro_obj.street_address1 
    street_address2 = pro_obj.street_address2 
    city = pro_obj.city 
    state = pro_obj.state 
    pincode = pro_obj.pincode 
    profile_pic = pro_obj.profile_pic
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        dob = request.POST['dob']
        profession = request.POST['profession']
        contact_no = request.POST['contact_no']
        street_address1 = request.POST['street_address1']
        street_address2 = request.POST['street_address2']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        profile_pic = request.FILES.get('profile_pic')
        Profile.objects.filter(user=request.user).update(first_name=first_name, 
                                                        last_name=last_name,
                                                        gender=gender, 
                                                        dob=dob, 
                                                        profession=profession, 
                                                        contact_no=contact_no,
                                                        street_address1=street_address1, 
                                                        street_address2=street_address2,
                                                        city=city, 
                                                        state=state, 
                                                        pincode=pincode)
        if profile_pic is not None and profile_pic != '':
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            uploaded_file_url = fs.url(filename)
            print(filename,uploaded_file_url)
            Profile.objects.filter(user=request.user).update(profile_pic=profile_pic)
            profile_pic = uploaded_file_url
        return HttpResponseRedirect('/profile/')
    return render(request,'profile.html',{
        'first_name' : first_name,
        'last_name' :  last_name, 
        'gender' :  gender,  
        'dob' : dob ,  
        'profession' :  profession,
        'contact_no' :  contact_no,  
        'street_address1' :  street_address1,  
        'street_address2' :  street_address2,   
        'city' : city   ,
        'state' : state   ,
        'pincode' : pincode ,
        'profile_pic':profile_pic
    })
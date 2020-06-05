from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect,Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from social_django.models import UserSocialAuth
from accounts.models import User
from accounts.tokens import account_activation_token
from .models import Profile

# Create your views here.

def index(request):
    if request.user.is_authenticated and not Profile.objects.filter(user=request.user).exists():
        return redirect('profile_page')

    # obj = UserSocialAuth.objects.all()
    # obj1 = User.objects.all()
    # print(obj,obj1)
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
def profile_page(request):
    user = request.user
    profile = Profile.objects.filter(user=user)

    if profile.exists():
        profile = profile[0]
        first_time = False
    else:
        # Dummy object to pass into the template
        profile = Profile(user=request.user)
        # If profile is being filled for the first time
        first_time = True

    if request.method == 'POST':
        profile.first_name = request.POST['first_name']
        profile.last_name = request.POST['last_name']
        profile.gender = request.POST['gender']
        profile.dob = request.POST['dob']
        profile.profession = request.POST['profession']
        profile.contact_no = request.POST['contact_no']
        profile.street_address1 = request.POST['street_address1']
        profile.street_address2 = request.POST['street_address2']
        profile.city = request.POST['city']
        profile.state = request.POST['state']
        profile.pincode = request.POST['pincode']

        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

        profile.save()

        if first_time:
            # Notify Admin for New User Sign Up
            current_site = get_current_site(request)

            from_email = settings.SENDER_EMAIL
            mail_subject = '[noreply] New User Signed Up'
            msg = 'A new User has signed up.'
            message = render_to_string('acc_active.html', {
                'user': user,
                'profile': profile,
                'domain': current_site.domain,
                'msg':msg,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = settings.ADMINS_EMAIL
            email = EmailMessage(
                mail_subject, message, from_email, to_email,
            )
            email.send()
        
            logout(request)
            return redirect('account_activated')

        return HttpResponseRedirect('/profile/')
        
    context = {
        'profile': profile,
        'first_time': first_time,
    }
    return render(request,'profile.html', context)
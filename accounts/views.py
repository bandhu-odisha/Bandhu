from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import render,redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,Http404

from .models import User
from .tokens import account_activation_token
from .forms import RegisterForm
from bandhuapp.models import Profile

import random

# Create your views here.

def login_view(request):
    logout(request)
    err_code = 0

    if request.POST:
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)   # Returns the User object if credentials are correct AND USER IS ACTIVE

        if user is not None:
            if user.auth is False:
                err_code = 2  # Not Authenticated
            else:
                login(request, user)

                pr_obj = Profile.objects.filter(user=user)
                if pr_obj.first_name is not None:
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponseRedirect('/profile/')
        else:
            # Either Email/Password is wrong or
            # user not activated
            user_obj = User.objects.filter(email=email)
 
            if not user_obj.exists():
                # Email incorrect
                err_code = 3
            else:
                user_obj = user_obj[0]
                if user_obj.check_password(password) and user_obj.is_active is False:
                    # User not active
                    err_code = 1
                else:
                    # Password not correct
                    err_code = 3

    context = {
        'err_code' : err_code,
    }
    return render(request, 'registration/login.html', context)

def signup_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = RegisterForm(request.POST)
        email_check = request.POST.get('email')
        obj = User.objects.filter(email=email_check).first()
        if obj:
            return render(request,'signup_failure_page.html',{'message':'This Email has already been taken!!'})
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            user.refresh_from_db()
            current_site = get_current_site(request)
            print(current_site)
            mail_subject = '[noreply] Activate your Account'
            msg = 'Thanks for signing up, welcome to bandhu. You have been successfully registered.'
            message = render_to_string('acc_email_active.html', {
                'user': user,
                'domain': current_site.domain,
                'msg':msg,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            print(to_email)
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            print(email)
            email.send()
            return redirect('signup_success_page')
        else:
            return render(request,'signup_failure_page.html',{'message':'You have not been registered. Your Passwords doesnt match!!'})
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form,'done':0})

def account_activation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        current_site = get_current_site(request)
        mail_subject = '[noreply] New User Signed Up'
        msg = 'A new User has signed up.'
        message = render_to_string('acc_active.html', {
            'user': user,
            'pk':uid,
            'domain': current_site.domain,
            'msg':msg,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = "guptaheet53@gmail.com"
        print(to_email)
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        print(email)
        email.send()
        return redirect('account_activated')
    else:
        return render(request, 'token_expired.html')

def account_authentication(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.auth = True
        user.save()
        Profile.objects.create(user=user)
        # return redirect('home')
        return redirect('account_authenticated')
    else:
        return render(request, 'token_expired.html')   # Token expired

def account_activated(request):
    return render(request,'account_activated.html')

def account_authenticated(request):
    return render(request,'account_authenticated.html')

def signup_success(request):
    return render(request,'signup_success.html')

def signup_failure(request):
    return render(request,'signup_failure.html')


# def change_password(request):
#     val=3
#     usb = User.objects.filter(email=request.user.email).first()
#     stud_info = StudentInfo.objects.filter(student_id=usb).first()
#     if request.method == 'POST':
#         print(request.POST)
#         form = PasswordChangeForm(request.user, request.POST)
#         val=3
#         print("erro")
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # Important!
#             messages.success(request, 'Your password was successfully updated!')
#             val=0
#             return render(request,'change_password.html',{'message':'Your password was successfully updated!','val':val,'stud_info':stud_info})
#         else:
#             messages.error(request, 'Please correct the error below.')
#             val=1
#             if request.POST.get('new_password1') != request.POST.get('new_password2'):
#                 val=3
#                 return render(request,'change_password.html',{'message':'Your new password and confirmation dont match.!!','val':val,'stud_info':stud_info})
#             return render(request,'change_password.html',{'message':'Current Password is incorrect!!','val':val,'stud_info':stud_info})
#     else:
#         form = PasswordChangeForm(request.user)

#     return render(request, 'change_password.html', {
#         'form': form,'val':2,'stud_info':stud_info
#     })

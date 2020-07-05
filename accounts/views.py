from django.http import Http404, HttpResponseRedirect, HttpResponse
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
from django.contrib import messages

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse,Http404

from .models import User
from .tokens import account_activation_token
from .forms import RegisterForm
from bandhuapp.models import Profile

import random


def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('home')

    err_code = 0

    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        # Return the User object if credentials are correct AND USER IS ACTIVE
        user = authenticate(email=email, password=password)

        if user is not None:
            profile = Profile.objects.filter(user=user)
            # If user has filled profile and is not authenticated yet
            if user.auth is False and profile.exists():
                err_code = 2  # Not Authenticated
            else:
                login(request, user)
                
                if not profile.exists():
                    return HttpResponseRedirect('/profile/')
                else:
                    return HttpResponseRedirect('/')
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
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        email_check = request.POST.get('email')
        obj = User.objects.filter(email=email_check).first()
        if obj:
            return render(request,'signup.html',{'form': form, 'message':'This Email has already been taken!!', 'done':0})
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            user.refresh_from_db()
            current_site = get_current_site(request)
            print("123")
            from_email = settings.SENDER_EMAIL
            mail_subject = '[noreply] Activate your Account'
            msg = 'Thanks for signing up, welcome to bandhu. You have been successfully registered.'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'msg':msg,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = [form.cleaned_data.get('email')]
            email = EmailMessage(
                mail_subject, message, from_email, to_email,
            )
            email.content_subtype = "html"
            email.send()
            print("654")
            print(message)
            return redirect('signup_success_page')
        else:
            return render(request,'signup.html',{'form':form,'done': 0})
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form,'done':0})

def account_activation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Activate User Account
        user.is_active = True
        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Account Activation Successful!")
        return redirect('profile_page')
    else:
        msg = "You have either entered a wrong link or your account has already been activated."
        return render(request, 'token_expired.html', {'msg': msg, 'act_token': True})

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
        current_site = get_current_site(request)
        from_email = settings.SENDER_EMAIL
        mail_subject = '[noreply] Account Verified'
        msg = 'Your account has been verified by the admin, you can now Login to Bandhu.'
        message = render_to_string('account_verified_email.html', {
            'email': user.email,
            'msg':msg,
            'domain': current_site.domain,
        })
        to_email = [user.email]
        email = EmailMessage(
            mail_subject, message, from_email, to_email,
        )
        email.content_subtype="html"
        email.send()

        return redirect('account_authenticated')
    else:
        msg = "You have either entered a wrong link or some admin has already verified or deleted this account."
        return render(request, 'token_expired.html', {'msg': msg})

def account_deletion(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        profile = Profile.objects.filter(user=user).first()
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        context = {
            'uidb64': uidb64,
            'user': user,
            'profile': profile,
        }
        return render(request, 'account_deletion_confirmation.html', context)
    else:
        msg = "You have either entered a wrong link or some admin has already verified or deleted this account this account."
        return render(request, 'token_expired.html', {'msg': msg})

def account_deletion_confirmed(request, uidb64):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None:
        # user.profile.profile_pic.delete()  # man.png will also be deleted
        user.delete()
        current_site = get_current_site(request)
        from_email = settings.SENDER_EMAIL
        mail_subject = '[noreply] Account Deleted'
        message = render_to_string('account_emails/account_deleted_email.html', {
            'email': user.email,
        })
        to_email = [user.email]
        email = EmailMessage(
            mail_subject, message, from_email, to_email,
        )
        email.content_subtype="html"
        email.send()

        return redirect('account_deleted')
    else:
        raise Http404

def account_activated(request):
    return render(request,'account_activated.html')

def account_authenticated(request):
    return render(request,'account_authenticated.html')

def account_deleted(request):
    return render(request,'account_deleted.html')

def signup_success(request):
    return render(request,'signup_success.html')

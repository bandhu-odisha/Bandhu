from datetime import datetime, timedelta
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.static import serve

from social_django.models import UserSocialAuth
from accounts.models import User
from accounts.tokens import account_activation_token
from applications.anandakendra.models import Event as KendraEvent
from applications.ankurayan.models import Activity as AnkurayanActivity
from applications.ashram.models import Event as AshramEvent
from applications.charitywork.models import Activity as CharityActivity

import openpyxl
from openpyxl.styles import Font
from .models import (
    Profile, Photo, Initiatives, AboutUs,
    Mission, Volunteer, Gallery, Contact,
)
from .templatetags import permissions as temp_perms  # Template permissions

from openpyxl import Workbook
from openpyxl.styles import Font
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Create your views here.

def index(request):
    if request.user.is_authenticated and not Profile.objects.filter(user=request.user).exists():
        messages.error(request, "Complete your Profile first.")
        return redirect('profile_page')

    recent_events = []
    recent_events.extend(KendraEvent.objects.order_by('-date')[:10])
    recent_events.extend(AnkurayanActivity.objects.order_by('-date')[:10])
    recent_events.extend(AshramEvent.objects.order_by('-date')[:10])
    recent_events.extend(CharityActivity.objects.order_by('-date')[:10])

    recent_events.sort(key=lambda act: act.date, reverse=True)
    recent_events = recent_events[:10]

    context = {
        'initiatives': Initiatives.objects.all().first(),
        'about': AboutUs.objects.all().first(),
        'mission': Mission.objects.all().first(),
        'recent_events': recent_events,
        'volunteer': Volunteer.objects.all().first(),
        'photos': Photo.objects.filter(approved=True).order_by('-created'),
        'unapproved_photos': Photo.objects.filter(approved=False).order_by('created'),
        'curr_date': datetime.now().date(),
        'seven_day_delta': datetime.now().date() - timedelta(days=7),
    }
    return render(request, 'landing_page.html', context)

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
            if profile.profile_pic.name != 'profile_photos/man.png':
                profile.profile_pic.delete(False)
            profile.profile_pic = request.FILES['profile_pic']

        profile.save()

        if first_time:
            # Notify Admin for New User Sign Up
            current_site = get_current_site(request)

            from_email = settings.SENDER_EMAIL
            mail_subject = '[noreply] New User Signed Up'
            msg = 'A new User has signed up.'
            message = render_to_string('account_verification_email.html', {
                'user': user,
                'profile': profile,
                'domain': current_site.domain,
                'msg':msg,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = settings.ADMINS_EMAIL
            # email = EmailMessage(
            #     mail_subject, message, from_email, to_email,
            # )
            # email.content_subtype = "html"
            # email.send()

            email = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=mail_subject,
                html_content=message,
            )
            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(email)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)

            logout(request)
            return redirect('account_activated')

        return HttpResponseRedirect('/profile/')
        
    context = {
        'profile': profile,
        'first_time': first_time,
    }
    return render(request,'profile.html', context)

@login_required
def add_image(request):
    if request.method == 'POST':
        picture = request.FILES['image']
        caption = request.POST['caption']
        tag_list = request.POST.getlist('tags')

        tags = ""
        for tag in tag_list:
            tags += f'{tag} '

        if temp_perms.is_admin(request.user):
            Photo.objects.create(picture=picture, caption=caption, tags=tags, approved=True)
            messages.success(request, "Image added successfully!")
        else:
            Photo.objects.create(picture=picture, caption=caption, tags=tags)
            messages.success(request, "Image sent for admin approval")

    return HttpResponseRedirect('/')

@login_required
def approve_image(request):
    if request.method == 'POST':
        image_pk = request.POST.get('image')
        status = request.POST.get('status')

        photo = get_object_or_404(Photo, pk=int(image_pk))

        if status == "approve":
            photo.approved = True
            photo.save()
            return JsonResponse({'response': 'approved'})
        else:
            photo.picture.delete(save=False)
            photo.delete()
            return JsonResponse({'response': 'discarded'})

        
    return HttpResponseRedirect('/')

@login_required
def extract_user_data(request):
    profiles = Profile.objects.order_by('-user__is_admin')

    file_path = settings.MEDIA_ROOT + '/sheets/user_profile_data.xlsx'
    excel = Workbook()
    sheet = excel.active

    # excel = openpyxl.load_workbook(filename = file_path)
    # sheet = excel.active
    col_width = [8, 30, 20, 8, 15, 15, 13, 30, 10, 20, 10, 10]

    sheet.cell(row=1, column=1).value = 'S.No'
    sheet.cell(row=1, column=2).value = 'Email'
    sheet.cell(row=1, column=3).value = 'Name'
    sheet.cell(row=1, column=4).value = 'Gender'
    sheet.cell(row=1, column=5).value = 'Date Of Birth'
    sheet.cell(row=1, column=6).value = 'Profession'
    sheet.cell(row=1, column=7).value = 'Contact'
    sheet.cell(row=1, column=8).value = 'Address'
    sheet.cell(row=1, column=9).value = 'City'
    sheet.cell(row=1, column=10).value = 'State'
    sheet.cell(row=1, column=11).value = 'Pincode'
    sheet.cell(row=1, column=12).value = 'Admin'

    for i in range(1, 13):
        sheet.cell(row = 1, column = i).font = Font(size=12, bold=True)
        sheet.column_dimensions[chr(65+(i-1))].width=col_width[i-1]

    for row, profile in enumerate(profiles, 2): 
        sheet.cell(row=row, column=1).value = row - 1 
        sheet.cell(row=row, column=2).value = profile.user.email
        sheet.cell(row=row, column=3).value = profile.get_full_name
        sheet.cell(row=row, column=4).value = profile.gender
        sheet.cell(row=row, column=5).value = profile.dob
        sheet.cell(row=row, column=6).value = profile.profession
        sheet.cell(row=row, column=7).value = profile.contact_no
        sheet.cell(row=row, column=8).value = f'{profile.street_address1}, {profile.street_address2}'
        sheet.cell(row=row, column=9).value = profile.city
        sheet.cell(row=row, column=10).value = profile.state
        sheet.cell(row=row, column=11).value = int(profile.pincode)
        sheet.cell(row=row, column=12).value = profile.user.is_admin

    excel.save(file_path)
    return HttpResponseRedirect(settings.MEDIA_URL + '/sheets/user_profile_data.xlsx')

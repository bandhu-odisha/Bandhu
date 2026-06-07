from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from accounts.models import User
from bandhuapp.models import Profile
from bandhuapp.templatetags.permissions import is_admin
from bandhuapp import initiative_program_year as ipy
from . import models as initiative_models
from .models import (
    Ashram, Activity, Photo, Meeting,
    Attendee, ActivityCategory, Event, HomePage,
)

# Create your views here.

def index(request):
    context = ipy.build_index_context(request, 'prasantaraktadan', initiative_models)
    context.update(ipy.build_index_gallery_context(request, 'prasantaraktadan', initiative_models))
    return render(request, 'prasantaraktadan/prasantaraktadan.html', context)

@login_required
def create_ashram(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        locality = request.POST.get('locality')
        description = request.POST.get('description')
        address = request.POST.get('address')
        image = request.FILES.get('image')

        # admin = request.POST.get('admin')
        # admin_profile = get_object_or_404(Profile,pk=int(admin))

        if Ashram.objects.filter(name=name, locality=locality).exists():
            messages.error(request, "Ashram with entered Name and Locality already exists.")
            return redirect('prasantaraktadan:prasantaraktadan')

        slug = slugify(f'{name} {locality}')
        Ashram.objects.create(
            name=name,
            locality=locality,
            slug=slug,
            description=description,
            address=address,
            image=image,
            is_published=False,
        )
        messages.info(
            request,
            'Entry created as a draft. Add reports, invitation, activities, events, or gallery content to make it visible to visitors.',
        )
        return redirect('prasantaraktadan:AshramDetail', slug)

    return redirect('prasantaraktadan:prasantaraktadan')

def ashram_detail(request, slug):
    return ipy.render_year_detail(request, slug, 'prasantaraktadan', initiative_models)


upload_report_file = ipy.make_upload_report_file('prasantaraktadan', initiative_models)
add_report_link = ipy.make_add_report_link('prasantaraktadan', initiative_models)
delete_report_file = ipy.make_delete_report_file('prasantaraktadan', initiative_models)
delete_report_link = ipy.make_delete_report_link('prasantaraktadan', initiative_models)
upload_invitation = ipy.make_upload_invitation('prasantaraktadan', initiative_models)
delete_invitation = ipy.make_delete_invitation('prasantaraktadan', initiative_models)
update_description = ipy.make_update_description('prasantaraktadan', initiative_models)

@login_required
def add_attendee(request):
    if request.method == 'POST':
        schedule = request.POST.get('schedule')
        topic = request.POST.get('topic')
        slug = request.POST.get('slug')

        name = request.POST.get('name')
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')

        attende = request.POST.get('attendes')
        attendes = attende.split(",")
        meeting = Meeting.objects.filter(schedule=schedule).filter(topic=topic).first()

        if name:
            Attendee.objects.create(meeting=meeting,name=name,
                                contact_no=contact_no,email=email)
        else:
            for i in attendes:
                profile = Profile.objects.filter(user__email=i).first()
                Attendee.objects.create(meeting=meeting,profile=profile)
        
        url = '/prasanta-raktadan-shibir/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')
  
@login_required      
def add_meeting(request):
    if request.method == 'POST':
        slug = request.POST.get('slug')
        ashram = get_object_or_404(Ashram,slug=slug)

        topic = request.POST.get('topic')
        agenda = request.POST.get('agenda')
        schedule = request.POST.get('schedule')
        location = request.POST.get('location')
        minutes = request.FILES.get('minutes')

        Meeting.objects.create(minutes=minutes,topic=topic,agenda=agenda,
                                    schedule=schedule,location=location,
                                    ashram=ashram)

        url = '/prasanta-raktadan-shibir/detail/' + slug +'/'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect('/')

add_activity_category = ipy.make_add_activity_category('prasantaraktadan', initiative_models)
create_activity = ipy.make_create_activity('prasantaraktadan', initiative_models)
add_to_gallery = ipy.make_add_to_gallery('prasantaraktadan', initiative_models)

@login_required
def admin_approval(request):
    if request.method == 'POST':
        slug = request.POST.get('prasantaraktadan')
        image_pk = request.POST.get('image')
        status = request.POST.get('status')

        ashram = get_object_or_404(Ashram,slug=slug)
        photo = get_object_or_404(Photo,pk=int(image_pk))
        if status == "approve":
            photo.approved = True
            photo.save()
            ipy.maybe_publish_entry(ashram, initiative_models)
        else:
            photo.delete()
        
        if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
            url = reverse('prasantaraktadan:AshramDetail', kwargs={'slug': slug}) + '#gallery'
            return HttpResponseRedirect(url)

        photos = Photo.objects.filter(ashram=ashram)
        data = serializers.serialize('json', photos)
        return JsonResponse(data, safe=False)
    return HttpResponseRedirect('/')

create_event = ipy.make_create_event('prasantaraktadan', initiative_models)
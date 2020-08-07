from .models import Profile
from applications.anandakendra.models import Acharya
from applications.anandakendra.models import Activity as anandakendra_activity
from applications.ankurayan.models import Activity as ankurayan_activity
# from applications.sanskarbarga.models import Activity as sanskarbarga_activity
from applications.charitywork.models import Activity as charitywork_activity
from applications.ashram.models import Activity as ashram_activity
# from applications.madhmukti.models import Activity as madhmukti_activity
from bandhuapp.models import RecentActivity, Gallery, Contact

# Create your views here.
def userList(request):
    users = list(Profile.objects.all().exclude(first_name=None))
    acharya = list(Acharya.objects.all())
    ach_list = {}
    for i in acharya:
        ach_list[i.acharya_id] = ach_list.get(i.acharya_id,0) + 1
    rm_users = []
    for i in users:
        if ach_list.get(i) is None:
            rm_users.append(i)
    return {'users': rm_users,'all_users':users}
    
def recent_activities(request):
    recent_act = RecentActivity.objects.all().order_by('-date_created')
    gallery = Gallery.objects.all().first()
    contact = Contact.objects.all().first()
    return {
        'recent_activities':  recent_act,
        'gallery': gallery,
        'contact': contact,
    }
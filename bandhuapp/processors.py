from .models import Profile
from applications.anandakendra.models import Acharya
from applications.anandakendra.models import Activity as anandakendra_activity
from applications.ankurayan.models import Activity as ankurayan_activity
# from applications.sanskarbarga.models import Activity as sanskarbarga_activity
from applications.charitywork.models import Activity as charitywork_activity
from applications.ashram.models import Activity as ashram_activity
# from applications.madhmukti.models import Activity as madhmukti_activity
from bandhuapp.models import RecentActivity as recent_acts

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
    recent_act = recent_acts.objects.all().order_by('-date')
    # anandakendra_act = anandakendra_activity.objects.all().order_by('activity_date')[0]
    # ankurayan_act = ankurayan_activity.objects.all().order_by('-activity_date').first()
    # charitywork_act = charitywork_activity.objects.all().order_by('activity_date')[0]
    # sanskarbarga_act = sanskarbarga_activity.objects.all().order_by('activity_date')
    # madhmukti_act = madhmukti_activity.objects.all().order_by('activity_date')
    # ashram_act = ashram_activity.objects.all().order_by('activity_date')[0]
    # recent_act = [anandakendra_act, ankurayan_act, charitywork_act, ashram_act]
    # recent_act = []
    # if ankurayan_act:
    #     recent_act = [ankurayan_act]
    # recent_act.sort(key=lambda x: x.activity_date, reverse=True)
    return {'recent_activities' :  recent_act}
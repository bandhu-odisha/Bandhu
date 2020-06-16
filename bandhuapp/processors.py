from .models import Profile
from applications.anandakendra.models import Acharya

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
    return {'users': rm_users}
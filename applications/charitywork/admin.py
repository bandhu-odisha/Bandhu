from django.contrib import admin
from .models import Charity,Volunteer,Activity,Photo
# Register your models here.

admin.site.register(Charity)
admin.site.register(Volunteer)
admin.site.register(Activity)
admin.site.register(Photo)

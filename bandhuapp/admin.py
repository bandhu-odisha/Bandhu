from django.contrib import admin
from django.utils.html import format_html, urlencode

from accounts.admin_form_utils import admin_form_with_user
from .admin_forms import (
    AdminAddProfileForm,
    DesignationAdminForm,
    DesignationRoleAdminForm,
    PeoplesDesignationAdminForm,
    PeoplesDesignationInlineFormSet,
    StaffExperienceAdminForm,
    StaffExperienceInlineForm,
)
from .models import (
    Designation, DesignationRole, PeoplesDesignation, Profile, RecentActivity, Photo,
    Initiatives, AboutUs, Mission, SanskarCarousel, Staff, StaffExperience,
    StaffExperiencePhoto, SwarajCarousel, SwabalambanCarousel,
    UrlData, Video, Volunteer, Gallery, Contact, HomePage, HomeVisitor, CurrentUpdates,
    AnnualReport,
)

# Register your models here.

class SanskarCarouselInline(admin.StackedInline):
    model = SanskarCarousel

class SwarajCarouselInline(admin.StackedInline):
    model = SwarajCarousel

class SwabalambanCarouselInline(admin.StackedInline):
    model = SwabalambanCarousel


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'profession', 'city')
    search_fields = ('first_name', 'last_name', 'user__email')
    ordering = ('first_name', 'last_name')

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = AdminAddProfileForm
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            return admin_form_with_user(form, request.user)
        return form

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (None, {
                    'fields': ('first_name', 'last_name', 'email', 'admin_password'),
                    'description': (
                        'Creates a login account with no password. '
                        'Email is optional. The member is pre-approved (active and authorised) '
                        'and never receives admin access. '
                        'If you enter your own admin email, confirm with your password; '
                        'the member still gets a separate login. '
                        'Add address and other details on the profile edit page later.'
                    ),
                }),
            )
        return (
            (None, {'fields': ('user',)}),
            ('Personal', {
                'fields': (
                    'first_name', 'last_name', 'gender', 'dob', 'profession',
                    'contact_no', 'profile_pic',
                ),
            }),
            ('Address', {
                'fields': (
                    'street_address1', 'street_address2', 'city', 'state', 'pincode',
                ),
            }),
        )

admin.site.register(Initiatives)
admin.site.register(AboutUs)

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    inlines = [SanskarCarouselInline, SwarajCarouselInline, SwabalambanCarouselInline]

admin.site.register(Volunteer)
admin.site.register(Gallery)
admin.site.register(Contact)

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'notice_file')

    def save_model(self, request, obj, form, change):
        """Updating link and deleting file if file is removed."""
        if change and not obj.notice_file:
            pre_instance = RecentActivity.objects.filter(id=obj.id)
            if (pre_instance.exists() and pre_instance[0].notice_file and
                    obj.link == pre_instance[0].notice_file.url):
                pre_instance[0].notice_file.delete(False)
                obj.link = '#'
        super().save_model(request, obj, form, change)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'picture', 'approved')

# @admin.register(SanskarCarousel)
# class SanskarCarouselAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'picture')

# @admin.register(SwarajCarousel)
# class SwarajCarouselAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'picture')

# @admin.register(SwabalambanCarousel)
# class SwabalambanCarouselAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'picture')

admin.site.register(HomePage)


@admin.register(HomeVisitor)
class HomeVisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'occupation', 'place', 'photo_thumb', 'sort_order', 'is_published')
    readonly_fields = ('photo_preview',)

    def photo_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" alt="" height="36" width="36" style="object-fit:cover;border-radius:50%;" />',
                obj.photo.url,
            )
        return '—'
    photo_thumb.short_description = 'Photo'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" alt="" style="max-height:120px;border-radius:8px;" />',
                obj.photo.url,
            )
        return 'No photo uploaded (default man/woman illustration is used).'
    photo_preview.short_description = 'Current photo'
    list_editable = ('sort_order', 'is_published')
    list_filter = ('is_published', 'avatar')
    search_fields = ('name', 'occupation', 'place', 'quote')
    ordering = ('sort_order', 'name')
    fieldsets = (
        (None, {
            'fields': (
                'name', 'occupation', 'place', 'avatar', 'photo', 'photo_preview',
                'sort_order', 'is_published',
            ),
        }),
        ('Story', {
            'fields': ('quote', 'about'),
        }),
        ('Social links', {
            'fields': ('facebook_url', 'linkedin_url'),
            'classes': ('collapse',),
        }),
    )


@admin.register(UrlData)
class UrlDataAdmin(admin.ModelAdmin):
    list_display = ('url', 'shorten_url', 'times_followed', 'created')
    def shorten_url(self,url_data):
        return format_html('<a href="/links/{}">{}</a>', url_data.hash, url_data.hash)

@admin.register(CurrentUpdates)
class CurrentUpdatesAdmin(admin.ModelAdmin):
    list_display = ('created_at','desc','url')


@admin.register(AnnualReport)
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ('year', 'display_title', 'link_type', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    list_editable = ('is_published',)
    search_fields = ('title', 'year', 'external_url')
    ordering = ('-year',)
    readonly_fields = ('pdf_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': (
                'year',
                'title',
                'is_published',
            ),
            'description': (
                'Add one row per year. Upload a PDF <strong>or</strong> paste a public '
                'Google Drive link (Share → anyone with the link). If both are set, '
                'the uploaded PDF is used in the footer.'
            ),
        }),
        ('Report file', {
            'fields': ('pdf_file', 'pdf_preview', 'external_url'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def display_title(self, obj):
        return obj.display_title()

    display_title.short_description = 'Title'

    def link_type(self, obj):
        if obj.pdf_file:
            return 'PDF upload'
        if (obj.external_url or '').strip():
            return 'External link'
        return '—'

    link_type.short_description = 'Source'

    def pdf_preview(self, obj):
        if obj.pk and obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">Open PDF</a>',
                obj.pdf_file.url,
            )
        return '—'

    pdf_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

class DesignationRoleInline(admin.TabularInline):
    model = DesignationRole
    form = DesignationRoleAdminForm
    extra = 1
    fields = ("title", "rank")
    ordering = ("rank",)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    form = DesignationAdminForm
    list_display = ("rank", "title")
    inlines = [DesignationRoleInline]


class PeoplesDesignationInline(admin.StackedInline):
    model = PeoplesDesignation
    form = PeoplesDesignationAdminForm
    formset = PeoplesDesignationInlineFormSet
    extra = 1
    min_num = 0
    fields = ("designation", "role", "desc", "rank")
    verbose_name = "group membership (Core Team / Office Bearers)"
    verbose_name_plural = (
        "group memberships — Core Team once (Role empty). "
        "For multiple office positions, add several Office Bearers rows with different roles."
    )

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 2
        return 1


class PeoplesDesignationAdminMedia:
    js = ("bandhuapp/js/admin_peoples_designation.js",)


class StaffExperiencePhotoInline(admin.TabularInline):
    model = StaffExperiencePhoto
    extra = 1
    fields = ("image_preview", "image", "caption")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-height:56px;max-width:88px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Preview"


class StaffExperienceInline(admin.StackedInline):
    model = StaffExperience
    form = StaffExperienceInlineForm
    extra = 0
    fields = ("message", "image", "image_caption", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("profile", "designation_list", "about")
    search_fields = (
        "profile__first_name",
        "profile__last_name",
        "profile__user__email",
    )
    inlines = [PeoplesDesignationInline, StaffExperienceInline]
    fieldsets = (
        (
            None,
            {
                "fields": ("profile", "about", "qualifications", "webpage"),
                "description": (
                    "Assign groups under <strong>Group memberships</strong> below. "
                    "Core Team: one row, Role empty. Office Bearers: one row per position "
                    "(e.g. Treasurer on one row, Joint Secretary on another)."
                ),
            },
        ),
        (
            "Social links",
            {
                "classes": ("collapse",),
                "fields": ("facebook", "twitter", "linkedin", "youtube"),
            },
        ),
    )

    def designation_list(self, obj):
        labels = [
            str(pd) for pd in obj.designations.select_related("designation", "role")
        ]
        return ", ".join(labels) if labels else "—"

    designation_list.short_description = "Groups"

    class Media(PeoplesDesignationAdminMedia):
        pass


@admin.register(DesignationRole)
class DesignationRoleAdmin(admin.ModelAdmin):
    form = DesignationRoleAdminForm
    list_display = ("designation", "title", "rank")
    list_filter = ("designation",)
    ordering = ("designation__rank", "rank")
    search_fields = ("title", "designation__title")


# PeoplesDesignation: no standalone admin — use Staff → Group memberships inline only.

@admin.register(StaffExperience)
class StaffExperienceAdmin(admin.ModelAdmin):
    form = StaffExperienceAdminForm
    list_display = ("staff", "message_preview", "created_at", "photo_count")
    list_filter = ("created_at",)
    search_fields = (
        "message",
        "staff__profile__first_name",
        "staff__profile__last_name",
        "staff__profile__user__email",
    )
    readonly_fields = ("created_at",)
    fields = ("staff", "message", "image", "image_caption", "created_at")
    inlines = [StaffExperiencePhotoInline]

    def message_preview(self, obj):
        text = (obj.message or "").strip()
        return text[:80] + ("…" if len(text) > 80 else "")

    message_preview.short_description = "Message"

    def photo_count(self, obj):
        return obj.photos.count()

    photo_count.short_description = "Photos"


@admin.register(StaffExperiencePhoto)
class StaffExperiencePhotoAdmin(admin.ModelAdmin):
    list_display = ("experience", "caption", "image_preview", "created_at_display")
    list_filter = ("experience__staff",)
    search_fields = (
        "caption",
        "experience__message",
        "experience__staff__profile__first_name",
        "experience__staff__profile__last_name",
    )
    autocomplete_fields = ("experience",)
    fields = ("experience", "image", "caption")

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-height:72px;max-width:120px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Preview"

    def created_at_display(self, obj):
        return obj.experience.created_at if obj.experience_id else "—"

    created_at_display.short_description = "Experience date"


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'created_at')
    fields = ('title', 'duration', 'script')
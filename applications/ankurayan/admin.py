from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from .models import (
    Ankurayan, Participant, Guest, GuestNote,
    ActivityCategory, Activity, Photo,
    HomePage, AnkurayanReportFile, AnkurayanPublicationFile,
    AnkurayanInvitationLetter,
)

@admin.register(Ankurayan)
class AnkurayanAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('year',)}
    list_display = ('theme', 'year', 'start_date', 'end_date')
    ordering = ('year',)
    search_fields = ('year', 'theme', 'locality')
    fieldsets = (
        (None, {'fields': ('year', 'title', 'theme', 'slug', 'logo', 'start_date', 'end_date')}),
        ('Content', {'fields': ('description', 'reports', 'publications', 'visitors')}),
    )

    def response_add(self, request, obj, post_url_continue=None):
        next_site = request.GET.get('next')
        if next_site == 'ankurayan_details':
            return HttpResponseRedirect(reverse('ankurayan:AnkurayanDetail', args=(obj.slug,)))

        return super(AnkurayanAdmin, self).response_add(request, obj, post_url_continue)

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_year',)
    list_filter = ('ankurayan__year',)
    ordering = ('-ankurayan__year', 'name',)
    search_fields = ('name', 'ankurayan__year')

    def get_year(self, obj):
        return obj.ankurayan.year
    get_year.short_description = 'Ankurayan Year'
    get_year.admin_order_field = 'ankurayan__year'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'date', 'winner','runner_up1','runner_up1')
    ordering = ('-date',)
    search_fields = ('name', 'category__ankurayan__year','category__ankurayan__theme','category__name')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name','ankurayan', 'contact_no','school_class')
    ordering = ('name',)
    list_filter = ('school_class',)
    search_fields = ('name', 'ankurayan__year','ankurayan__theme',)

class GuestNoteInline(admin.TabularInline):
    model = GuestNote
    extra = 0


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'ankurayan', 'profession', 'quote_preview')
    list_editable = ('sort_order',)
    search_fields = ('name', 'ankurayan__year', 'ankurayan__theme', 'quote')
    inlines = (GuestNoteInline,)
    fieldsets = (
        (None, {
            'fields': (
                'ankurayan', 'name', 'profession', 'avatar', 'photo',
                'sort_order', 'email', 'contact_no',
            ),
        }),
        ('Profile', {'fields': ('about', 'quote')}),
        ('Social links', {
            'fields': ('facebook_url', 'linkedin_url'),
            'classes': ('collapse',),
        }),
    )

    def quote_preview(self, obj):
        if not obj.quote:
            return '—'
        return (obj.quote[:50] + '…') if len(obj.quote) > 50 else obj.quote
    quote_preview.short_description = 'Quote'
    ordering = ('ankurayan', 'sort_order', 'name')
    list_filter = ('ankurayan__year',)


@admin.register(GuestNote)
class GuestNoteAdmin(admin.ModelAdmin):
    list_display = ('guest', 'note_preview', 'created_at')
    list_filter = ('guest__ankurayan__year',)
    search_fields = ('note', 'guest__name')
    ordering = ('-created_at',)

    def note_preview(self, obj):
        t = (obj.note or '').strip()
        return (t[:60] + '…') if len(t) > 60 else (t or '—')
    note_preview.short_description = 'Note'

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('ankurayan','activity','approved')
    ordering = ('ankurayan',)
    list_filter = ('approved',)
    search_fields = ('activity', 'ankurayan__year','ankurayan__theme',)


@admin.register(AnkurayanReportFile)
class AnkurayanReportFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'ankurayan', 'uploaded_at')
    list_filter = ('ankurayan__year',)
    search_fields = ('title', 'ankurayan__year')


@admin.register(AnkurayanPublicationFile)
class AnkurayanPublicationFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'ankurayan', 'uploaded_at')
    list_filter = ('ankurayan__year',)
    search_fields = ('title', 'ankurayan__year')


@admin.register(AnkurayanInvitationLetter)
class AnkurayanInvitationLetterAdmin(admin.ModelAdmin):
    list_display = ('ankurayan', 'uploaded_at')
    list_filter = ('ankurayan__year',)
    search_fields = ('ankurayan__year', 'ankurayan__title')
    autocomplete_fields = ('ankurayan',)


admin.site.register(HomePage)

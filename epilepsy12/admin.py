from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from semantic_admin import SemanticModelAdmin
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
from .models import *

from .forms import Epilepsy12UserChangeForm, Epilepsy12UserCreationForm


class Epilepsy12UserAdmin(UserAdmin, SimpleHistoryAdmin):
    add_form = Epilepsy12UserCreationForm
    form = Epilepsy12UserChangeForm
    ordering = ['email']
    model = Epilepsy12User
    search_fields = ('email', 'surname',
                     'role', 'hospital_employer', 'is_active',)
    list_display = ('id', "email", "title", "first_name", "surname",
                    "is_active", "twitter_handle", "role", "hospital_employer", 'is_superuser', "is_rcpch_audit_team_member", "email_confirmed")
    list_filter = ("is_active", "role", "hospital_employer",)
    fieldsets = (
        (
            None, {
                'fields': (
                    'title',
                    'first_name',
                    'surname',
                )
            }
        ),
        (
            'Epilepsy12 Centre', {
                'fields': (
                    'hospital_employer',
                    'role'
                )
            }
        ),
        (
            'Contacts', {
                'fields': (
                    'email',
                    'twitter_handle'
                )
            }
        ),
        (
            'Permissions', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_rcpch_audit_team_member',
                    'is_superuser',
                    "email_confirmed",
                    "view_preference",
                )
            }
        ),
        (
            'Group Permissions', {
                'classes': ('collapse',),
                'fields': (
                    'groups', 'user_permissions',
                )
            }
        ),
        (
            'Personal', {
                'fields': ('bio',)
            }
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'title', 'first_name', 'surname', 'is_staff', 'is_active', 'is_rcpch_audit_team_member', 'role', 'hospital_employer', 'is_superuser', 'groups')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['hospital_employer'].required = False
        if not request.user.is_superuser:
            self.exclude = ['is_superuser']
        else:
            self.exclude = []
        if request.user.groups.filter(name='trust_audit_team_edit_access'):
            form.base_fields['groups'].disabled = True
            form.base_fields['first_name'].disabled = True
            form.base_fields['surname'].disabled = True
            form.base_fields['title'].disabled = True
            form.base_fields['email'].disabled = True
            form.base_fields['is_staff'].disabled = True
        return form


admin.site.register(Epilepsy12User, Epilepsy12UserAdmin)
admin.site.register(AntiEpilepsyMedicine, SimpleHistoryAdmin)
admin.site.register(Assessment, SimpleHistoryAdmin)
admin.site.register(Case, SimpleHistoryAdmin)
admin.site.register(Comorbidity, SimpleHistoryAdmin)
admin.site.register(EpilepsyContext, SimpleHistoryAdmin)
admin.site.register(Investigations, SimpleHistoryAdmin)
admin.site.register(HospitalTrust, SimpleHistoryAdmin)
admin.site.register(FirstPaediatricAssessment, SimpleHistoryAdmin)
admin.site.register(Management, SimpleHistoryAdmin)
admin.site.register(Registration, SimpleHistoryAdmin)
admin.site.register(Keyword, SimpleHistoryAdmin)
admin.site.register(Site, SimpleHistoryAdmin)
admin.site.register(AuditProgress)
admin.site.register(Episode, SimpleHistoryAdmin)
admin.site.register(MultiaxialDiagnosis, SimpleHistoryAdmin)
admin.site.register(Syndrome, SimpleHistoryAdmin)
admin.site.register(KPI)
admin.site.register(VisitActivity)

admin.site.site_header = 'Epilepsy12 admin'
admin.site.site_title = 'Epilepsy12 admin'
admin.site.index_title = 'Epilepsy12'
admin.site.site_url = '/epilepsy12/'

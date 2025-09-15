# -*- coding: utf-8 -*-

import csv
import datetime
import tarfile
from io import StringIO

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import smart_bytes
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from djspace.application.models import *
from djspace.core.admin import PROFILE_LIST_DISPLAY
from djspace.core.admin import GenericAdmin
from djspace.core.models import UserFiles
from djspace.core.utils import admin_display_file
from djspace.registration.admin import PROFILE_HEADERS
from djspace.registration.admin import get_profile_fields
from openpyxl import load_workbook
from openpyxl.writer.excel import save_virtual_workbook


FUNDED_FILES = (
    ('', '---Select---'),
    ('academics_pdf', 'Academic Posters, Presentations, Papers'),
    ('biography', 'Biography'),
    ('budget', 'Budget'),
    ('close_out_finance_document', 'Close Out Finance Document'),
    ('critical_design_report', 'Critical Design Report'),
    ('interim_progress_report', 'Critical Design Report (NOI)'),
    ('cv', 'CV'),
    ('education_outreach', 'Education Outreach'),
    ('final_design_report', 'Final Design Report'),
    ('final_report', 'Final Report'),
    ('flight_demo', 'Flight Demo'),
    ('flight_readiness_report', 'Flight Readiness Report'),
    ('flysheet_1', 'Flysheet 1'),
    ('flysheet_2', 'Flysheet 2'),
    ('flysheet_3', 'Flysheet 3'),
    ('flysheet_4', 'Flysheet 4'),
    ('interim_progress_report', 'Interim Progress Report'),
    ('interim_report', 'Interim Report'),
    ('invoice_q1', 'Invoice Q1'),
    ('invoice_q2', 'Invoice Q2'),
    ('invoice_q3', 'Invoice Q3'),
    ('invoice_q4', 'Invoice Q4'),
    ('lodging_list', 'Lodging List'),
    ('mugshot', 'Mugshot'),
    ('stories_pdf', 'News Articles/Stories '),
    ('oral_presentation', 'Oral Presentation'),
    ('other_file', 'Other File'),
    ('post_flight_performance_report', 'Post Flight Performance Report'),
    ('preliminary_design_report', 'Preliminary Design Report'),
    ('intended_program_match', 'Program Match'),
    ('proposal', 'Proposal'),
    ('openrocketrocksim', 'RockSim Design Review 1'),
    ('openrocketrocksim2', 'RockSim Design Review 2'),
    ('openrocketrocksim3', 'RockSim Design Review 3'),
    ('openrocketrocksim4', 'RockSim Design Review 4'),
    ('virtual_cdr', 'Virtual Critical Design Report'),
    ('virtual_frr', 'Virtual Flight Readiness Report'),
    ('virtual_pdr', 'Virtual Preliminary Design Report'),
    ('institutional_w9', 'W9 Institutional'),
    ('irs_w9', 'W9 Personal'),
)


def required_files(modeladmin, request, queryset):
    """Export required program files for all applicants to a tarball."""
    if queryset:
        object_name = modeladmin.model._meta.object_name
        response = HttpResponse(content_type='application/x-gzip')
        response['Content-Disposition'] = 'attachment; filename={0}.tar.gz'.format(
            object_name,
        )
        tar_ball = tarfile.open(fileobj=response, mode='w:gz')
        for instance in queryset:
            for field in instance.required_files():
                phile = getattr(instance, field)
                if phile:
                    path = phile.path
                    path_list = path.split('/')
                    name = path_list[-1]
                    tar_ball.add(path, arcname=name)
        tar_ball.close()
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Currently, there are no applications for this program.",
            extra_tags='danger',
        )
        response = HttpResponseRedirect(
            reverse_lazy(
                'admin:application_{0}_changelist'.format(object_name.lower()),
            ),
        )
    return response


def export_required_files(modeladmin, request, queryset):
    """Export required files."""
    return required_files(modeladmin, request, queryset)


export_required_files.short_description = "Export Required Files"


def photo_files(modeladmin, request, queryset):
    """Export photos for all applicants to a tarball."""
    if queryset:
        object_name = modeladmin.model._meta.object_name
        response = HttpResponse(content_type='application/x-gzip')
        response['Content-Disposition'] = 'attachment; filename={0}.tar.gz'.format(
            object_name,
        )
        tar_ball = tarfile.open(fileobj=response, mode='w:gz')
        for instance in queryset:
            fotos = instance.photos.all()
            for index, foto in enumerate(fotos):
                path = '{0}/{1}'.format(settings.MEDIA_ROOT, str(foto.phile))
                path_list = path.split('/')
                name = '{0}_{1}_{2}'.format(instance.id, index, path_list[-1])
                tar_ball.add(path, name)
        tar_ball.close()
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Currently, there are no applications for this program.",
            extra_tags='danger',
        )
        response = HttpResponseRedirect(
            reverse_lazy(
                'admin:application_{0}_changelist'.format(object_name.lower()),
            ),
        )

    return response


def export_photo_files(modeladmin, request, queryset):
    """Export photo files."""
    return photo_files(modeladmin, request, queryset)


export_photo_files.short_description = "Export Photos"


def longitudinal_tracking(modeladmin, request):
    """Export application data to OpenXML file."""
    users = User.objects.all().order_by('last_name')
    program = None
    exports = []
    for user in users:
        try:
            apps = user.profile.applications.all()
        except Exception:
            apps = None
        if apps:
            for app in apps:
                status = (
                    app._meta.object_name == modeladmin.model._meta.object_name and
                    app.status
                )
                if status:
                    exports.append({'user': user, 'app': app})
                    program = app.get_slug()

    # this could all be accomplished by a list of lists but building a list
    # for each row would be ugly. this seems more pythonic, and we can reuse
    # for CSV export if need be.
    today = datetime.date.today()
    template = loader.get_template('application/export.longitudinal.html')
    context = {'exports': exports, 'program': program, 'year': today.year}
    rendered_data = smart_bytes(
        template.render(context, request),
        encoding='utf-8',
        strings_only=False,
        errors='strict',
    )
    response = HttpResponse(rendered_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={0}.csv'.format(
        program,
    )

    return response


def export_longitudinal_tracking(modeladmin, request, extra_context=None):
    """Export application data to CSV for NASA reporting requirements."""
    return longitudinal_tracking(modeladmin, request)


export_longitudinal_tracking.short_description = "Export Longitudinal Tracking"


def export_applications(modeladmin, request, queryset, reg_type=None):
    """Export application data to CSV."""
    file_fields = [
        'cv',
        'proposal',
        'letter_interest',
        'budget',
        'undergraduate_transcripts',
        'graduate_transcripts',
        'recommendation',
        'recommendation_1',
        'recommendation_2',
        'high_school_transcripts',
        'wsgc_advisor_recommendation',
        'statement',
    ]
    username_fields = [
        'co_advisor1',
        'co_advisor2',
        'co_advisor3',
        'leader',
        'grants_officer',
        'grants_officer2',
    ]
    exclude = [
        'user',
        'userprofile',
        'user_id',
        'updated_by_id',
        'id',
        'aerospaceoutreach',
        'clarkgraduatefellowship',
        'first_nations_rocket_competition',
        'collegiate_rocket_competition',
        'earlystageinvestigator',
        'midwest_high_powered_rocket_competition',
        'graduatefellowship',
        'undergraduateaerospacedesignresearchscholarship',
        'highaltitudeballoonlaunch',
        'highereducationinitiatives',
        'industryinternship',
        'nasacompetition',
        'researchinfrastructure',
        'specialinitiatives',
        'undergraduateresearch',
        'undergraduatescholarship',
        'unmannedaerialvehiclesresearchscholarship',
    ]

    field_names = [field.name for field in modeladmin.model._meta.get_fields()]
    headers = PROFILE_HEADERS + field_names
    # remove unwanted headers
    for exclu in exclude:
        if exclu in headers:
            headers.remove(exclu)

    csv.register_dialect('pipes', delimiter='|')
    buffy = StringIO()
    writer = csv.writer(buffy, dialect='pipes')
    writer.writerow(headers)

    slug = None
    for reg in queryset:
        if not slug:
            slug = reg.get_slug()
        fields = []
        profile_fields = get_profile_fields(reg)
        # deal with non-standard characters
        for prof in profile_fields:
            fields.append(smart_str(prof))
        field_names = [field.name for field in reg._meta.get_fields()]
        for name in field_names:
            if name and name not in exclude:
                attr = getattr(reg, name, None)
                if attr != '':
                    if name == 'synopsis':
                        attr = strip_tags(attr).strip()
                    elif name in file_fields:
                        earl = 'https://{0}{1}{2}'.format(
                            settings.SERVER_URL, settings.MEDIA_URL, attr,
                        )
                        attr = '=HYPERLINK("{0}","{1}")'.format(earl, name)
                    elif name in username_fields:
                        if attr:
                            attr = '{0}, {1} ({2})'.format(
                                attr.last_name, attr.first_name, attr.email,
                            )
                fields.append(attr)
        writer.writerow(fields)
    wb = load_workbook(
        '{0}/application/applications.xlsx'.format(settings.ROOT_DIR),
    )
    ws = wb.active
    reader = csv.reader(StringIO(buffy.getvalue()), dialect='pipes')
    for row in reader:
        ws.append(row)

    # in memory response instead of save to file system
    response = HttpResponse(
        save_virtual_workbook(wb), content_type='application/ms-excel',
    )

    response['Content-Disposition'] = 'attachment;filename={0}.xlsx'.format(slug)

    return response


def export_all_applications(modeladmin, request, queryset):
    """Export application data to CSV for all registration types."""
    return export_applications(modeladmin, request, queryset)


export_all_applications.short_description = "Export All Applications"


def _build_tarball(queryset, object_name, field, userfiles=False):
    """Private function to build a tarball."""
    response = HttpResponse(content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename={0}_{1}.tar.gz'.format(
        object_name, field,
    )
    tar_ball = tarfile.open(fileobj=response, mode='w:gz')
    for row in queryset:
        if userfiles:
            # some users might not have a user_files relationship
            try:
                row = row.user.user_files
            except Exception:
                row = None
        if row:
            phile = getattr(row, field, None)
            if phile:
                path = phile.path
                path_list = path.split('/')
                name = path_list[-1]
                tar_ball.add(path, arcname=name)
    tar_ball.close()

    return response


def export_funded_files(modeladmin, request, queryset):
    """Generate a tarball of files for funded programs."""
    phile = request.POST['phile']
    if not phile:
        messages.add_message(
            request,
            messages.ERROR,
            "You must choose a file name.",
            extra_tags='danger',
        )
    else:
        object_name = modeladmin.model._meta.object_name
        if phile in [f.name for f in modeladmin.model._meta.get_fields()]:
            response = _build_tarball(queryset, object_name, phile)
            return response
        elif phile in [f.name for f in UserFiles._meta.get_fields()]:
            response = _build_tarball(
                queryset, object_name, phile, userfiles=True,
            )
            return response
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "The file you requested is not in the current program.",
                extra_tags='danger',
            )


export_funded_files.short_description = "Export Funded Files"


class TarballActionForm(ActionForm):
    """Admin Form class for exporting data to a tarball."""

    phile = forms.CharField(
        label="File name",
        required=False,
        widget=forms.Select(choices=FUNDED_FILES),
    )


class UndergraduateAerospaceDesignResearchScholarshipAdmin(GenericAdmin):
    """Admin class for Undergraduate Aerospace Design Research Scholarship."""

    model = UndergraduateAerospaceDesignResearchScholarship

    list_display = PROFILE_LIST_DISPLAY + [
        'signed_certification',
        'cv_file',
        'position',
        'commit_short',
        'letter_interest_file',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = ['funded_code', 'complete', 'status']
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def cv_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'cv')
    cv_file.allow_tags = True
    cv_file.short_description = "CV"

    def commit_short(self, instance):
        """Return Commitment status."""
        return instance.commit
    commit_short.short_description = "Commitment"

    def letter_interest_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'letter_interest')
    letter_interest_file.allow_tags = True
    letter_interest_file.short_description = "Interest"


class HighAltitudeBalloonLaunchAdmin(UndergraduateAerospaceDesignResearchScholarshipAdmin):
    """Admin class for High Altitude Balloon Launch."""

    model = HighAltitudeBalloonLaunch

    list_display = PROFILE_LIST_DISPLAY + [
        'signed_certification',
        'cv_file',
        'letter_interest_file',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]


class UnmannedAerialVehiclesResearchScholarshipAdmin(UndergraduateAerospaceDesignResearchScholarshipAdmin):
    """Admin class for Unmanned Aerial Vehicles Research Scholarship."""

    model = UnmannedAerialVehiclesResearchScholarship

    list_display = PROFILE_LIST_DISPLAY + [
        'cv_file',
        'letter_interest_file',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]


class ClarkGraduateFellowshipAdmin(GenericAdmin):
    """Admin class for Clark Graduate Fellowhsip."""

    model = ClarkGraduateFellowship

    list_display = PROFILE_LIST_DISPLAY + [
        'signed_certification',
        'proposal_file',
        'cv_file',
        'budget_file',
        'undergraduate_transcripts_file',
        'graduate_transcripts_file',
        'recommendation_1_file',
        'recommendation_2_file',
        'project_title',
        'begin_date',
        'end_date',
        'anticipating_funding',
        'funds_requested',
        'funds_authorized',
        'synopsis_trunk',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = ['funds_authorized', 'funded_code', 'complete', 'status']
    list_display_links = ['project_title']
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def synopsis_trunk(self, instance):
        """Return the truncated synopsis text."""
        return Truncator(instance.synopsis).words(
            25, html=True, truncate=' ...',
        )
    synopsis_trunk.allow_tags = True
    synopsis_trunk.short_description = "Synopsis truncated"

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal')
    proposal_file.allow_tags = True
    proposal_file.short_description = 'Proposal'

    def cv_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'cv')
    cv_file.allow_tags = True
    cv_file.short_description = "CV"

    def budget_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget')
    budget_file.allow_tags = True
    budget_file.short_description = "Budget"

    def undergraduate_transcripts_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'undergraduate_transcripts')
    undergraduate_transcripts_file.allow_tags = True
    undergraduate_transcripts_file.short_description = "UG Trans"

    def graduate_transcripts_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'graduate_transcripts')
    graduate_transcripts_file.allow_tags = True
    graduate_transcripts_file.short_description = "GR Trans"

    def recommendation_1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'recommendation_1')
    recommendation_1_file.allow_tags = True
    recommendation_1_file.short_description = "Recom 1"

    def recommendation_2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'recommendation_2')
    recommendation_2_file.allow_tags = True
    recommendation_2_file.short_description = "Recom 2"


class GraduateFellowshipAdmin(ClarkGraduateFellowshipAdmin):
    """Admin class for Graduate Fellowhsip."""

    model = GraduateFellowship


class UndergraduateAdmin(GenericAdmin):
    """Base admin class for the various undergrad applications."""

    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def high_school_transcripts_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'high_school_transcripts')
    high_school_transcripts_file.allow_tags = True
    high_school_transcripts_file.short_description = "HS Trans"

    def undergraduate_transcripts_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'undergraduate_transcripts')
    undergraduate_transcripts_file.allow_tags = True
    undergraduate_transcripts_file.short_description = "UG Trans"

    def wsgc_advisor_recommendation_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'wsgc_advisor_recommendation')
    wsgc_advisor_recommendation_file.allow_tags = True
    wsgc_advisor_recommendation_file.short_description = "WSGC Advisor Recom"

    def recommendation_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'recommendation')
    recommendation_file.allow_tags = True
    recommendation_file.short_description = "Recommendation"


class UndergraduateResearchAdmin(UndergraduateAdmin):
    """Admin class for Undergraduate Research."""

    model = UndergraduateResearch

    list_display = PROFILE_LIST_DISPLAY + [
        'signed_certification',
        'proposal_file',
        'high_school_transcripts_file',
        'undergraduate_transcripts_file',
        'wsgc_advisor_recommendation_file',
        'recommendation_file',
        'project_title',
        'begin_date',
        'end_date',
        'funds_authorized',
        'other_funding',
        'other_funding_explain',
        'synopsis_trunk',
        'other_funding',
        'other_funding_explain',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = ['funds_authorized', 'funded_code', 'complete', 'status']
    list_display_links = ['project_title']

    def synopsis_trunk(self, instance):
        return Truncator(instance.synopsis).words(
            25, html=True, truncate=' ...',
        )
    synopsis_trunk.allow_tags = True
    synopsis_trunk.short_description = "Synopsis truncated"

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal')
    proposal_file.allow_tags = True
    proposal_file.short_description = 'Proposal'


class UndergraduateScholarshipAdmin(UndergraduateAdmin):
    """Admin class for Undergraduate Scholarship."""

    model = UndergraduateScholarship

    list_display = PROFILE_LIST_DISPLAY + [
        'signed_certification',
        'statement_file',
        'high_school_transcripts_file',
        'undergraduate_transcripts_file',
        'wsgc_advisor_recommendation_file',
        'recommendation_file',
        'academic_institution',
        'wsgc_affiliate',
        'other_funding',
        'other_funding_explain',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = ['funded_code', 'complete', 'status']

    def statement_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'statement')
    statement_file.allow_tags = True
    statement_file.short_description = 'Statement'


class WomenInAviationScholarshipAdmin(UndergraduateScholarshipAdmin):
    """Admin class for Aviation Scholarship."""

    model = WomenInAviationScholarship


class StemBridgeScholarshipAdmin(UndergraduateScholarshipAdmin):
    """Admin class for STEM Bridge Scholarship."""

    model = StemBridgeScholarship


class RocketLaunchTeamAdmin(GenericAdmin):
    """Admin class for Rocke Launch Team (NOI)."""

    model = RocketLaunchTeam

    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    search_fields = (
        'user__last_name',
        'user__first_name',
        'user__email',
        'co_advisor1__last_name',
        'co_advisor1__first_name',
        'co_advisor1__email',
        'co_advisor2__last_name',
        'co_advisor2__first_name',
        'co_advisor2__email',
        'co_advisor3__last_name',
        'co_advisor3__first_name',
        'co_advisor3__email',
        'leader__last_name',
        'leader__first_name',
        'leader__email',
        'grants_officer__last_name',
        'grants_officer__first_name',
        'grants_officer__email',
        'grants_officer2__last_name',
        'grants_officer2__first_name',
        'grants_officer2__email',
    )

    list_display = PROFILE_LIST_DISPLAY + [
        'budget_file',
        'proposal_file',
        'interim_progress_report_file',
        'virtual_cdr_file',
        'preliminary_design_report_file',
        'virtual_pdr_file',
        'final_design_report_file',
        'flight_demo_file',
        'openrocketrocksim_file',
        'openrocketrocksim2_file',
        'openrocketrocksim3_file',
        'openrocketrocksim4_file',
        'flysheet_1_file',
        'flysheet_2_file',
        'flysheet_3_file',
        'flysheet_4_file',
        'invoice_q1_file',
        'invoice_q2_file',
        'invoice_q3_file',
        'invoice_q4_file',
        'final_motor_selection_trunk',
        'lodging_list_file',
        'critical_design_report_file',
        'post_flight_performance_report_file',
        'education_outreach_file',
        'flight_readiness_report_file',
        'virtual_frr_file',
        'proceeding_paper_file',
        'name',
        'competition',
        'grants_officer_name',
        'grants_officer2_name',
        'co_advisor1_name',
        'co_advisor2_name',
        'co_advisor3_name',
        'leader_name',
        'industry_mentor_name',
        'industry_mentor_email',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_display_links = ['name']
    list_editable = ['funded_code', 'complete', 'status']
    raw_id_fields = (
        'user',
        'co_advisor1',
        'co_advisor2',
        'co_advisor3',
        'leader',
        'members',
    )

    def grants_officer_name(self, obj):
        name = None
        if obj.grants_officer:
            name = mark_safe('<a href="mailto:{0}">{1}, {2} ({3})</a>'.format(
                obj.grants_officer.email,
                obj.grants_officer.last_name,
                obj.grants_officer.first_name,
                obj.grants_officer.email,
            ))
        return name
    grants_officer_name.allow_tags = True
    grants_officer_name.short_description = "Authorized User"

    def grants_officer2_name(self, obj):
        name = None
        if obj.grants_officer2:
            name = mark_safe('<a href="mailto:{0}">{1}, {2} ({3})</a>'.format(
                obj.grants_officer2.email,
                obj.grants_officer2.last_name,
                obj.grants_officer2.first_name,
                obj.grants_officer2.email,
            ))
        return name
    grants_officer2_name.allow_tags = True
    grants_officer2_name.short_description = "Authorized User 2"

    def co_advisor1_name(self, obj):
        name = None
        if obj.co_advisor1:
            name = mark_safe('<a href="mailto:{0}">{1}, {2} ({3})</a>'.format(
                obj.co_advisor1.email,
                obj.co_advisor1.last_name,
                obj.co_advisor1.first_name,
                obj.co_advisor1.email,
            ))
        return name
    co_advisor1_name.allow_tags = True
    co_advisor1_name.short_description = "Co-Advisor"

    def co_advisor2_name(self, obj):
        name = None
        if obj.co_advisor2:
            name = mark_safe('<a href="mailto:{0}">{1}, {2} ({3})</a>'.format(
                obj.co_advisor2.email,
                obj.co_advisor2.last_name,
                obj.co_advisor2.first_name,
                obj.co_advisor2.email,
            ))
        return name
    co_advisor2_name.allow_tags = True
    co_advisor2_name.short_description = "Co-Advisor 2"

    def co_advisor3_name(self, obj):
        name = None
        if obj.co_advisor3:
            name = mark_safe('<a href="mailto:{0}">{1}, {2} ({3})</a>'.format(
                obj.co_advisor3.email,
                obj.co_advisor3.last_name,
                obj.co_advisor3.first_name,
                obj.co_advisor3.email,
            ))
        return name
    co_advisor3_name.allow_tags = True
    co_advisor3_name.short_description = "Co-Advisor 3"

    def leader_name(self, instance):
        """Return the team leader's name as link to email address."""
        name = None
        if instance.leader:
            name = mark_safe('<a href="mailto:{0}">{1}, {2} ({3})</a>'.format(
                instance.leader.email,
                instance.leader.last_name,
                instance.leader.first_name,
                instance.leader.email,
            ))
        return name
    leader_name.allow_tags = True
    leader_name.short_description = "Leader"

    def budget_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget')
    budget_file.allow_tags = True
    budget_file.short_description = "Budget"

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal')
    proposal_file.allow_tags = True
    proposal_file.short_description = "Proposal"

    def interim_progress_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'interim_progress_report')
    interim_progress_report_file.allow_tags = True
    interim_progress_report_file.short_description = "CDR"

    def virtual_cdr_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'virtual_cdr')
    virtual_cdr_file.allow_tags = True
    virtual_cdr_file.short_description = "VCDR"

    def preliminary_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'preliminary_design_report')
    preliminary_design_report_file.allow_tags = True
    preliminary_design_report_file.short_description = "Prelim design"

    def virtual_pdr_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'virtual_pdr')
    virtual_pdr_file.allow_tags = True
    virtual_pdr_file.short_description = "VPDR"

    def final_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'final_design_report')
    final_design_report_file.allow_tags = True
    final_design_report_file.short_description = "Final Design Rpt"

    def flight_demo_file(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = mark_safe('<i class="fa fa-times-circle red" aria-hidden="true"></i>')
        if instance.flight_demo:
            icon = mark_safe(
                """
                <i class="fa fa-check green" aria-hidden="true" title="{0}"></i>
                """.format(instance.flight_demo),
            )
        return icon
    flight_demo_file.allow_tags = True
    flight_demo_file.short_description = "Flight Demo URL"

    def final_motor_selection_trunk(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = mark_safe('<i class="fa fa-times-circle red" aria-hidden="true"></i>')
        if instance.final_motor_selection:
            icon = mark_safe(
                """
                <i class="fa fa-check green" aria-hidden="true" title="{0}"></i>
                """.format(instance.final_motor_selection),
            )
        return icon
    final_motor_selection_trunk.allow_tags = True
    final_motor_selection_trunk.short_description = "Final Motor"

    def lodging_list_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'lodging_list')
    lodging_list_file.allow_tags = True
    lodging_list_file.short_description = "Lodging"

    def critical_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'critical_design_report')
    critical_design_report_file.allow_tags = True
    critical_design_report_file.short_description = "Critical design"

    def oral_presentation_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'oral_presentation')
    oral_presentation_file.allow_tags = True
    oral_presentation_file.short_description = "Oral Pres."

    def post_flight_performance_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'post_flight_performance_report')
    post_flight_performance_report_file.allow_tags = True
    post_flight_performance_report_file.short_description = "Post flight"

    def education_outreach_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'education_outreach')
    education_outreach_file.allow_tags = True
    education_outreach_file.short_description = "Edu. Outreach"

    def flight_readiness_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'flight_readiness_report')
    flight_readiness_report_file.allow_tags = True
    flight_readiness_report_file.short_description = "Flight Ready"

    def virtual_frr_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'virtual_frr')
    virtual_frr_file.allow_tags = True
    virtual_frr_file.short_description = "VFRR"

    def flysheet_1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'flysheet_1')
    flysheet_1_file.allow_tags = True
    flysheet_1_file.short_description = "FLY1"

    def flysheet_2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'flysheet_2')
    flysheet_2_file.allow_tags = True
    flysheet_2_file.short_description = "FLY2"

    def flysheet_3_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'flysheet_3')
    flysheet_3_file.allow_tags = True
    flysheet_3_file.short_description = "FLY3"

    def flysheet_4_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'flysheet_4')
    flysheet_4_file.allow_tags = True
    flysheet_4_file.short_description = "FLY4"

    def invoice_q1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q1')
    invoice_q1_file.allow_tags = True
    invoice_q1_file.short_description = "INV1"

    def invoice_q2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q2')
    invoice_q2_file.allow_tags = True
    invoice_q2_file.short_description = "INV2"

    def invoice_q3_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q3')
    invoice_q3_file.allow_tags = True
    invoice_q3_file.short_description = "INV3"

    def invoice_q4_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q4')
    invoice_q4_file.allow_tags = True
    invoice_q4_file.short_description = "INV4"

    def openrocketrocksim_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'openrocketrocksim')
    openrocketrocksim_file.allow_tags = True
    openrocketrocksim_file.short_description = "ORK1"

    def openrocketrocksim2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'openrocketrocksim2')
    openrocketrocksim2_file.allow_tags = True
    openrocketrocksim2_file.short_description = "ORK2"

    def openrocketrocksim3_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'openrocketrocksim3')
    openrocketrocksim3_file.allow_tags = True
    openrocketrocksim3_file.short_description = "ORK3"

    def openrocketrocksim4_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'openrocketrocksim4')
    openrocketrocksim4_file.allow_tags = True
    openrocketrocksim4_file.short_description = "ORK4"

    def proceeding_paper_file(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = mark_safe('<i class="fa fa-times-circle red" aria-hidden="true"></i>')
        if instance.proceeding_paper:
            icon = mark_safe(
                """
                <i class="fa fa-check green" aria-hidden="true" title="{0}"></i>
                """.format(instance.proceeding_paper),
            )
        return icon
    proceeding_paper_file.allow_tags = True
    proceeding_paper_file.short_description = "Proceeding Paper Date"


class CollegiateRocketCompetitionAdmin(GenericAdmin):
    """Admin class for Collegiate Rocket Launch Competition."""

    model = CollegiateRocketCompetition

    list_display = PROFILE_LIST_DISPLAY + [
        'budget_file',
        'proposal_file',
        'preliminary_design_report_file',
        'flight_demo_file',
        'lodging_list_file',
        'oral_presentation_file',
        'critical_design_report_file',
        'post_flight_performance_report_file',
        'education_outreach_file',
        'cv_file',
        'team',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]

    list_display_links = ['team']
    list_editable = ['funded_code', 'complete', 'status']

    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def cv_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'cv')
    cv_file.allow_tags = True
    cv_file.short_description = "CV"

    def budget_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget', team=True)
    budget_file.allow_tags = True
    budget_file.short_description = "Budget"

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal', team=True)
    proposal_file.allow_tags = True
    proposal_file.short_description = "Proposal"

    def interim_progress_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'interim_progress_report', team=True)
    interim_progress_report_file.allow_tags = True
    interim_progress_report_file.short_description = "Interim Rpt"

    def preliminary_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'preliminary_design_report', team=True)
    preliminary_design_report_file.allow_tags = True
    preliminary_design_report_file.short_description = "Prelim design"

    def final_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'final_design_report', team=True)
    final_design_report_file.allow_tags = True
    final_design_report_file.short_description = "Final Design Rpt"

    def flight_demo_file(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = mark_safe('<i class="fa fa-times-circle red" aria-hidden="true"></i>')
        if instance.team.flight_demo:
            icon = mark_safe(
                """
                <a href="{0}">
                <i class="fa fa-check green" aria-hidden="true" title="{1}"></i></a>
                """.format(instance.team.flight_demo, instance.team.flight_demo),
            )
        return icon
    flight_demo_file.allow_tags = True
    flight_demo_file.short_description = "Flight Demo URL"

    def final_motor_selection_trunk(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = '<i class="fa fa-times-circle red" aria-hidden="true"></i>'
        if instance.team.final_motor_selection:
            icon = """
              <i class="fa fa-check green" aria-hidden="true" title="{0}"></i>
            """.format(instance.team.final_motor_selection)
        return icon
    final_motor_selection_trunk.allow_tags = True
    final_motor_selection_trunk.short_description = "Final Motor"

    def lodging_list_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'lodging_list', team=True)
    lodging_list_file.allow_tags = True
    lodging_list_file.short_description = "Lodging"

    def critical_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'critical_design_report', team=True)
    critical_design_report_file.allow_tags = True
    critical_design_report_file.short_description = "Critical design"

    def oral_presentation_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'oral_presentation', team=True)
    oral_presentation_file.allow_tags = True
    oral_presentation_file.short_description = "Oral Pres."

    def post_flight_performance_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(
            instance, 'post_flight_performance_report', team=True,
        )
    post_flight_performance_report_file.allow_tags = True
    post_flight_performance_report_file.short_description = "Post flight"

    def education_outreach_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'education_outreach', team=True)
    education_outreach_file.allow_tags = True
    education_outreach_file.short_description = "Edu. Outreach"

    def flight_readiness_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'flight_readiness_report', team=True)
    flight_readiness_report_file.allow_tags = True
    flight_readiness_report_file.short_description = "Flight Ready"

    def proceeding_paper_file(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = '<i class="fa fa-times-circle red" aria-hidden="true"></i>'
        if instance.team.proceeding_paper:
            icon = """
              <i class="fa fa-check green" aria-hidden="true" title="{0}"></i>
            """.format(instance.team.proceeding_paper)
        return icon
    proceeding_paper_file.allow_tags = True
    proceeding_paper_file.short_description = "Proceeding Paper Date"


class MidwestHighPoweredRocketCompetitionAdmin(GenericAdmin):
    """Admin class for Midwest High Powered Rocket Competition."""

    model = MidwestHighPoweredRocketCompetition

    list_display = PROFILE_LIST_DISPLAY + [
        'team',
        'cv_file',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_display_links = ['team']
    list_editable = ['funded_code', 'complete', 'status']
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def cv_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'cv')
    cv_file.allow_tags = True
    cv_file.short_description = "CV"


class FirstNationsRocketCompetitionAdmin(GenericAdmin):
    """Admin class for First Nations Rocket Launch Competition."""

    model = FirstNationsRocketCompetition

    list_display = PROFILE_LIST_DISPLAY + [
        'budget_file',
        'preliminary_design_report_file',
        'flight_demo_file',
        'proposal_file',
        'lodging_list_file',
        'oral_presentation_file',
        'critical_design_report_file',
        'post_flight_performance_report_file',
        'team',
        'competition',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_display_links = ['team']
    list_editable = ['funded_code', 'complete', 'status']
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    @admin.display(ordering='team__competition', description='Competition')
    def competition(self, instance):
        """Display the competition value from NOI object on admin dashboard."""
        return instance.team.competition

    def budget_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget', team=True)
    budget_file.allow_tags = True
    budget_file.short_description = "Budget"

    def preliminary_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(
            instance, 'preliminary_design_report', team=True,
        )
    preliminary_design_report_file.allow_tags = True
    preliminary_design_report_file.short_description = "Prelim design"

    def flight_demo_file(self, instance):
        """Construct display file code for the admin dashboard."""
        icon = mark_safe('<i class="fa fa-times-circle red" aria-hidden="true"></i>')
        if instance.team.flight_demo:
            icon = mark_safe(
                """
                <a href="{0}">
                <i class="fa fa-check green" aria-hidden="true" title="{1}"></i></a>
                """.format(instance.team.flight_demo, instance.team.flight_demo),
            )
        return icon
    flight_demo_file.allow_tags = True
    flight_demo_file.short_description = "Flight Demo URL"

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal', team=True)
    proposal_file.allow_tags = True
    proposal_file.short_description = "Proposal"

    def lodging_list_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'lodging_list', team=True)
    lodging_list_file.allow_tags = True
    lodging_list_file.short_description = "Lodging"

    def critical_design_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'critical_design_report', team=True)
    critical_design_report_file.allow_tags = True
    critical_design_report_file.short_description = "Critical design"

    def oral_presentation_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'oral_presentation', team=True)
    oral_presentation_file.allow_tags = True
    oral_presentation_file.short_description = "Oral Pres."

    def post_flight_performance_report_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(
            instance, 'post_flight_performance_report', team=True,
        )
    post_flight_performance_report_file.allow_tags = True
    post_flight_performance_report_file.short_description = "Post flight"


class HigherEducationInitiativesAdmin(GenericAdmin):
    """Admin class for Higher Education Incentives."""

    model = HigherEducationInitiatives

    list_display = PROFILE_LIST_DISPLAY + [
        'invoice_q1_file',
        'invoice_q2_file',
        'invoice_q3_file',
        'invoice_q4_file',
        'institutional_w9_file',
        'photos_overview_file',
        'publications_overview_file',
        'budget_modification_file',
        'performance_modification_file',
        'scope_modification_file',
        'no_cost_extension_file',
        'close_out_finance_document_file',
        'project_title',
        'begin_date',
        'end_date',
        'award_type',
        'funds_requested',
        'funds_authorized',
        'proposed_match',
        'authorized_match',
        'source_match',
        'location',
        'synopsis_trunk',
        'proposal_file',
        'finance_officer_name',
        'finance_officer_address',
        'finance_officer_email',
        'finance_officer_phone',
        'grant_officer_name',
        'grant_officer_address',
        'grant_officer_email',
        'grant_officer_phone',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = [
        'funds_authorized',
        'authorized_match',
        'funded_code',
        'complete',
        'status',
    ]
    list_display_links = ['project_title']
    date_hierarchy = 'date_created'
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def synopsis_trunk(self, instance):
        """Return a truncated bit of text from synopsis for display."""
        return Truncator(instance.synopsis).words(
            25, html=True, truncate=" ...",
        )
    synopsis_trunk.allow_tags = True
    synopsis_trunk.short_description = "Synopsis truncated"

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal')
    proposal_file.allow_tags = True
    proposal_file.short_description = 'Proposal'

    def invoice_q1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q1')
    invoice_q1_file.allow_tags = True
    invoice_q1_file.short_description = "Invoice Q1"

    def invoice_q2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q2')
    invoice_q2_file.allow_tags = True
    invoice_q2_file.short_description = "Invoice Q2"

    def invoice_q3_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q3')
    invoice_q3_file.allow_tags = True
    invoice_q3_file.short_description = "Invoice Q3"

    def invoice_q4_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q4')
    invoice_q4_file.allow_tags = True
    invoice_q4_file.short_description = "Invoice Q4"

    def institutional_w9_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'institutional_w9')
    institutional_w9_file.allow_tags = True
    institutional_w9_file.short_description = "Institutional W9"

    def photos_overview_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'photos_overview')
    photos_overview_file.allow_tags = True
    photos_overview_file.short_description = "Photos Overview"

    def publications_overview_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'publications_overview')
    publications_overview_file.allow_tags = True
    publications_overview_file.short_description = "Publications Overview"

    def budget_modification_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget_modification')
    budget_modification_file.allow_tags = True
    budget_modification_file.short_description = "Budget Modification"

    def performance_modification_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'performance_modification')
    performance_modification_file.allow_tags = True
    performance_modification_file.short_description = "Performance Modification"

    def scope_modification_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'scope_modification')
    scope_modification_file.allow_tags = True
    scope_modification_file.short_description = "Scope Modification"

    def no_cost_extension_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'no_cost_extension')
    no_cost_extension_file.allow_tags = True
    no_cost_extension_file.short_description = "No Cost Extension"

    def close_out_finance_document_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'close_out_finance_document')
    close_out_finance_document_file.allow_tags = True
    close_out_finance_document_file.short_description = "Close Out Finance Doc"


class ResearchInfrastructureAdmin(HigherEducationInitiativesAdmin):
    """Admin class for Research Infrastructure."""

    model = ResearchInfrastructure


class EarlyStageInvestigatorAdmin(HigherEducationInitiativesAdmin):
    """Admin class for Early-Stage Investigator."""

    model = EarlyStageInvestigator


class AerospaceOutreachAdmin(HigherEducationInitiativesAdmin):
    """Admin class for Aerospace Outreach."""

    model = AerospaceOutreach

    list_display = PROFILE_LIST_DISPLAY + [
        'invoice_q1_file',
        'invoice_q2_file',
        'invoice_q3_file',
        'invoice_q4_file',
        'institutional_w9_file',
        'photos_overview_file',
        'publications_overview_file',
        'budget_modification_file',
        'performance_modification_file',
        'scope_modification_file',
        'no_cost_extension_file',
        'close_out_finance_document_file',
        'project_title',
        'begin_date',
        'end_date',
        'project_category',
        'proposal_file',
        'funds_requested',
        'funds_authorized',
        'other_funding',
        'other_funding_explain',
        'proposed_match',
        'authorized_match',
        'source_match',
        'location',
        'synopsis_trunk',
        'finance_officer_name',
        'finance_officer_address',
        'finance_officer_email',
        'finance_officer_phone',
        'grant_officer_name',
        'grant_officer_address',
        'grant_officer_email',
        'grant_officer_phone',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]


class NasaCompetitionAdmin(GenericAdmin):
    """Admin class for National Competitions and Programs."""

    model = NasaCompetition
    list_display = PROFILE_LIST_DISPLAY + [
        'invoice_q1_file',
        'invoice_q2_file',
        'invoice_q3_file',
        'invoice_q4_file',
        'institutional_w9_file',
        'photos_overview_file',
        'publications_overview_file',
        'budget_modification_file',
        'performance_modification_file',
        'scope_modification_file',
        'no_cost_extension_file',
        'intended_program_match_file',
        'close_out_finance_document_file',
        'statement_file',
        'budget_file',
        'competition_type',
        'competition_type_other',
        'program_acceptance',
        'begin_date',
        'end_date',
        'funds_requested',
        'funds_authorized',
        'proposed_match',
        'authorized_match',
        'source_match',
        'finance_officer_name',
        'finance_officer_address',
        'finance_officer_email',
        'finance_officer_phone',
        'grant_officer_name',
        'grant_officer_address',
        'grant_officer_email',
        'grant_officer_phone',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_display_links = ['date_created']
    list_editable = [
        'funds_authorized',
        'authorized_match',
        'funded_code',
        'complete',
        'status',
    ]
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]

    def budget_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget')
    budget_file.allow_tags = True
    budget_file.short_description = "Budget"

    def statement_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'statement')
    statement_file.allow_tags = True
    statement_file.short_description = 'Statement'

    def invoice_q1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q1')
    invoice_q1_file.allow_tags = True
    invoice_q1_file.short_description = "Invoice Q1"

    def invoice_q2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q2')
    invoice_q2_file.allow_tags = True
    invoice_q2_file.short_description = "Invoice Q2"

    def invoice_q3_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q3')
    invoice_q3_file.allow_tags = True
    invoice_q3_file.short_description = "Invoice Q3"

    def invoice_q4_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q4')
    invoice_q4_file.allow_tags = True
    invoice_q4_file.short_description = "Invoice Q4"

    def institutional_w9_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'institutional_w9')
    institutional_w9_file.allow_tags = True
    institutional_w9_file.short_description = "Institutional W9"

    def photos_overview_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'photos_overview')
    photos_overview_file.allow_tags = True
    photos_overview_file.short_description = "Photos Overview"

    def publications_overview_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'publications_overview')
    publications_overview_file.allow_tags = True
    publications_overview_file.short_description = "Publications Overview"

    def budget_modification_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget_modification')
    budget_modification_file.allow_tags = True
    budget_modification_file.short_description = "Budget Modification"

    def performance_modification_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'performance_modification')
    performance_modification_file.allow_tags = True
    performance_modification_file.short_description = "Performance Modification"

    def scope_modification_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'scope_modification')
    scope_modification_file.allow_tags = True
    scope_modification_file.short_description = "Scope Modification"

    def no_cost_extension_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'no_cost_extension')
    no_cost_extension_file.allow_tags = True
    no_cost_extension_file.short_description = "No Cost Extension"

    def intended_program_match_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'intended_program_match')
    intended_program_match_file.allow_tags = True
    intended_program_match_file.short_description = "Intended program match"

    def close_out_finance_document_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'close_out_finance_document')
    close_out_finance_document_file.allow_tags = True
    close_out_finance_document_file.short_description = "Close Out Finance Doc"


class SpecialInitiativesAdmin(AerospaceOutreachAdmin):
    """Admin class for Special Initiatives."""

    model = SpecialInitiatives


'''
class WorkPlanTaskInline(admin.TabularInline):
    """Inline Admin class for Work Plan Task."""

    model = WorkPlanTask
    fields = ('title', 'description', 'hours_percent', 'expected_outcome')
'''


class IndustryInternshipAdmin(GenericAdmin):
    """Admin class for Industry Internship."""

    list_display = PROFILE_LIST_DISPLAY + [
        'budget_file',
        'invoice_q1_file',
        'invoice_q2_file',
        'invoice_q3_file',
        'invoice_q4_file',
        'intended_program_match_file',
        'close_out_finance_document_file',
        'award_type',
        'funds_requested',
        'funds_authorized',
        'proposed_match',
        'authorized_match',
        'source_match',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    model = IndustryInternship
    list_display_links = ['first_name']
    list_editable = [
        'funds_authorized',
        'authorized_match',
        'funded_code',
        'complete',
        'status',
    ]
    action_form = TarballActionForm
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_required_files,
        export_funded_files,
        export_photo_files,
        'email_applicants',
    ]
    #inlines = [WorkPlanTaskInline]

    def budget_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'budget')
    budget_file.allow_tags = True
    budget_file.short_description = "Budget"

    def invoice_q1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q1')
    invoice_q1_file.allow_tags = True
    invoice_q1_file.short_description = "Invoice Q1"

    def invoice_q2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q2')
    invoice_q2_file.allow_tags = True
    invoice_q2_file.short_description = "Invoice Q2"

    def invoice_q3_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q3')
    invoice_q3_file.allow_tags = True
    invoice_q3_file.short_description = "Invoice Q3"

    def invoice_q4_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q4')
    invoice_q4_file.allow_tags = True
    invoice_q4_file.short_description = "Invoice Q4"

    def intended_program_match_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'intended_program_match')
    intended_program_match_file.allow_tags = True
    intended_program_match_file.short_description = "Intended program match"

    def close_out_finance_document_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'close_out_finance_document')
    close_out_finance_document_file.allow_tags = True
    close_out_finance_document_file.short_description = "Close Out Finance Doc"


class ProfessionalProgramStudentAdmin(GenericAdmin):
    """Admin class for Professional Program for Students."""

    model = ProfessionalProgramStudent
    list_display = PROFILE_LIST_DISPLAY + [
        'signed_certification',
        'program_link',
        'program_application_link',
        'mentor',
        'past_funding',
        'past_funding_year',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = ['funded_code', 'complete', 'status']
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_photo_files,
        'email_applicants',
    ]

    def program_application_link(self, instance):
        """Return link to program application."""
        return instance.program_application_link()
    program_application_link.allow_tags = True
    program_application_link.short_description = "Program Application"

    def program_link(self, instance):
        """Construct link to admin update view."""
        return mark_safe('<a href="{0}">{1}</a>'.format(
            reverse(
                'admin:application_professionalprogramstudent_change',
                args=(instance.id,),
            ),
            instance.program,
        ))
    program_link.allow_tags = True
    program_link.short_description = 'Program Name (view/edit)'


class OtherProgramAdmin(GenericAdmin):
    """Admin class for Other Program."""

    model = OtherProgram
    list_display = PROFILE_LIST_DISPLAY + [
        'proposal_file',
        'invoice_q1_file',
        'invoice_q2_file',
        'funded_code',
        'complete',
        'status',
    ]
    list_editable = ['funded_code', 'complete', 'status']
    actions = [
        export_longitudinal_tracking,
        export_all_applications,
        export_photo_files,
    ]

    def proposal_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'proposal')
    proposal_file.allow_tags = True
    proposal_file.short_description = "Proposal"

    def invoice_q1_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q1')
    invoice_q1_file.allow_tags = True
    invoice_q1_file.short_description = "Reimbursement 1"

    def invoice_q2_file(self, instance):
        """Construct display file code for the admin dashboard."""
        return admin_display_file(instance, 'invoice_q2')
    invoice_q2_file.allow_tags = True
    invoice_q2_file.short_description = "Reimbursement 2"


admin.site.register(
    HigherEducationInitiatives, HigherEducationInitiativesAdmin,
)
admin.site.register(
    ResearchInfrastructure, ResearchInfrastructureAdmin,
)
admin.site.register(
    EarlyStageInvestigator, EarlyStageInvestigatorAdmin,
)
admin.site.register(
    AerospaceOutreach, AerospaceOutreachAdmin,
)
admin.site.register(
    SpecialInitiatives, SpecialInitiativesAdmin,
)
admin.site.register(
    RocketLaunchTeam, RocketLaunchTeamAdmin,
)
admin.site.register(
    FirstNationsRocketCompetition, FirstNationsRocketCompetitionAdmin,
)
admin.site.register(
    CollegiateRocketCompetition, CollegiateRocketCompetitionAdmin,
)
admin.site.register(
    MidwestHighPoweredRocketCompetition,
    MidwestHighPoweredRocketCompetitionAdmin,
)
admin.site.register(
    HighAltitudeBalloonLaunch, HighAltitudeBalloonLaunchAdmin,
)
admin.site.register(
    UndergraduateAerospaceDesignResearchScholarship, UndergraduateAerospaceDesignResearchScholarshipAdmin,
)
admin.site.register(
    ClarkGraduateFellowship, ClarkGraduateFellowshipAdmin,
)
admin.site.register(
    GraduateFellowship, GraduateFellowshipAdmin,
)
admin.site.register(
    NasaCompetition, NasaCompetitionAdmin,
)
admin.site.register(
    StemBridgeScholarship, StemBridgeScholarshipAdmin,
)
admin.site.register(
    UndergraduateScholarship, UndergraduateScholarshipAdmin,
)
admin.site.register(
    WomenInAviationScholarship, WomenInAviationScholarshipAdmin,
)
admin.site.register(
    UndergraduateResearch, UndergraduateResearchAdmin,
)
admin.site.register(
    UnmannedAerialVehiclesResearchScholarship,
    UnmannedAerialVehiclesResearchScholarshipAdmin,
)
admin.site.register(
    IndustryInternship, IndustryInternshipAdmin,
)
admin.site.register(
    ProfessionalProgramStudent, ProfessionalProgramStudentAdmin,
)
admin.site.register(
    OtherProgram, OtherProgramAdmin,
)

# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.safestring import mark_safe
from djspace.application.models import *
from djspace.core.models import PAST_FUNDING_YEAR_CHOICES
from djspace.core.utils import get_start_date
from djtools.fields import BINARY_CHOICES
from djtools.fields.localflavor import USPhoneNumberField


# UploadsForms are for the user dashboard where file uploads
# take place after the application has been approved and
# additional files are required


class HigherEducationInitiativesForm(forms.ModelForm):
    """Higher Education Initiatives Form."""

    budget = forms.FileField(
        help_text="""
            Note the spend down date requirement in the
            Announcement of Opportunity.
        """,
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    finance_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grant_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(HigherEducationInitiativesForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = HigherEducationInitiatives
        fields = (
            'project_title',
            'award_type',
            'funds_requested',
            'proposed_match',
            'source_match',
            'past_funding',
            'past_funding_year',
            'anticipating_funding',
            'other_fellowship',
            'other_fellowship_explain',
            'begin_date',
            'end_date',
            'location',
            'synopsis',
            'proposal',
            'budget',
            'finance_officer_name',
            'finance_officer_title',
            'finance_officer_address',
            'finance_officer_email',
            'finance_officer_phone',
            'grant_officer_name',
            'grant_officer_title',
            'grant_officer_address',
            'grant_officer_email',
            'grant_officer_phone',
            'grants_officer',
            'grants_officer2',
            'member_1',
            'member_2',
            'member_3',
            'member_4',
            'member_5',
            'member_6',
            'member_7',
            'member_8',
            'member_9',
            'member_10',
        )

    def clean(self):
        """Deal with grants officer(s)."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None


class HigherEducationInitiativesUploadsForm(forms.ModelForm):
    """Higher Education Initiatives uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = HigherEducationInitiatives
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'close_out_finance_document',
        )


class ResearchInfrastructureForm(forms.ModelForm):
    """Research Infrastructure form."""

    budget = forms.FileField(
        help_text="""
            Note the spend down date requirement in the
            Announcement of Opportunity.
        """,
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    finance_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grant_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(ResearchInfrastructureForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = ResearchInfrastructure
        fields = (
            'project_title',
            'award_type',
            'funds_requested',
            'proposed_match',
            'source_match',
            'past_funding',
            'past_funding_year',
            'anticipating_funding',
            'other_fellowship',
            'other_fellowship_explain',
            'begin_date',
            'end_date',
            'location',
            'synopsis',
            'proposal',
            'budget',
            'nasa_mission_directorate',
            'nasa_mission_directorate_other',
            'finance_officer_name',
            'finance_officer_title',
            'finance_officer_address',
            'finance_officer_email',
            'finance_officer_phone',
            'grant_officer_name',
            'grant_officer_title',
            'grant_officer_address',
            'grant_officer_email',
            'grant_officer_phone',
            'grants_officer',
            'grants_officer2',
            'member_1',
            'member_2',
            'member_3',
            'member_4',
            'member_5',
            'member_6',
            'member_7',
            'member_8',
            'member_9',
            'member_10',
        )

    def clean(self):
        """Deal with grants officer."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None


class ResearchInfrastructureUploadsForm(forms.ModelForm):
    """Research Infrastructure uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = ResearchInfrastructure
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'close_out_finance_document',
        )


class EarlyStageInvestigatorForm(forms.ModelForm):
    """Early-Stage Investigator form."""

    budget = forms.FileField(
        help_text="""
            Note the spend down date requirement in the
            Announcement of Opportunity.
        """,
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    finance_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grant_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(EarlyStageInvestigatorForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = EarlyStageInvestigator
        fields = (
            'project_title',
            'award_type',
            'funds_requested',
            'proposed_match',
            'source_match',
            'past_funding',
            'past_funding_year',
            'anticipating_funding',
            'other_fellowship',
            'other_fellowship_explain',
            'begin_date',
            'end_date',
            'location',
            'synopsis',
            'proposal',
            'budget',
            'nasa_mission_directorate',
            'nasa_mission_directorate_other',
            'finance_officer_name',
            'finance_officer_title',
            'finance_officer_address',
            'finance_officer_email',
            'finance_officer_phone',
            'grant_officer_name',
            'grant_officer_title',
            'grant_officer_address',
            'grant_officer_email',
            'grant_officer_phone',
            'grants_officer',
            'grants_officer2',
            'member_1',
            'member_2',
            'member_3',
            'member_4',
            'member_5',
            'member_6',
            'member_7',
            'member_8',
            'member_9',
            'member_10',
        )

    def clean(self):
        """Deal with grants officer."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None


class EarlyStageInvestigatorUploadsForm(forms.ModelForm):
    """Early-Stage Investigator uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = EarlyStageInvestigator
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'close_out_finance_document',
        )


class AerospaceOutreachForm(forms.ModelForm):
    """Aerospace Outreach Form."""

    budget = forms.FileField(
        help_text="""
            Note the spend down date requirement in the
            Announcement of Opportunity.
        """,
    )
    project_category = forms.TypedChoiceField(
        choices=PROJECT_CATEGORIES, widget=forms.RadioSelect(),
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    finance_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grant_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(AerospaceOutreachForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = AerospaceOutreach
        fields = (
            'project_title',
            'project_category',
            'funds_requested',
            'proposed_match',
            'source_match',
            'past_funding',
            'past_funding_year',
            'anticipating_funding',
            'other_funding',
            'other_funding_explain',
            'begin_date',
            'end_date',
            'location',
            'synopsis',
            'proposal',
            'budget',
            'nasa_mission_directorate',
            'nasa_mission_directorate_other',
            'finance_officer_name',
            'finance_officer_title',
            'finance_officer_address',
            'finance_officer_email',
            'finance_officer_phone',
            'grant_officer_name',
            'grant_officer_title',
            'grant_officer_address',
            'grant_officer_email',
            'grant_officer_phone',
            'grants_officer',
            'grants_officer2',
            'member_1',
            'member_2',
            'member_3',
            'member_4',
            'member_5',
            'member_6',
            'member_7',
            'member_8',
            'member_9',
            'member_10',
        )

    def clean(self):
        """Deal with grants officer."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None


class AerospaceOutreachUploadsForm(forms.ModelForm):
    """Aerospace Outreach uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = AerospaceOutreach
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'close_out_finance_document',
        )


class SpecialInitiativesForm(forms.ModelForm):
    """Special Initiatives Form."""

    budget = forms.FileField(
        help_text="""
            [PDF format]
            Note the spend down date requirement in the
            Announcement of Opportunity.
        """,
    )
    project_category = forms.TypedChoiceField(
        choices=PROJECT_CATEGORIES, widget=forms.RadioSelect(),
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    proposed_match = forms.IntegerField(
        label="Proposed match (1:1 mimimum)(in $)",
        help_text="""
            Match must be 50% for ongoing program;
            25% for new innovated programs (or)
            programs with significant legacy value.
        """,
    )
    source_match = forms.CharField(
        label="Source(s) of match",
        help_text="""
            Overhead (or indirect costs) cannot exceed 0.5
            of the required matching funds
        """,
    )
    finance_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grant_officer_phone = USPhoneNumberField(
        label="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        widget=forms.TextInput(attrs={'class': 'phone'}),
        required=True,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(SpecialInitiativesForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = SpecialInitiatives
        fields = (
            'project_title',
            'project_category',
            'funds_requested',
            'proposed_match',
            'source_match',
            'past_funding',
            'past_funding_year',
            'anticipating_funding',
            'other_funding',
            'other_funding_explain',
            'begin_date',
            'end_date',
            'location',
            'synopsis',
            'proposal',
            'budget',
            'nasa_mission_directorate',
            'nasa_mission_directorate_other',
            'finance_officer_name',
            'finance_officer_title',
            'finance_officer_address',
            'finance_officer_email',
            'finance_officer_phone',
            'grant_officer_name',
            'grant_officer_title',
            'grant_officer_address',
            'grant_officer_email',
            'grant_officer_phone',
            'grants_officer',
            'grants_officer2',
            'member_1',
            'member_2',
            'member_3',
            'member_4',
            'member_5',
            'member_6',
            'member_7',
            'member_8',
            'member_9',
            'member_10',
        )

    def clean(self):
        """Deal with grants officer."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None


class SpecialInitiativesUploadsForm(forms.ModelForm):
    """Special Initiatives uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = SpecialInitiatives
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'close_out_finance_document',
        )


class UndergraduateScholarshipForm(forms.ModelForm):
    """Undergraduate Scholarship Form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    academic_institution = forms.TypedChoiceField(
        label="Application submitted for",
        widget=forms.RadioSelect(),
        choices=ACADEMIC_INSTITUTIONS,
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = UndergraduateScholarship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
        )


class UndergraduateScholarshipUploadsForm(forms.ModelForm):
    """Undergraduate Scholarship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = UndergraduateScholarship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
        )


class StemBridgeScholarshipForm(forms.ModelForm):
    """STEM Bridge Scholarship form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    academic_institution = forms.TypedChoiceField(
        label="Application submitted for",
        widget=forms.RadioSelect(),
        choices=ACADEMIC_INSTITUTIONS,
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = StemBridgeScholarship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
        )


class StemBridgeScholarshipUploadsForm(forms.ModelForm):
    """STEM Bridge Scholarship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = StemBridgeScholarship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
        )


class WomenInAviationScholarshipForm(forms.ModelForm):
    """Women in Aviation Scholarship form."""

    statement = forms.FileField(
        help_text=mark_safe("""
            Maximum two-page statement containing the following:
            <ol class="help_text">
            <li>interest in aviation</li>
            <li>experience in aviation (coursework, pilot training, etc.)</li>
            <li>benefit of attending the 2020 Women in Aviation conference</li>
            <li>future plan to participate in aviation as a career, hobby, etc./<li>
            </ol> [PDF format]
        """),
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    academic_institution = forms.TypedChoiceField(
        label="Application submitted for",
        widget=forms.RadioSelect(),
        choices=ACADEMIC_INSTITUTIONS,
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = WomenInAviationScholarship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
        )


class WomenInAviationScholarshipUploadsForm(forms.ModelForm):
    """Women in Aviation Scholarship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = WomenInAviationScholarship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
        )


class UndergraduateResearchForm(forms.ModelForm):
    """Undergraduate Research form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = UndergraduateResearch
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'funds_requested',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
        )


class UndergraduateResearchUploadsForm(forms.ModelForm):
    """Undergraduate Research uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = UndergraduateResearch
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
        )


class GraduateFellowshipForm(forms.ModelForm):
    """Graduate Fellowship form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time graduate or professional student
        at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = GraduateFellowship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
        )


class GraduateFellowshipUploadsForm(forms.ModelForm):
    """Graduate Fellowship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = GraduateFellowship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
        )


class ClarkGraduateFellowshipForm(forms.ModelForm):
    """Clark Graduate Fellowship form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time graduate or professional student
        at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = ClarkGraduateFellowship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
        )


class ClarkGraduateFellowshipUploadsForm(forms.ModelForm):
    """Clark Graduate Fellowship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = ClarkGraduateFellowship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
        )


class UndergraduateAerospaceDesignResearchScholarshipForm(forms.ModelForm):
    """Undergraduate Aerospace Design Research Scholarship"""

    commit = forms.TypedChoiceField(
        label="""
            Will you be able to commit 32-40 hours/week
            to this 10-week summer experience?
        """,
        required=True,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="Do you currently hold another Federal fellowship or traineeship?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = UndergraduateAerospaceDesignResearchScholarship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
            'team_photo',
            'team_biography',
        )


class UndergraduateAerospaceDesignResearchScholarshipUploadsForm(forms.ModelForm):
    """Undergraduate Aerospace Design Research Scholarship."""

    class Meta:
        """Attributes about the form and options."""

        model = UndergraduateAerospaceDesignResearchScholarship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'team_photo',
            'team_biography',
        )


class HighAltitudeBalloonLaunchForm(forms.ModelForm):
    """High Altitude Balloon Launch form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = HighAltitudeBalloonLaunch
        exclude = (
            'complete',
            'user',
            'status',
            'commit',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
            'team_photo',
            'team_biography',
        )


class HighAltitudeBalloonLaunchUploadsForm(forms.ModelForm):
    """High Altitude Balloon Launch uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = HighAltitudeBalloonLaunch
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'team_photo',
            'team_biography',
        )


class UnmannedAerialVehiclesResearchScholarshipForm(forms.ModelForm):
    """Unmanned Aerial Vehicles Research Scholarship form."""

    commit = forms.TypedChoiceField(
        label="""
            Will you be able to commit 32-40 hours/week
            to this 10-week summer experience?
        """,
        required=True,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="Do you currently hold another Federal fellowship or traineeship?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )

    class Meta:
        """Attributes about the form and options."""

        model = UnmannedAerialVehiclesResearchScholarship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'url1',
            'url2',
            'url3',
            'team_photo',
            'team_biography',
        )


class UnmannedAerialVehiclesResearchScholarshipUploadsForm(forms.ModelForm):
    """Unmanned Aerial Vehicles Research Scholarship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = UnmannedAerialVehiclesResearchScholarship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'team_photo',
            'team_biography',
        )


class RocketLaunchTeamForm(forms.ModelForm):
    """Form that handles the create/update for Rocket Launch Teams."""

    uid = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    co_advisor1 = forms.CharField(
        label="Co-Advisor 1",
        required=False,
        help_text="""
            Co-Advisor must be registered for auto-population of this field.
        """,
    )
    co_advisor2 = forms.CharField(
        label="Co-Advisor 2",
        required=False,
        help_text="""
            Co-Advisor must be registered for auto-population of this field.
        """,
    )
    co_advisor3 = forms.CharField(
        label="Co-Advisor 3",
        required=False,
        help_text="""
            Co-Advisor must be registered for auto-population of this field.
        """,
    )
    leader = forms.CharField(
        label="Team Lead",
        required=True,
        help_text="""
            Team Leads must be registered for auto-population of this field.
        """,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )

    class Meta:
        """Attributes about the form and options."""

        model = RocketLaunchTeam
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'members',
            'award_acceptance',
            'interim_progress_report',
            'interim_report',
            'team_roster',
            'preliminary_design_report',
            'final_design_report',
            'final_report',
            'flight_demo',
            'lodging_list',
            'flysheet_1',
            'flysheet_2',
            'flysheet_3',
            'flysheet_4',
            'openrocketrocksim',
            'openrocketrocksim2',
            'openrocketrocksim3',
            'openrocketrocksim4',
            'oral_presentation',
            'other_file',
            'other_file2',
            'other_file3',
            'critical_design_report',
            'proceeding_paper',
            'flight_readiness_report',
            'post_flight_performance_report',
            'education_outreach',
            'verified_budget',
            'final_motor_selection',
            'close_out_finance_document',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'charges_certification',
            'institutional_w9',
            'url1',
            'url2',
            'url3',
            'team_photo',
            'team_biography',
            'academics_url',
            'academics_pdf',
            'stories_url',
            'stories_pdf',
            'virtual_cdr',
            'virtual_pdr',
            'virtual_frr',
        )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(RocketLaunchTeamForm, self).__init__(*args, **kwargs)

    def clean(self):
        """Deal with the auto populate fields."""
        error = False
        cd = self.cleaned_data
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['co_advisor1'] = cd.get('co_advisor1')
        authuser['co_advisor2'] = cd.get('co_advisor2')
        authuser['co_advisor3'] = cd.get('co_advisor3')
        authuser['leader'] = cd.get('leader')
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # verify authorized user(s)
        for key, aid in authuser.items():
            if aid in uids:
                self.add_error(
                    key,
                    "User already has a role on this team.",
                )
                cd[key] = None
                error = True
            elif aid:
                uids.append(aid)
        # convert authorized users from ID to User object
        for key, aid in authuser.items():
            if aid:
                sesh_key = '{0}_name'.format(key)
                user = User.objects.filter(pk=aid).first()
                if user and user.profile:
                    cd[key] = user
                    full_name = '{0}, {1}'.format(user.last_name, user.first_name)
                    self.request.session[sesh_key] = full_name
                else:
                    self.add_error(
                        key,
                        "This user does not have a complete profile",
                    )
                    cd[key] = None
            else:
                cd[key] = None
        return cd


class RocketLaunchTeamUploadsForm(forms.ModelForm):
    """Rocket Launch Team uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = RocketLaunchTeam
        fields = (
            'award_acceptance',
            'interim_progress_report',
            'preliminary_design_report',
            'final_design_report',
            'flight_demo',
            'lodging_list',
            'openrocketrocksim',
            'openrocketrocksim2',
            'openrocketrocksim3',
            'openrocketrocksim4',
            'other_file',
            'other_file2',
            'other_file3',
            'critical_design_report',
            'oral_presentation',
            'post_flight_performance_report',
            'education_outreach',
            'flight_readiness_report',
            'proceeding_paper',
            'proposal',
            'budget',
            'verified_budget',
            'close_out_finance_document',
            'flysheet_1',
            'flysheet_2',
            'flysheet_3',
            'flysheet_4',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'charges_certification',
            'institutional_w9',
            'virtual_cdr',
            'virtual_pdr',
            'virtual_frr',
            'team_photo',
            'team_biography',
            'academics_pdf',
            'stories_pdf',
        )


class FirstNationsRocketCompetitionForm(forms.ModelForm):
    """First Nations Rocket Competition form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )

    class Meta:
        """Attributes about the form and options."""

        model = FirstNationsRocketCompetition
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'interim_report',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'url1',
            'url2',
            'url3',
        )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to set team choices."""
        super(FirstNationsRocketCompetitionForm, self).__init__(*args, **kwargs)
        self.fields['team'].queryset = RocketLaunchTeam.objects.filter(
            competition__contains='First Nations',
        ).filter(date_created__gte=get_start_date()).order_by('name')

    def clean(self):
        """Deal with TRA/NAR fields if need be."""
        cd = self.cleaned_data

        member = cd.get('tra_nar_member')
        number = cd.get('tra_nar_number')
        if member == 'Yes':
            if not number:
                self.add_error(
                    'tra_nar_number',
                    "Please provide your TRA/NAR membership number",
                )


class FirstNationsRocketCompetitionUploadsForm(forms.ModelForm):
    """
    WSGC have removed the requirement for Award Acceptance letter.

    We will keep this form class in place for when they decide to go
    back to requiring it.
    """

    class Meta:
        """Attributes about the form and options."""

        model = FirstNationsRocketCompetition
        fields = (
            'award_acceptance', 'other_file', 'other_file2', 'other_file3',
        )


class MidwestHighPoweredRocketCompetitionForm(forms.ModelForm):
    """Midwest High Powered Rocket Competition form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_participation = forms.TypedChoiceField(
        label="Have you previously participated in Collegiate Rocket Launch?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )

    class Meta:
        """Attributes about the form and options."""

        model = MidwestHighPoweredRocketCompetition
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'interim_report',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'url1',
            'url2',
            'url3',
        )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to set team choices."""
        super(MidwestHighPoweredRocketCompetitionForm, self).__init__(*args, **kwargs)
        self.fields['team'].queryset = RocketLaunchTeam.objects.annotate(
            count=Count('members'),
        ).filter(
            competition__in=['Midwest High Powered Rocket Competition'],
        ).filter(
            date_created__gte=get_start_date(),
        ).exclude(
            count__gte=settings.ROCKET_LAUNCH_COMPETITION_TEAM_LIMIT,
        ).order_by("name")


class MidwestHighPoweredRocketCompetitionUploadsForm(forms.ModelForm):
    """Midwest High Powered Rocket Competition uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = MidwestHighPoweredRocketCompetition
        fields = (
            'award_acceptance', 'other_file', 'other_file2', 'other_file3',
        )


class CollegiateRocketCompetitionForm(forms.ModelForm):
    """Collegiate Rocket Competition form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    other_fellowship = forms.TypedChoiceField(
        label="""
            Do you currently hold another Federal fellowship or traineeship?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )

    class Meta:
        """Attributes about the form and options."""

        model = CollegiateRocketCompetition
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'interim_report',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'url1',
            'url2',
            'url3',
        )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to set team choices."""
        super(CollegiateRocketCompetitionForm, self).__init__(*args, **kwargs)
        self.fields['team'].queryset = RocketLaunchTeam.objects.annotate(
            count=Count('members'),
        ).filter(competition__in=["Collegiate Rocket Competition"]).filter(
            date_created__gte=get_start_date(),
        ).exclude(
            count__gte=settings.ROCKET_LAUNCH_COMPETITION_TEAM_LIMIT,
        ).order_by("name")

    def clean(self):
        """Deal with TRA/NAR fields if need be."""
        cd = self.cleaned_data

        member = cd.get('tra_nar_member')
        number = cd.get('tra_nar_number')
        if member == 'Yes':
            if not number:
                self.add_error(
                    'tra_nar_number',
                    "Please provide your TRA/NAR membership number",
                )


class CollegiateRocketCompetitionUploadsForm(forms.ModelForm):
    """Collegiate Rocket Competition uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = CollegiateRocketCompetition
        fields = (
            'award_acceptance', 'other_file', 'other_file2', 'other_file3',
        )


class NasaCompetitionForm(forms.ModelForm):
    """NASA Competition form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    program_acceptance = forms.TypedChoiceField(
        label="Has your team applied and been accepted into the program?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(NasaCompetitionForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = NasaCompetition
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'funds_authorized',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'intended_program_match',
            'close_out_finance_document',
            'url1',
            'url2',
            'url3',
            'team_photo',
            'team_biography',
        )

    def clean(self):
        """Deal with grants officer and 'other' fields if need be."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None

        if cd.get("competition_type") == "Other":
            if cd.get("competition_type_other") == "":
                self.add_error('competition_type_other', "Required field")

        if cd.get("facility_name") == "Other":
            if cd.get("facility_name_other") == "":
                self.add_error('facility_name_other', "Required field")


class NasaCompetitionUploadsForm(forms.ModelForm):
    """NASA Competition uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = NasaCompetition
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'institutional_w9',
            'photos_overview',
            'publications_overview',
            'budget_modification',
            'performance_modification',
            'scope_modification',
            'no_cost_extension',
            'intended_program_match',
            'close_out_finance_document',
            'other_file',
            'other_file2',
            'other_file3',
            'team_photo',
            'team_biography',
        )


class IndustryInternshipForm(forms.ModelForm):
    """Industry Internship form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    grants_officer = forms.CharField(
        label="Authorized User",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )
    grants_officer2 = forms.CharField(
        label="Authorized User 2",
        required=False,
        help_text="""
            I authorize the individual listed above to submit
            the required documents associated with this proposal on my behalf.
            (NOTE: In order to choose an Authorized User, the individual must be
            registered with WSGC prior to submitting this application.)
        """,
    )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(IndustryInternshipForm, self).__init__(*args, **kwargs)

    class Meta:
        """Attributes about the form and options."""

        model = IndustryInternship
        exclude = (
            'complete',
            'user',
            'status',
            'funded_code',
            'work_plan',
            'authorized_match',
            'award_acceptance',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
            'interim_report',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'intended_program_match',
            'close_out_finance_document',
            'funds_authorized',
            'url1',
            'url2',
            'url3',
        )

    def clean(self):
        """Deal with grants officer."""
        cd = self.cleaned_data
        # authorized users
        uids = [str(self.request.user.id)]
        authuser = {}
        authuser['grants_officer'] = cd.get('grants_officer')
        authuser['grants_officer2'] = cd.get('grants_officer2')
        # Assign a User object to grants officer(s)
        for key, aid in authuser.items():
            sesh_key = '{0}_name'.format(key)
            if aid:
                if aid in uids:
                    self.add_error(
                        key,
                        "User already has a role on this team.",
                    )
                    cd[key] = None
                else:
                    uids.append(aid)
                    try:
                        user = User.objects.get(pk=aid)
                        if user.profile:
                            cd[key] = user
                            self.request.session[sesh_key] = '{0}, {1}'.format(
                                user.last_name, user.first_name,
                            )
                        else:
                            self.add_error(
                                key,
                                "This user does not have a complete profile",
                            )
                            cd[key] = None
                    except Exception:
                        self.add_error(
                            key,
                            "That User does not exist in the system",
                        )
            else:
                cd[key] = None


class IndustryInternshipUploadsForm(forms.ModelForm):
    """Industry Internship uploads form."""

    class Meta:
        """Attributes about the form and options."""

        model = IndustryInternship
        fields = (
            'award_acceptance',
            'final_report',
            'interim_report',
            'other_file',
            'other_file2',
            'other_file3',
            'invoice_q1',
            'invoice_q2',
            'invoice_q3',
            'invoice_q4',
            'intended_program_match',
            'close_out_finance_document',
        )


class ProfessionalProgramStudentForm(forms.ModelForm):
    """Professional Programs for Student form."""

    past_funding = forms.TypedChoiceField(
        label="Have you received WSGC funding within the past five years?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    past_funding_year = forms.CharField(
        label="If 'Yes', what year?",
        widget=forms.Select(choices=PAST_FUNDING_YEAR_CHOICES),
        required=False,
    )
    mentor = forms.CharField(
        label="Mentor",
        required=True,
        help_text="""
            Enter the last name or first name of mentor to see results
            from which to choose.
        """,
    )
    award_acceptance = forms.FileField(
        label="WSGC Award Acceptance",
        help_text="PDF format",
        required=False,
    )
    AerospaceOutreach = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    EarlyStageInvestigator = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    HigherEducationInitiatives = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    IndustryInternship = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    NasaCompetition = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    ResearchInfrastructure = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    SpecialInitiatives = forms.CharField(
        required=False, max_length=64, widget=forms.HiddenInput(),
    )
    signed_certification = forms.BooleanField(
        label="""
        I certify that I am, will be, or have applied to be a
        full-time undergraduate/graduate or professional student
        at one of the Wisconsin Space Grant Consortium colleges or
        universities during the award period covered in this application,
        and the information contained in this application is accurate
        to the best of my knowledge. I understand that, should I receive
        funding, some or all of this scholarship/fellowship may be taxable
        according to IRS regulations and that I am responsible for making
        sure all tax requirements are met.
        """,
        required=True,
    )

    class Meta:
        """Attributes about the form and options."""

        model = ProfessionalProgramStudent
        fields = (
            'program',
            'mentor',
            'past_funding',
            'past_funding_year',
            'anticipating_funding',
            'nasa_award_letter',
            'award_acceptance',
            'signed_certification',
        )

    def __init__(self, *args, **kwargs):
        """Override of the initialization method to obtain the request object."""
        self.request = kwargs.pop('request', None)
        super(ProfessionalProgramStudentForm, self).__init__(*args, **kwargs)

    def clean_mentor(self):
        """Assign a User object to co-advisor."""
        cd = self.cleaned_data
        mid = cd.get('mentor')
        user = None
        if mid:
            try:
                user = User.objects.get(pk=mid)
            except Exception:
                self.add_error(
                    'mentor', "That User does not exist in the system",
                )
            cd['mentor'] = user
        else:
            self.add_error('mentor', "Required field")

        return cd.get('mentor')


class ProfessionalProgramStudentUploadsForm(forms.ModelForm):
    """Professional Program Student uploads form."""

    class Meta:
        """Attributes about the form and options."""

        #model = HigherEducationInitiatives
        model = ProfessionalProgramStudent
        fields = (
            'award_acceptance',
            'nasa_award_letter',
            'interim_report',
            'final_report',
            'other_file',
            'other_file2',
            'other_file3',
        )

# -*- coding: utf-8 -*-
from django import forms
from django.forms.extras.widgets import SelectDateWidget

from djspace.application.models import *
from djtools.fields.widgets import MonthYearWidget
from djtools.fields import BINARY_CHOICES

class HigherEducationInitiativesForm(forms.ModelForm):

    time_frame = forms.DateField(widget=MonthYearWidget)

    class Meta:
        model = HigherEducationInitiatives
        exclude = ('user','status','funds_authorized','authorized_match')


class ResearchInfrastructureForm(forms.ModelForm):

    time_frame = forms.DateField(widget=MonthYearWidget)

    class Meta:
        model = ResearchInfrastructure
        exclude = ('user','status','funds_authorized','authorized_match')


class AerospaceOutreachForm(forms.ModelForm):

    project_category = forms.TypedChoiceField(
        choices = PROJECT_CATEGORIES, widget = forms.RadioSelect()
    )
    time_frame = forms.DateField(
        widget=MonthYearWidget
    )
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices = BINARY_CHOICES, widget = forms.RadioSelect()
    )

    class Meta:
        model = AerospaceOutreach
        fields = [
            'project_title','project_category','location','time_frame',
            'funds_requested','proposed_match','source_match',
            'other_funding','other_funding_explain',
            'synopsis', 'proposal'
        ]
        exclude = ('user','status','funds_authorized','authorized_match')


class SpecialInitiativesForm(forms.ModelForm):

    project_category = forms.TypedChoiceField(
        choices = PROJECT_CATEGORIES, widget = forms.RadioSelect()
    )
    time_frame = forms.DateField(widget=MonthYearWidget)
    other_funding = forms.TypedChoiceField(
        label="Are you seeking other WSGC funding for this project?",
        choices = BINARY_CHOICES, widget = forms.RadioSelect()
    )

    proposed_match = forms.IntegerField(
        label = "Proposed match (1:1 mimimum)(in $)",
        help_text = """
            Match must be 50% for ongoing program;
            25% for new innovated programs (or)
            programs with significant legacy value.
        """
    )
    source_match = forms.CharField(
        label = "Source(s) of match",
        help_text = """
            Overhead (or indirect costs) cannot exceed 0.5
            of the required matching funds
        """
    )

    class Meta:
        model = SpecialInitiatives
        fields = [
            'project_title','project_category','location','time_frame',
            'funds_requested','proposed_match','source_match',
            'other_funding','other_funding_explain', 'synopsis', 'proposal'
        ]
        exclude = ('user','status','funds_authorized','authorized_match')


class UndergraduateScholarshipForm(forms.ModelForm):

    academic_institution = forms.TypedChoiceField(
        label = "Application submitted for",
        widget = forms.RadioSelect(),
        choices=ACADEMIC_INSTITUTIONS
    )
    class Meta:
        model = UndergraduateScholarship
        exclude = ('user','status')


class UndergraduateResearchForm(forms.ModelForm):

    class Meta:
        model = UndergraduateResearch
        exclude = ('user','status','funds_authorized')


class GraduateFellowshipForm(forms.ModelForm):

    class Meta:
        model = GraduateFellowship
        exclude = ('user','status','funds_authorized')


class ClarkGraduateFellowshipForm(forms.ModelForm):

    class Meta:
        model = ClarkGraduateFellowship
        exclude = ('user','status','funds_authorized')

class HighAltitudeBalloonPayloadForm(forms.ModelForm):

    class Meta:
        model = HighAltitudeBalloonPayload
        exclude = ('user','status')

class HighAltitudeBalloonLaunchForm(forms.ModelForm):

    class Meta:
        model = HighAltitudeBalloonLaunch
        exclude = ('user','status')

class FirstNationsLaunchCompetitionForm(forms.ModelForm):

    class Meta:
        model = FirstNationsLaunchCompetition
        exclude = ('user','status')


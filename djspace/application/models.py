# -*- coding: utf-8 -*-

import datetime
import re
from functools import partial

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from djspace.core.models import FILE_VALIDATORS
from djspace.core.models import PHOTO_VALIDATORS
from djspace.core.models import BaseModel
from djspace.core.utils import get_term
from djspace.core.utils import upload_to_path
from djtools.fields import BINARY_CHOICES


TODAY = datetime.date.today()
YEAR_2 = int(TODAY.strftime('%y'))
if TODAY.month >= settings.GRANT_CYCLE_START_MES:
    YEAR_2 = YEAR_2 + 1

PPT_EXTENSIONS = [FileExtensionValidator(allowed_extensions=['ppt', 'pptx', 'pot', 'pps']),]
OPENROCKET_EXTENSIONS = [FileExtensionValidator(allowed_extensions=['rkt'])]
SPREADSHEET_VALIDATORS = [FileExtensionValidator(allowed_extensions=['xls', 'xlsx'])]
if settings.DEBUG:
    PPT_EXTENSIONS = []
    OPENROCKET_EXTENSIONS = []
    FILE_VALIDATORS = []
    PHOTO_VALIDATORS = []
DIRECTORATE_CHOICES = (
    ('Aeronautics Research', 'Aeronautics Research'),
    ('Explorations System Development', 'Explorations System Development'),
    ('Science', 'Science'),
    ('Space Operations', 'Space Operations'),
    ('Space Technology', 'Space Technology'),
    ('Other', 'Other'),
)
GRAVITY_TRAVEL = (
    ('gravity', 'Reduced Gravity'),
    ('travel', 'Student Travel'),
)
TIME_FRAME = (
    ('Summer', 'Summer'),
    ('Summer and fall', 'Summer and fall'),
    ('Fall', 'Fall'),
    ('Spring', 'Spring'),
    ('Summer, fall, and spring', 'Summer, fall, and spring'),
    ('Fall and spring', 'Fall and spring'),
)
PROJECT_CATEGORIES = (
    (
        'Pre-College Program (Formal Education Outreach - K-12)',
        'Pre-College Program (Formal Education Outreach - K-12)',
    ),
    (
        'Informal Education Program (Museums, Planetariums, etc.)',
        'Informal Education Program (Museums, Planetariums, etc.)',
    ),
)
ACADEMIC_INSTITUTIONS = (
    ('Undergraduate Scholarship', 'Undergraduate Scholarship'),
    ('Aviation Scholarship', 'Aviation Scholarship'),
)
INDUSTRY_AWARD_TYPES = (
    (
        'Industry Internship: $5000 award with a required 1:1 match',
        'Industry Internship: $5000 award with a required 1:1 match',
    ),
    (
        'Industry Internship: $5000 award with an optional match',
        'Industry Internship: $5000 award with an optional match',
    ),
    (
        'Internship/Apprenticeship: $0.00 Award with full match',
        'Internship/Apprenticeship:  $0.00 Award with full match',
    ),
    (
        'Technical Apprenticeship: $2500 for two-year schools with a 1:1 match',
        'Technical Apprenticeship: $2500 for two-year schools with a 1:1 match',
    ),
    (
        'Technical Apprenticeship:  $2500 for two-year schools with an optional match.',
        'Technical Apprenticeship:  $2500 for two-year schools with an optional match.',
    ),
)
UNDERGRADUATE_RESEARCH_AWARD_TYPES = (
    (
        'Academic-Year Research: Up to $5000',
        'Academic-Year Research: Up to $5000',
    ),
    (
        'Fall Research: Up to $5000',
        'Fall Research: Up to $5000',
    ),
    (
        'Spring Research: Up to $5000',
        'Spring Research: Up to $5000',
    ),
    (
        'Summer Research: Up to $5000',
        'Summer Research: Up to $5000',
    ),
)
EDUCATION_INITIATIVES_AWARD_TYPES = (
    (
        'Early-Stage Investigator: Up to $10,000',
        'Early-Stage Investigator: Up to $10,000',
    ),
    ('Major Award: $5000-$10000', 'Major Award: $5000-$10000'),
    ('Minor Award:  Up to $5000', 'Minor Award:  Up to $5000'),
)
DISCIPLINES = (
    ('Engineering', 'Engineering'),
    ('Biology', 'Biology'),
    ('Technical (2 year)', 'Technical (2 year)'),
    ('Other', 'Other'),
)
NASA_COMPETITION_TYPES = (
    (
        'App Development Challenge (ADC)',
        'App Development Challenge (ADC)',
    ),
    ('Big Idea', 'Big Idea'),
    (
        'Great Lunar Expedition for Everyone (GLEE)',
        'Great Lunar Expedition for Everyone (GLEE)',
    ),
    (
        'Great Midwest Rocket Launch Competition (MRL)',
        'Great Midwest Rocket Launch Competition (MRL)',
    ),
    (
        'High Altitude Student Platform (HASP)',
        'High Altitude Student Platform (HASP)'
    ),
    (
        'Human Exploration Rover Challenge (HERC)',
        'Human Exploration Rover Challenge (HERC)',
    ),
    (
        'International Rocket Engineering Competition (IREC)',
        'International Rocket Engineering Competition (IREC)'
    ),
    ('Lunabotics', 'Lunabotics'),
    (
        'Micro-g Neutral Buoyancy Experiment Design Teams (Micro-G NExT)',
        'Micro-g Neutral Buoyancy Experiment Design Teams (Micro-G NExT)',
    ),
    (
        'Revolutionary Aerospace Systems Concepts-Academic Linkage (RASC-AL)',
        'Revolutionary Aerospace Systems Concepts-Academic Linkage (RASC-AL)',
    ),
    ('RockStar', 'RockStar'),
    ('Space Apps', 'Space Apps'),
    (
        'Spacesuit User Interface Technologies for Students (SUITS)',
        'Spacesuit User Interface Technologies for Students (SUITS)',
    ),
    ('Student Launch', 'Student Launch'),
    ('XHab', 'XHab'),
    ('Other', 'Other'),
)
NASA_CENTER_CHOICES = (
    ('Ames Research Center', 'Ames Research Center'),
    ('Armstrong Flight Research Center', 'Armstrong Flight Research Center'),
    ('Glenn Research Center', 'Glenn Research Center'),
    ('Goddard Space Flight Center', 'Goddard Space Flight Center'),
    ('Jet Propulsion Laboratory', 'Jet Propulsion Laboratory'),
    ('Johnson Space Center', 'Johnson Space Center'),
    ('Kennedy Space Center', 'Kennedy Space Center'),
    ('Langley Research Center', 'Langley Research Center'),
    ('Marshall Space Flight Center', 'Marshall Space Flight Center'),
    ('Stennis Space Center', 'Stennis Space Center'),
    ('Wallops Flight Facility', 'Wallops Flight Facility'),
    ('Other', 'Other'),
)
ROCKET_COMPETITIONS = (
    ('Collegiate Rocket Competition', 'Collegiate Rocket Competition'),
    ('First Nations Mars Challenge', 'First Nations Mars Challenge'),
    ('First Nations Moon Challenge', 'First Nations Moon Challenge'),
    ('First Nations Gateway Challenge', 'First Nations Gateway Challenge'),
    ('Midwest High Powered Rocket Competition', 'Midwest High Powered Rocket Competition'),
)
ROCKET_LAUNCH_COMPETITION_WITH_LIMIT = [
    'Midwest High Powered Rocket Competition',
    'Collegiate Rocket Competition',
]
EDUCATION_INITITATIVES_PROGRAMS = [
    'aerospaceoutreach',
    'earlystageinvestigator',
    'highereducationinitiatives',
    'industryinternship',
    'nasacompetition',
    'researchinfrastructure',
    'specialinitiatives',
]
PROFESSIONAL_PROGRAMS = [
    'aerospaceoutreach',
    'earlystageinvestigator',
    'highereducationinitiatives',
    'industryinternship',
    'nasacompetition',
    'researchinfrastructure',
    'specialinitiatives',
]
# update excludes in application/views.py for non-programs
STUDENT_PROFESSIONAL_PROGRAMS = (
    ('AerospaceOutreach', 'Aerospace Outreach'),
    ('EarlyStageInvestigator', 'Early-Stage Investigator'),
    ('HigherEducationInitiatives', 'Higher Education Incentives'),
    ('IndustryInternship', 'Industry Internship'),
    ('NasaInternship', 'NASA Internship'),
    ('NasaCompetition', 'National Competitions and Programs'),
    ('ResearchInfrastructure', 'Research Infrastructure'),
    ('SecondStageSpaceSciences', 'Second Stage Space Sciences'),
)
# only used at UI level
ROCKET_COMPETITIONS_EXCLUDE = [
    'midwesthighpoweredrocketcompetition',
    'collegiaterocketcompetition',
    'firstnationsrocketcompetition',
]
TRA_NAR_MEMBER = (('Yes', 'Yes'), ('No', 'No'), ('Not certain', 'Not certain'))
OTHER_PROGRAM_PURPOSE = (
    ('', "----select----"),
    ('Embedded Teacher Program', "Embedded Teacher Program"),
    ('LiftOff', 'LiftOff'),
    ('SEEC', 'SEEC'),
    ('Travel', 'Travel'),
)


class EducationInitiatives(BaseModel):
    """Education Initiatives abstract base model."""

    class Meta:
        """Attributes about the data model and admin options."""

        abstract = True

    # core
    project_title = models.CharField("Title of project", max_length=255)
    funds_requested = models.IntegerField(help_text="In dollars")
    funds_authorized = models.IntegerField(
        null=True,
        blank=True,
        help_text="In Dollars",
    )
    proposed_match = models.IntegerField(
        "Proposed match (1:1 mimimum)(in $)",
    )
    authorized_match = models.IntegerField(
        null=True, blank=True,
    )
    source_match = models.CharField(
        "Source(s) of match", max_length=255,
    )
    begin_date = models.DateField()
    end_date = models.DateField(
        help_text="""
            Note the spend down date requirement in the Announcement of Opportunity.
        """,
    )
    location = models.TextField(
        "Location of project",
        max_length=255,
        help_text="Please list all cities and zipcodes (Format City, State, Zipcode)",
    )
    synopsis = models.TextField(
        help_text="""
            Please include a short synopsis of your project
            (no more than 200 characters) outlining its purpose
            in terms understandable by the general reader.
            If your project is selected for funding, this
            wording will be used on our website.
        """,
    )
    proposal = models.FileField(
        upload_to=partial(upload_to_path, 'Proposal'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    budget = models.FileField(
        upload_to=partial(upload_to_path, 'Budget'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="[PDF format]",
    )
    member_1 = models.CharField(max_length=128, null=True, blank=True)
    member_2 = models.CharField(max_length=128, null=True, blank=True)
    member_3 = models.CharField(max_length=128, null=True, blank=True)
    member_4 = models.CharField(max_length=128, null=True, blank=True)
    member_5 = models.CharField(max_length=128, null=True, blank=True)
    member_6 = models.CharField(max_length=128, null=True, blank=True)
    member_7 = models.CharField(max_length=128, null=True, blank=True)
    member_8 = models.CharField(max_length=128, null=True, blank=True)
    member_9 = models.CharField(max_length=128, null=True, blank=True)
    member_10 = models.CharField(
        "Member 10", max_length=128, null=True, blank=True,
    )
    # finance officer
    finance_officer_name = models.CharField("Name", max_length=128)
    finance_officer_title = models.CharField("Title", max_length=128)
    finance_officer_address = models.TextField("Address")
    finance_officer_email = models.EmailField("Email")
    finance_officer_phone = models.CharField(
        verbose_name="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
    )
    # grant officer
    grant_officer_name = models.CharField("Name", max_length=128)
    grant_officer_title = models.CharField("Title", max_length=128)
    grant_officer_address = models.TextField("Address")
    grant_officer_email = models.EmailField("Email")
    grant_officer_phone = models.CharField(
        verbose_name="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
    )
    invoice_q1 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q1'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q2 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q2'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q3 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q3'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q4 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q4'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    close_out_finance_document = models.FileField(
        upload_to=partial(upload_to_path, 'Closeout_Finance_Document'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    institutional_w9 = models.FileField(
        upload_to=partial(upload_to_path, 'Institutional_W9'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    photos_overview = models.FileField(
        upload_to=partial(upload_to_path, 'Photos_Overview'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="""
            Please provide a brief overview of each photo submitted above,
            include participant names and media releases.
        """,
    )
    publications_overview = models.FileField(
        upload_to=partial(upload_to_path, 'Publications_Overview'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="""
            Please provide an overview with links to all media, articles,
            publications, etc that this project received.
        """,
    )
    budget_modification = models.FileField(
        upload_to=partial(upload_to_path, 'Budget_Modification_Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    performance_modification = models.FileField(
        upload_to=partial(upload_to_path, 'POP Modification Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    scope_modification = models.FileField(
        upload_to=partial(upload_to_path, 'Scope Modification Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    no_cost_extension = models.FileField(
        upload_to=partial(upload_to_path, 'NCE Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['proposal', 'budget']

    def proposal_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('proposal')

    def budget_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget')

    def invoice_q1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q1')

    def invoice_q2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q2')

    def invoice_q3_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q3')

    def invoice_q4_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q4')

    def institutional_w9_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('institutional_w9')

    def photos_overview_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('photos_overview')

    def publications_overview_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('publications_overview')

    def budget_modification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget_modification')

    def performance_modification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('performance_modification')

    def scope_modification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('scope_modification')

    def no_cost_extension_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('no_cost_extension')

    def close_out_finance_document_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('close_out_finance_document')

    def __str__(self):
        """Default data for display."""
        return self.project_title


class HigherEducationInitiatives(EducationInitiatives):
    """Higher Education Incentives."""

    # grants officer user
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='hei_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='hei_grants_officer2',
    )
    award_type = models.CharField(
        "Award",
        max_length=128,
        choices=(
            ('Major Award: $5000 - $10000', 'Major Award: $5000 - $10000'),
            ('Minor Award: Up to $5000', 'Minor Award: Up to $5000'),
        ),
        help_text="""
            Select the opportunity to which the proposal is being submitted.
        """,
    )
    nasa_mission_directorate = models.CharField(
        "NASA Mission Directorate",
        max_length=128,
        choices=DIRECTORATE_CHOICES,
        help_text=mark_safe(
            """
            See NASA's
            <a href="https://www.nasa.gov/directorates/"
              target="_blank"> Mission Directorates</a> page for more information.
            """,
        ),
    )
    nasa_mission_directorate_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the NASA Mission Directorate in which you are
            requesting funds to participate.
        """,
    )

    def __str__(self):
        """Default data for display."""
        return self.project_title

    def get_application_type(self):
        """Application type title for display."""
        return 'Higher Education Incentives'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'higher-education-initiatives'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        award_type = 'MNR'
        if 'Major' in self.award_type:
            award_type = 'MJR'
        return 'HEI{0}_{1}'.format(YEAR_2, award_type)

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Higher Education Incentives"


class ResearchInfrastructure(EducationInitiatives):
    """Research Infrastructure Initiatives."""

    award_type = models.CharField(
        "Award",
        max_length=128,
        choices=EDUCATION_INITIATIVES_AWARD_TYPES,
        help_text="""
            Select the opportunity to which the proposal is being submitted.
        """,
    )
    nasa_mission_directorate = models.CharField(
        "NASA Mission Directorate",
        max_length=128,
        choices=DIRECTORATE_CHOICES,
        help_text=mark_safe(
            """
            See NASA's
            <a href="https://www.nasa.gov/directorates/"
              target="_blank"> Mission Directorates</a> page for more information.
            """,
        ),
    )
    nasa_mission_directorate_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the NASA Mission Directorate in which you are
            requesting funds to participate.
        """,
    )
    # grants officer user
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='rip_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='rip_grants_officer2',
    )

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        award_type = 'MNR'
        if 'Major' in self.award_type:
            award_type = 'MJR'
        return 'RIP{0}_{1}'.format(YEAR_2, award_type)

    def __str__(self):
        """Default data for display."""
        return self.project_title

    def get_application_type(self):
        """Application type title for display."""
        return 'Research Infrastructure'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'research-infrastructure'

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Research Infrastructure"


class EarlyStageInvestigator(EducationInitiatives):
    """Early-Stage Investigator (ESI)."""

    award_type = models.CharField(
        "Award",
        max_length=128,
        choices=EDUCATION_INITIATIVES_AWARD_TYPES,
        help_text="""
            Select the opportunity to which the proposal is being submitted.
        """,
    )
    nasa_mission_directorate = models.CharField(
        "NASA Mission Directorate",
        max_length=128,
        choices=DIRECTORATE_CHOICES,
        help_text=mark_safe(
            """
            See NASA's
            <a href="https://www.nasa.gov/directorates/"
              target="_blank"> Mission Directorates</a> page for more information.
            """,
        ),
    )
    nasa_mission_directorate_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the NASA Mission Directorate in which you are
            requesting funds to participate.
        """,
    )
    # grants officer user
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='esi_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='esi_grants_officer2',
    )

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        award_type = 'MNR'
        if 'Major' in self.award_type:
            award_type = 'MJR'
        return 'ESI{0}_{1}'.format(YEAR_2, award_type)

    def __str__(self):
        """Default data for display."""
        return self.project_title

    def get_application_type(self):
        """Application type title for display."""
        return 'Early-Stage Investigator'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'early-stage-investigator'

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Early-Stage Investigator"


class AerospaceOutreach(EducationInitiatives):
    """Aerospace Outreach education inititative."""

    # grants officer user
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='aop_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='aop_grants_officer2',
    )
    project_category = models.CharField(
        max_length=128,
        choices=PROJECT_CATEGORIES,
    )
    other_fellowship = None
    other_fellowship_explain = None
    other_funding = models.CharField(
        "Are you seeking other WSGC funding for this project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_funding_explain = models.CharField(
        "If yes, please explain.",
        max_length=255,
        null=True,
        blank=True,
    )
    nasa_mission_directorate = models.CharField(
        "NASA Mission Directorate",
        max_length=128,
        choices=DIRECTORATE_CHOICES,
        help_text=mark_safe(
            """
            See NASA's
            <a href="https://www.nasa.gov/directorates/"
              target="_blank"> Mission Directorates</a> page for more information.
            """,
        ),
    )
    nasa_mission_directorate_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the NASA Mission Directorate in which you are
            requesting funds to participate.
        """,
    )

    def __str__(self):
        """Default data for display."""
        return self.project_title

    def get_application_type(self):
        """Application type title for display."""
        return 'Aerospace Outreach'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'aerospace-outreach'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        project_category = 'IE'
        if 'K-12' in self.project_category:
            project_category = 'K12'
        return 'AOP{0}_{1}'.format(YEAR_2, project_category)

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Aerospace Outreach"


class SpecialInitiatives(EducationInitiatives):
    """Special Inititative education initiative."""

    # grants officer user
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='sip_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='sip_grants_officer2',
    )
    project_category = models.CharField(max_length=128, choices=PROJECT_CATEGORIES)
    other_fellowship = None
    other_fellowship_explain = None
    other_funding = models.CharField(
        "Are you seeking other WSGC funding for this project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_funding_explain = models.CharField(
        "If yes, please explain",
        max_length=255,
        null=True,
        blank=True,
    )
    nasa_mission_directorate = models.CharField(
        "NASA Mission Directorate",
        max_length=128,
        choices=DIRECTORATE_CHOICES,
        help_text=mark_safe(
            """
            See NASA's
            <a href="https://www.nasa.gov/directorates/"
              target="_blank"> Mission Directorates</a> page for more information.
            """,
        ),
    )
    nasa_mission_directorate_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the NASA Mission Directorate in which you are
            requesting funds to participate.
        """,
    )

    def __str__(self):
        """Default data for display."""
        return self.project_title

    def get_application_type(self):
        """Application type title for display."""
        return 'Special Initiatives'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'special-initiatives'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        project_category = 'IE'
        if 'K-12' in self.project_category:
            project_category = 'K12'
        return 'SIP{0}_{1}'.format(YEAR_2, project_category)

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Special Initiatives"


class RocketLaunchTeam(BaseModel):
    """Rocket Launch Team for rocket launch competitions."""

    # core
    name = models.CharField(
        "Team name",
        max_length=255,
    )
    co_advisor1 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Co-Advisor 1",
        related_name='rocket_launch_team_co_advisor1',
    )
    co_advisor2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Co-Advisor 2",
        related_name='rocket_launch_team_co_advisor2',
    )
    co_advisor3 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Co-Advisor 3",
        related_name='rocket_launch_team_co_advisor3',
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Team lead",
        related_name='rocket_launch_team_leader',
    )
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='rocket_launch_team_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='rocket_launch_team_grants_officer2',
    )
    members = models.ManyToManyField(User, related_name='rocket_launch_team_members')
    industry_mentor_name = models.CharField(
        "Industry, Tripoli, or National Rocketry Association mentor name",
        max_length=128,
    )
    industry_mentor_email = models.EmailField(
        "Industry, Tripoli, or National Rocketry Association mentor email",
        max_length=128,
    )
    team_roster = models.TextField(
        "Team Roster",
        null=True,
        blank=True,
        help_text="""
            Maximum 6 members, except for First Nations competitions, which
            can have unlimited team members
        """,
    )
    # meta
    competition = models.CharField(max_length=128, choices=ROCKET_COMPETITIONS)
    # files
    proposal = models.FileField(
        upload_to=partial(upload_to_path, 'Proposal'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    budget = models.FileField(
        upload_to=partial(upload_to_path, 'Budget'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="""
            Rocket supplies and travel. Only required for the
            Midwest High Powered Rocket Competition. [PDF format]
        """,
    )
    verified_budget = models.FileField(
        upload_to=partial(upload_to_path, 'Verified_Budget'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q1 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q1'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q2 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q2'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q3 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q3'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q4 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q4'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    close_out_finance_document = models.FileField(
        upload_to=partial(upload_to_path, 'Closeout_Finance_Document'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    charges_certification = models.FileField(
        upload_to=partial(upload_to_path, 'Charges_Certification'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    institutional_w9 = models.FileField(
        upload_to=partial(upload_to_path, 'Institutional_W9'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    interim_progress_report = models.FileField(
        "Critical Design Report",
        upload_to=partial(upload_to_path, 'Critical_Design_Report'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    virtual_cdr = models.FileField(
        "CDR - Virtual Presentation",
        upload_to=partial(upload_to_path, 'CDRV'),
        validators=PPT_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="Power point",
    )
    preliminary_design_report = models.FileField(
        "Preliminary Design Review",
        upload_to=partial(upload_to_path, 'PDR'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    virtual_pdr = models.FileField(
        "PDR - Virtual Presentation",
        upload_to=partial(upload_to_path, 'PDRV'),
        validators=PPT_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="Power point",
    )
    final_design_report = models.FileField(
        upload_to=partial(upload_to_path, 'FDR'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    flight_demo = models.CharField(
        max_length=768,
        null=True,
        blank=True,
        help_text="URL where your video is located",
    )
    final_motor_selection = models.TextField(
        "Motor Selection",
        null=True,
        blank=True,
        help_text="""
            If you do not have a motor selected at this time,
            leave this field blank, and update your application
            when you have a final motor selection.
        """,
    )
    lodging_list = models.FileField(
        upload_to=partial(upload_to_path, 'Lodging_List'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    critical_design_report = models.FileField(
        "Critical Design Review",
        upload_to=partial(upload_to_path, 'CDR'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    oral_presentation = models.FileField(
        upload_to=partial(upload_to_path, 'PPT'),
        validators=PPT_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="Power point",
    )
    post_flight_performance_report = models.FileField(
        "Post Launch Assessment Review",
        upload_to=partial(upload_to_path, 'PLAR'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    education_outreach = models.FileField(
        upload_to=partial(upload_to_path, 'Education_Outreach'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    flight_readiness_report = models.FileField(
        "Flight Readiness Review",
        upload_to=partial(upload_to_path, 'FRR'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    virtual_frr = models.FileField(
        "FRR - Virtual Presentation",
        upload_to=partial(upload_to_path, 'VFRR'),
        validators=PPT_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="Power point",
    )
    flysheet_1 = models.FileField(
        upload_to=partial(upload_to_path, 'Flysheet_1'),
        validators=SPREADSHEET_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="XLSX format",
    )
    flysheet_2 = models.FileField(
        upload_to=partial(upload_to_path, 'Flysheet_2'),
        validators=SPREADSHEET_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="XLSX format",
    )
    flysheet_3 = models.FileField(
        upload_to=partial(upload_to_path, 'Flysheet_3'),
        validators=SPREADSHEET_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="XLSX format",
    )
    flysheet_4 = models.FileField(
        upload_to=partial(upload_to_path, 'Flysheet_4'),
        validators=SPREADSHEET_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="XLSX format",
    )
    openrocketrocksim = models.FileField(
        "RockSim Design Review",
        upload_to=partial(upload_to_path, 'RockSim1'),
        validators=OPENROCKET_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="RKT file",
    )
    openrocketrocksim2 = models.FileField(
        "RockSim Design Review 2",
        upload_to=partial(upload_to_path, 'RockSim2'),
        validators=OPENROCKET_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="RKT file",
    )
    openrocketrocksim3 = models.FileField(
        "RockSim Design Review 3",
        upload_to=partial(upload_to_path, 'RockSim3'),
        validators=OPENROCKET_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="RKT file",
    )
    openrocketrocksim4 = models.FileField(
        "RockSim Design Review 4",
        upload_to=partial(upload_to_path, 'ORRS'),
        validators=OPENROCKET_EXTENSIONS,
        max_length=225,
        null=True,
        blank=True,
        help_text="RKT file",
    )
    team_photo = models.ImageField(
        upload_to=partial(upload_to_path, 'Team_Photo'),
        validators=PHOTO_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
        help_text="JPEG only",
    )
    team_biography = models.FileField(
        upload_to=partial(upload_to_path, 'Team_Biography'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
    )
    academics_url = models.CharField(
        "Academic Posters, Presentations, Papers (URL)",
        max_length=225,
        null=True,
        blank=True,
        help_text="URL for your academic presenations.",
    )
    academics_pdf = models.FileField(
        "Academic Posters, Presentations, Papers (File)",
        upload_to=partial(upload_to_path, 'Academics_Presentations'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
    )
    stories_url = models.CharField(
        "News Articles/Stories (URL)",
        max_length=225,
        null=True,
        blank=True,
        help_text="URL for your academic presenations.",
    )
    stories_pdf = models.FileField(
        "News Articles/Stories (File)",
        upload_to=partial(upload_to_path, 'Team_Stories'),
        validators=FILE_VALIDATORS,
        max_length=225,
        null=True,
        blank=True,
    )
    # misc
    proceeding_paper = models.DateField(null=True, blank=True)
    # team members
    member_1 = models.CharField(max_length=128, null=True, blank=True)
    member_2 = models.CharField(max_length=128, null=True, blank=True)
    member_3 = models.CharField(max_length=128, null=True, blank=True)
    member_4 = models.CharField(max_length=128, null=True, blank=True)
    member_5 = models.CharField(max_length=128, null=True, blank=True)
    member_6 = models.CharField(max_length=128, null=True, blank=True)
    member_7 = models.CharField(max_length=128, null=True, blank=True)
    member_8 = models.CharField(max_length=128, null=True, blank=True)
    member_9 = models.CharField(max_length=128, null=True, blank=True)
    member_10 = models.CharField(max_length=128, null=True, blank=True)
    member_11 = models.CharField(max_length=128, null=True, blank=True)
    member_12 = models.CharField(max_length=128, null=True, blank=True)
    member_13 = models.CharField(max_length=128, null=True, blank=True)
    member_14 = models.CharField(max_length=128, null=True, blank=True)
    member_15 = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['name']
        verbose_name = 'Collegiate Rocket Launch Team (Create NOI))'
        verbose_name_plural = 'Collegiate Rocket Launch Team (Create NOI)'

    def __str__(self):
        """Default data for display."""
        return "{0}".format(self.name)

    def get_application_type(self):
        """Application type title for display."""
        return 'Rocket Launch Team'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'rocket-launch-team'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'RLT{0}'.format(YEAR_2)

    def get_file_path(self):
        """Construct the file path prefix."""
        return 'files/applications'

    def get_team_members(self):
        """Return the team members."""
        team = None
        if self.competition == 'Collegiate Rocket Competition':
            team = self.collegiate_rocket_competition
        elif self.competition == 'Midwest High Powered Rocket Competition':
            team = self.midwest_high_powered_rocket_competition
        elif 'First Nations' in self.competition:
            team = self.first_nations_rocket_competition
        return team

    def get_file_name(self, lackey=False):
        """Construct the file name based on code, team, school, person's name."""
        if self.competition == 'Collegiate Rocket Competition':
            code = 'CRL{0}'.format(YEAR_2)
        elif self.competition == 'Midwest High Powered Rocket Competition':
            code = 'MRL{0}'.format(YEAR_2)
        elif 'First Nations' in self.competition:
            suffix = self.competition.split(' ')[2]
            code = 'FNL{0}_{1}'.format(YEAR_2, suffix)
        last_name = self.user.last_name
        first_name = self.user.first_name
        if lackey:
            user = getattr(self, lackey, None)
            last_name = user.last_name
            first_name = user.first_name
        return '{0}_{1}_{2}'.format(
            code,
            last_name,
            first_name,
        )


    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['budget']

    # timestamp methods are for UI level display
    def proposal_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('proposal')

    def budget_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget')

    def flysheet_1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('flysheet_1')

    def flysheet_2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('flysheet_2')

    def flysheet_3_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('flysheet_3')

    def flysheet_4_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('flysheet_4')

    def verified_budget_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('verified_budget')

    def invoice_q1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q1')

    def invoice_q2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q2')

    def invoice_q3_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q3')

    def invoice_q4_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q4')

    def close_out_finance_document_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('close_out_finance_document')

    def charges_certification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('charges_certification')

    def institutional_w9_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('institutional_w9')

    def interim_progress_report_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('interim_progress_report')

    def virtual_cdr_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('virtual_cdr')

    def preliminary_design_report_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('preliminary_design_report')

    def virtual_pdr_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('virtual_pdr')

    def final_design_report_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('final_design_report')

    def flight_demo_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('flight_demo')

    def final_motor_selection_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('final_motor_selection')

    def lodging_list_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('lodging_list')

    def critical_design_report_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('critical_design_report')

    def oral_presentation_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('oral_presentation')

    def post_flight_performance_report_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('post_flight_performance_report')

    def education_outreach_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('education_outreach')

    def flight_readiness_report_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('flight_readiness_report')

    def virtual_frr_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('virtual_frr')

    def openrocketrocksim_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('openrocketrocksim')

    def openrocketrocksim2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('openrocketrocksim2')

    def openrocketrocksim3_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('openrocketrocksim3')

    def openrocketrocksim4_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('openrocketrocksim4')

    def team_photo_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('team_photo')

    def team_biography_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('team_biography')

    def academics_pdf_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('academics_pdf')

    def stories_pdf_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('stories_pdf')


class MidwestHighPoweredRocketCompetition(BaseModel):
    """Midwest High Powered Rocket Competition."""

    # core
    team = models.ForeignKey(
        RocketLaunchTeam,
        on_delete=models.CASCADE,
        related_name='midwest_high_powered_rocket_competition',
    )
    cv = models.FileField(
        "Résumé",
        upload_to=partial(upload_to_path, 'CV'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    past_participation = models.CharField(
        "Have you previously participated in Collegiate Rocket Launch?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    prior_experience = models.TextField(
        "Prior Rocket Experience",
        help_text="""
            Team experience, leadership experience,
            project experience, hands on experience.
        """,
    )
    other_fellowship = models.CharField(
        "Do you currently hold another federal fellowship or traineeship?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_fellowship_explain = models.CharField(
        """
            If yes, please provide the funding source and the
            funding expiration date.
        """,
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        """Default data for display."""
        return "Midwest High-Powered Rocket Competition"

    def get_application_type(self):
        """Application type title for display."""
        return 'Midwest High-Powered Rocket Competition'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'midwest-high-powered-rocket-competition'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'MRL{0}'.format(YEAR_2)

    def get_file_name(self, lackey=False):
        """Construct the file name based on code, team, school, user."""
        team_name = re.sub(r'[^a-zA-Z0-9]', '-', self.team.name)
        school_name = re.sub(
            r'[^a-zA-Z0-9]',
            '-',
            self.team.user.profile.get_registration().wsgc_affiliate.name,
        )
        return '{0}_{1}_{2}_{3}_{4}'.format(
            self.get_code(),
            team_name,
            school_name,
            self.user.last_name,
            self.user.first_name,
        )

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['cv']

    def cv_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('cv')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class CollegiateRocketCompetition(BaseModel):
    """Collegiate Rocket Competition."""

    # core
    team = models.ForeignKey(
        RocketLaunchTeam,
        on_delete=models.CASCADE,
        related_name='collegiate_rocket_competition',
    )
    tra_nar_member = models.CharField(
        "Are you a current TRA or NAR member?",
        max_length=16,
        choices=TRA_NAR_MEMBER,
    )
    tra_nar_number = models.CharField(
        "What is your TRA or NAR membership number?",
        max_length=32,
        null=True,
        blank=True,
    )
    other_fellowship = models.CharField(
        "Do you currently hold another federal fellowship or traineeship?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_fellowship_explain = models.CharField(
        """
            If yes, please provide the funding source and the
            funding expiration date.
        """,
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        """Default data for display."""
        return "Collegiate Rocket Competition"

    def get_application_type(self):
        """Application type title for display."""
        return 'Collegiate Rocket Competition'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'collegiate-rocket-competition'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'CRL{0}'.format(YEAR_2)

    def get_file_name(self, lackey=False):
        """Construct the file name based on code, team, school, user."""
        team_name = re.sub(r'[^a-zA-Z0-9]', '-', self.team.name)
        school_name = re.sub(
            r'[^a-zA-Z0-9]',
            '-',
            self.team.user.profile.get_registration().wsgc_affiliate.name,
        )
        return '{0}_{1}_{2}_{3}_{4}'.format(
            self.get_code(),
            team_name,
            school_name,
            self.user.last_name,
            self.user.first_name,
        )

    def get_irs_w9(self):
        """Return the user's IRS W9 file object."""
        return self.user.user_files.irs_w9

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['cv']

    def cv_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('cv')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class FirstNationsRocketCompetition(BaseModel):
    """First Nations Rocket Competition."""

    # core
    team = models.ForeignKey(
        RocketLaunchTeam,
        on_delete=models.CASCADE,
        related_name='first_nations_rocket_competition',
    )
    tra_nar_member = models.CharField(
        "Are you a current TRA or NAR member?",
        max_length=16,
        choices=TRA_NAR_MEMBER,
    )
    tra_nar_number = models.CharField(
        "What is your TRA or NAR membership number?",
        max_length=32,
        null=True,
        blank=True,
    )

    def __str__(self):
        """Default data for display."""
        return "First Nations Rocket Competition"

    def get_application_type(self):
        """Application type title for display."""
        return 'First Nations Rocket Competition'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'first-nations-rocket-competition'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        if self.team.competition == 'First Nations Mars Challenge':
            suffix = 'Mars'
        else:
            suffix = 'Moon'
        return 'FNL{0}_{1}'.format(YEAR_2, suffix)

    def get_file_name(self, lackey=False):
        """Construct the file name based on code, user."""
        return '{0}_{1}_{2}'.format(
            self.get_code(),
            self.user.last_name,
            self.user.first_name,
        )

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class HighAltitudeBalloon(BaseModel):
    """High Altitude Balloon Launch."""

    class Meta:
        """Attributes about the data model and admin options."""

        abstract = True

    # core
    letter_interest = models.FileField(
        "Letter of interest",
        upload_to=partial(upload_to_path, 'Letter_Interest'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="""
            Letter must include two faculty members' names, emails,
            and phone numbers, who can be contacted as references.
            [PDF format]
        """,
    )
    commit = models.CharField(
        """
            Will you be able to commit 32-40 hours/week
            to this 10-week summer experience?
        """,
        max_length=4,
        null=True,
        blank=True,
        choices=BINARY_CHOICES,
    )
    other_fellowship = models.CharField(
        "Do you currently hold another federal fellowship or traineeship?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_fellowship_explain = models.CharField(
        """
            If yes, please provide the funding source and the
            funding expiration date.
        """,
        max_length=255,
        null=True,
        blank=True,
    )
    # files
    cv = models.FileField(
        "Résumé",
        upload_to=partial(upload_to_path, 'CV'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    team_photo = models.ImageField(
        upload_to=partial(upload_to_path, 'Team_Photo'),
        validators=PHOTO_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="JPEG only",
    )
    team_biography = models.FileField(
        upload_to=partial(upload_to_path, 'Team_Biography'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    signed_certification = models.BooleanField(
        """
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
        default=False,
    )

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['letter_interest', 'cv']

    def letter_interest_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('letter_interest')

    def cv_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('cv')

    def team_photo_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('team_photo')

    def team_biography_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('team_biography')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class HighAltitudeBalloonLaunch(HighAltitudeBalloon):
    """High Altitude Balloon Launch."""

    def __str__(self):
        """Default data for display."""
        return "High Altitude Balloon Launch"

    def get_application_type(self):
        """Application type title for display."""
        return 'High Altitude Balloon Launch'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'high-altitude-balloon-launch'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'EBL{0}'.format(YEAR_2)

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "High altitude balloon launch"


class UndergraduateAerospaceDesignResearchScholarship(HighAltitudeBalloon):
    """Undergraduate Aerospace Design Research Scholarship."""

    position = models.CharField(
        max_length=16,
        choices=(('Team Lead', 'Team Lead'), ('Team Member', 'Team Member')),
        help_text="""
            Team Lead applicants must have participated in the program
            within the past 2 years.
        """,
    )

    def __str__(self):
        """Default data for display."""
        return "Undergraduate Aerospace Design Research Scholarship"

    def get_application_type(self):
        """Application type title for display."""
        return 'Undergraduate Aerospace Design Research Scholarship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'undergraduate-aerospace-design-research-scholarship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'UAS{0}'.format(YEAR_2)

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Undergraduate Aerospace Design Research Scholarship"


class UnmannedAerialVehiclesResearchScholarship(HighAltitudeBalloon):
    """Unmanned Aerial Vehicles Research Scholarship."""

    def __str__(self):
        """Default data for display."""
        return "Unmanned Aerial Vehicles Research Scholarship"

    def get_application_type(self):
        """Application type title for display."""
        return 'Unmanned Aerial Vehicles Research Scholarship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'unmanned-aerial-vehicles-research-scholarship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'UAV{0}'.format(YEAR_2)

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name = "UAV Scholarship"
        verbose_name_plural = "UAV Scholarships"


class Fellowship(BaseModel):
    """Fellowship Abstract Base Model."""

    class Meta:
        """Attributes about the data model and admin options."""

        abstract = True

    # core
    project_title = models.CharField("Title of project", max_length=255)
    begin_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    funds_requested = models.IntegerField(help_text="In Dollars")
    funds_authorized = models.IntegerField(
        null=True,
        blank=True,
        help_text="In Dollars",
    )
    synopsis = models.TextField(
        help_text="""
            Please include a short synopsis of your project
            (no more than 200 characters) outlining its purpose
            in terms understandable by the general reader.
            If your project is selected for funding, this
            wording will be used on our website.
        """,
    )
    nasa_mission_directorate = models.CharField(
        "NASA Mission Directorate",
        max_length=128,
        choices=DIRECTORATE_CHOICES,
        help_text=mark_safe(
            """
            See NASA's
            <a href="https://www.nasa.gov/directorates/"
              target="_blank"> Mission Directorates</a> page for more information.
            """,
        ),
    )
    nasa_mission_directorate_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the NASA Mission Directorate in which you are
            requesting funds to participate.
        """,
    )
    other_fellowship = models.CharField(
        "Do you currently hold another federal fellowship or traineeship?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_fellowship_explain = models.CharField(
        """
            If yes, please provide the funding source and the
            funding expiration date.
        """,
        max_length=255,
        null=True,
        blank=True,
    )
    proposal = models.FileField(
        upload_to=partial(upload_to_path, 'Proposal'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    cv = models.FileField(
        "Résumé",
        upload_to=partial(upload_to_path, 'CV'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    budget = models.FileField(
        upload_to=partial(upload_to_path, 'Budget'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    undergraduate_transcripts = models.FileField(
        upload_to=partial(upload_to_path, 'Undergraduate_Transcripts'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    graduate_transcripts = models.FileField(
        upload_to=partial(upload_to_path, 'Graduate_Transcripts'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    recommendation_1 = models.FileField(
        "Recommendation letter 1",
        upload_to=partial(upload_to_path, 'Recommendation_1'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text=mark_safe("""
            Recommendation letters are required for the application.
            Advisors may email letters of recommendation directly to
            <a href="mailto:spacegrant@carthage.edu">
                spacegrant@carthage.edu</a>.
            [PDF format]
        """),
    )
    recommendation_2 = models.FileField(
        "Recommendation letter 2",
        upload_to=partial(upload_to_path, 'Recommendation_2'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text=mark_safe("""
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">
                spacegrant@carthage.edu</a>.
            [PDF format]
        """),
    )
    mentor_name = models.CharField("Mentor's Name", max_length=128)
    mentor_email = models.EmailField("Mentor's Email")
    signed_certification = models.BooleanField(
        """
        I certify that I am, will be, or have applied to be a
        full-time graduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        default=False,
    )

    def __str__(self):
        """Default data for display."""
        return '{0}'.format(self.project_title)

    def required_files(self):
        """Used when building a tarball of required files."""
        return [
            'proposal',
            'cv',
            'budget',
            'undergraduate_transcripts',
            'graduate_transcripts',
            'recommendation_1',
            'recommendation_2',
        ]

    def proposal_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('proposal')

    def cv_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('cv')

    def budget_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget')

    def undergraduate_transcripts_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('undergraduate_transcripts')

    def graduate_transcripts_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('graduate_transcripts')

    def recommendation_1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('recommendation_1')

    def recommendation_2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('recommendation_2')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class ClarkGraduateFellowship(Fellowship):
    """Dr. Laurel Salton Clark Memorial Research Fellowship."""

    def get_application_type(self):
        """Application type title for display."""
        return 'Dr. Laurel Salton Clark Memorial Research Fellowship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'clark-graduate-fellowship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'LSC{0}'.format(YEAR_2)


class GraduateFellowship(Fellowship):
    """WSGC Graduate and Professional Research Fellowship."""

    def get_application_type(self):
        """Application type title for display."""
        return 'WSGC Graduate &amp; Professional Research Fellowship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'graduate-fellowship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'RFP{0}'.format(YEAR_2)


class UndergraduateResearch(BaseModel):
    """Undergraduate Research Scholarship."""

    # core
    project_title = models.CharField("Title of project", max_length=255)
    funds_authorized = models.IntegerField(
        null=True,
        blank=True,
        help_text="In Dollars",
    )
    other_funding = models.CharField(
        "Are you seeking other WSGC funding for this project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_funding_explain = models.CharField(
        "If yes, please explain",
        max_length=255,
        null=True,
        blank=True,
    )
    other_fellowship = models.CharField(
        "Do you currently hold another federal fellowship or traineeship?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_fellowship_explain = models.CharField(
        """
            If yes, please provide the funding source and the
            funding expiration date.
        """,
        max_length=255,
        null=True,
        blank=True,
    )
    award_type = models.CharField(
        "Award", max_length=128, choices=UNDERGRADUATE_RESEARCH_AWARD_TYPES,
    )
    begin_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    synopsis = models.TextField(
        help_text="""
            Please include a short synopsis of your project
            (no more than 200 characters) outlining its purpose
            in terms understandable by the general reader.
            If your project is selected for funding, this
            wording will be used on our website. [PDF format]
        """,
    )
    proposal = models.FileField(
        upload_to=partial(upload_to_path, 'Proposal'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    high_school_transcripts = models.FileField(
        upload_to=partial(upload_to_path, 'High_School_Transcripts'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="High School Senior and Freshman students only. [PDF format]",
    )
    undergraduate_transcripts = models.FileField(
        upload_to=partial(upload_to_path, 'Undergraduate_Transcripts'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    wsgc_advisor_recommendation = models.FileField(
        "Faculty Research Advisor Recommendation Letter",
        upload_to=partial(upload_to_path, 'WSGC_Advisor_Recommendation'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text=mark_safe("""
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">spacegrant@carthage.edu</a>.
            [PDF format]
        """),
    )
    recommendation = models.FileField(
        """
            Additional Letter of Recommendation
            (faculty member or other professional reference)
        """,
        upload_to=partial(upload_to_path, 'Recommendation'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text=mark_safe("""
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">
                spacegrant@carthage.edu</a>.
            [PDF format]
        """),
    )
    mentor_name = models.CharField("Mentor's Name", max_length=128)
    mentor_email = models.EmailField("Mentor's Email")
    signed_certification = models.BooleanField(
        """
        I certify that I am, will be, or have applied to be a
        full-time graduate student at one of the Wisconsin Space
        Grant Consortium colleges or universities during the award period
        covered in this application, and the information
        contained in this application is accurate to the best of my
        knowledge. I understand that, should I receive funding,
        some or all of this scholarship/fellowship may be taxable according
        to IRS regulations and that I am responsible for making sure all
        tax requirements are met.
        """,
        default=False,
    )

    def __str__(self):
        """Default data for display."""
        return "{0}".format(self.project_title)

    def get_application_type(self):
        """Application type title for display."""
        return 'Undergraduate Research Scholarship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'undergraduate-research'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'UGR{0}'.format(YEAR_2)

    def form(self):
        """Return the corresponding data model form for this data class model."""
        from djspace.application.forms import UndergraduateResearchForm
        return UndergraduateResearchForm

    def required_files(self):
        """Used when building a tarball of required files."""
        return [
            'proposal',
            'high_school_transcripts',
            'undergraduate_transcripts',
            'wsgc_advisor_recommendation',
            'recommendation',
        ]

    def proposal_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('proposal')

    def high_school_transcripts_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('high_school_transcripts')

    def undergraduate_transcripts_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('undergraduate_transcripts')

    def wsgc_advisor_recommendation_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('wsgc_advisor_recommendation')

    def recommendation_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('recommendation')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name = "Undergraduate Research Scholarship"
        verbose_name_plural = "Undergraduate Research Scholarships"


class Scholarship(BaseModel):
    """Scholar abstract base model."""

    class Meta:
        """Attributes about the data model and admin options."""

        abstract = True

    # core
    statement = models.FileField(
        upload_to=partial(upload_to_path, 'Statement'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text=mark_safe("""
            Maximum two-page statement containing the following:
            <ol class="help_text">
            <li>a clear and concise account of your reasons
            for seeking this scholarship</li>
            <li>evidence of previous interest and experience
            in space, aerospace, or space-related studies</li>
            <li>description of your present interest in the
            space sciences</li>
            <li>a description of the program of space-related
            studies you plan to pursue during the period of this
            award</li></ol> [PDF format]
        """),
    )
    high_school_transcripts = models.FileField(
        upload_to=partial(upload_to_path, 'High_School_Transcripts'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="First and second year students only. [PDF format]",
    )
    undergraduate_transcripts = models.FileField(
        upload_to=partial(upload_to_path, 'Undergraduate_Transcripts'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    wsgc_advisor_recommendation = models.FileField(
        "STEM Faculty/Advisor Recommendation Letter",
        upload_to=partial(upload_to_path, 'WSGC_Advisor_Recommendation'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text=mark_safe("""
            Recommendation letters are not required for this scholarship
            application, but will be accepted as additional application
            documentation. Letters may be uploaded with your application
            or emailed directly to WSGC by an Advisor
            <a href="mailto:spacegrant@carthage.edu">spacegrant@carthage.edu</a>.
            [PDF format]
        """),
    )
    recommendation = models.FileField(
        """
            Additional Letter of Recommendation
            (faculty member or other professional reference)
        """,
        upload_to=partial(upload_to_path, 'Recommendation'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text=mark_safe("""
            Recommendation letters are not required for this scholarship
            application, but will be accepted as additional application
            documentation. Letters may be uploaded with your application
            or emailed directly to WSGC by an Advisor
            <a href="mailto:spacegrant@carthage.edu">spacegrant@carthage.edu</a>.
            [PDF format]
        """
        ),
    )
    academic_institution = models.CharField(
        "Application submitted for",
        max_length=128,
        choices=ACADEMIC_INSTITUTIONS,
    )
    other_funding = models.CharField(
        "Are you seeking other WSGC funding for this project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_funding_explain = models.CharField(
        "If yes, please explain",
        max_length=255,
        null=True,
        blank=True,
    )
    other_fellowship = models.CharField(
        "Do you currently hold another federal fellowship or traineeship?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_fellowship_explain = models.CharField(
        """
            If yes, please provide the funding source and the
            funding expiration date.
        """,
        max_length=255,
        null=True,
        blank=True,
    )
    signed_certification = models.BooleanField(
        """
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
        default=False,
    )

    def get_academic_institution(self):
        """Return the term based on the academic institution name."""
        term = 'FA'
        if 'Spring' in self.academic_institution:
            term = 'SP'
        return term

    def required_files(self):
        """Used when building a tarball of required files."""
        return [
            'statement',
            'high_school_transcripts',
            'undergraduate_transcripts',
            'wsgc_advisor_recommendation',
            'recommendation',
        ]

    def statement_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('statement')

    def high_school_transcripts_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('high_school_transcripts')

    def undergraduate_transcripts_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('undergraduate_transcripts')

    def wsgc_advisor_recommendation_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('wsgc_advisor_recommendation')

    def recommendation_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('recommendation')


class WomenInAviationScholarship(Scholarship):
    """Aviation scholarship."""

    def __str__(self):
        """Default data for display."""
        return "Aviation Scholarship"

    def get_application_type(self):
        """Application type title for display."""
        return 'Aviation Scholarship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'women-in-aviation-scholarship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'WAS{0}'.format(YEAR_2)

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name = "Aviation Scholarship"
        verbose_name_plural = "Aviation Scholarships"


class UndergraduateScholarship(Scholarship):
    """Undergraduate scholarship."""

    def __str__(self):
        """Default data for display."""
        return "Undergraduate Scholarship"

    def get_application_type(self):
        """Application type title for display."""
        return 'Undergraduate Scholarship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'undergraduate-scholarship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'UGS{0}_{1}'.format(
            YEAR_2, self.get_academic_institution(),
        )

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class StemBridgeScholarship(Scholarship):
    """STEM bridge scholarship."""

    def __str__(self):
        """Default data for display."""
        return "STEM Bridge Scholarship"

    def get_application_type(self):
        """Application type title for display."""
        return 'STEM Bridge Scholarship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'stem-bridge-scholarship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'SBS{0}'.format(YEAR_2)

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name = "STEM Bridge Scholarship"
        verbose_name_plural = "STEM Bridge Scholarships"


class NasaCompetition(BaseModel):
    """National Competitions and Programs: education inititative."""

    competition_type = models.CharField(
        """
            Funds requested to participate in the following National Competition or Program
        """,
        max_length=128,
        choices=NASA_COMPETITION_TYPES,
    )
    competition_type_other = models.CharField(
        "Other",
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please identify the National Competitions and Programs in which you are
            requesting funds to participate
        """,
    )
    program_acceptance = models.CharField(
        """
            Has your team applied and been accepted into the NASA program
            listed above?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    funds_requested = models.IntegerField(help_text="In dollars")
    funds_authorized = models.IntegerField(
        null=True,
        blank=True,
        help_text="In Dollars",
    )
    proposed_match = models.IntegerField(
        "Proposed match (optional)", null=True, blank=True,
    )
    authorized_match = models.IntegerField(null=True, blank=True)
    source_match = models.CharField("Source(s) of match", max_length=255, null=True, blank=True)
    begin_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    location = models.TextField(
        "Location of project",
        max_length=255,
        help_text="Please list all cities and zipcodes (Format City, State, Zipcode)",
    )
    # files
    statement = models.FileField(
        upload_to=partial(upload_to_path, 'Statement'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="1 to 2 pages",
    )
    budget = models.FileField(
        upload_to=partial(upload_to_path, 'Budget'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    team_photo = models.ImageField(
        upload_to=partial(upload_to_path, 'Team_Photo'),
        validators=PHOTO_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="JPEG only",
    )
    team_biography = models.FileField(
        upload_to=partial(upload_to_path, 'Team_Biography'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    team_lead = models.CharField("Team Lead", max_length=128)
    # finance officer
    finance_officer_name = models.CharField("Name", max_length=128)
    finance_officer_address = models.TextField("Address")
    finance_officer_email = models.EmailField("Email")
    finance_officer_phone = models.CharField(
        verbose_name="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
    )
    # grant officer
    grant_officer_name = models.CharField("Name", max_length=128)
    grant_officer_address = models.TextField("Address")
    grant_officer_email = models.EmailField("Email")
    grant_officer_phone = models.CharField(
        verbose_name="Phone number",
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
    )
    # grants officer user
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='opp_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='opp_grants_officer2',
    )
    # this is crazy and should be m2m but for now they do not
    # want to require members to be registered with the site
    member_1 = models.CharField(max_length=128, null=True, blank=True)
    member_2 = models.CharField(max_length=128, null=True, blank=True)
    member_3 = models.CharField(max_length=128, null=True, blank=True)
    member_4 = models.CharField(max_length=128, null=True, blank=True)
    member_5 = models.CharField(max_length=128, null=True, blank=True)
    member_6 = models.CharField(max_length=128, null=True, blank=True)
    member_7 = models.CharField(max_length=128, null=True, blank=True)
    member_8 = models.CharField(max_length=128, null=True, blank=True)
    member_9 = models.CharField(max_length=128, null=True, blank=True)
    member_10 = models.CharField(
        "Member 10",
        max_length=128,
        null=True,
        blank=True,
    )
    # approved files
    invoice_q1 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q1'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q2 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q2'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q3 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q3'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q4 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q4'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    institutional_w9 = models.FileField(
        upload_to=partial(upload_to_path, 'Institutional_W9'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    photos_overview = models.FileField(
        upload_to=partial(upload_to_path, 'Photos_Overview'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="""
            Please provide a brief overview of each photo submitted above,
            include participant names and media releases.
        """,
    )
    publications_overview = models.FileField(
        upload_to=partial(upload_to_path, 'Publications_Overview'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="""
            Please provide an overview with links to all media, articles,
            publications, etc that this project received.
        """,
    )
    budget_modification = models.FileField(
        upload_to=partial(upload_to_path, 'Budget_Modification_Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    performance_modification = models.FileField(
        upload_to=partial(upload_to_path, 'POP Modification Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    scope_modification = models.FileField(
        upload_to=partial(upload_to_path, 'Scope Modification Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    no_cost_extension = models.FileField(
        upload_to=partial(upload_to_path, 'NCE Request_Submitted'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
    )
    intended_program_match = models.FileField(
        upload_to=partial(upload_to_path, 'Intended_Program_Match'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    close_out_finance_document = models.FileField(
        upload_to=partial(upload_to_path, 'Closeout_Finance_Document'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "National Competitions and Programs"
        verbose_name = "National Competitions and Programs"

    def __str__(self):
        """Default data for display."""
        return "{0}, {1} [{2}]".format(
            self.user.last_name, self.user.first_name, self.id,
        )

    def get_application_type(self):
        """Application type title for display."""
        return 'National Competitions and Programs'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'nasa-competition'

    def get_code(self):
        """Three letter code for WSGC administrative purposes. OPP = Other Programs."""
        if self.competition_type != 'Other':
            program = re.sub(r'[^a-zA-Z0-9]', '-', self.competition_type)
        elif self.competition_type_other:
            program = re.sub(r'[^a-zA-Z0-9]', '-', self.competition_type_other)
        else:
            program = 'other'
        return 'OPP{0}_{1}_{2}'.format(
            YEAR_2, get_term(self.date_created), program,
        )

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['statement', 'budget']

    def statement_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('statement')

    def budget_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget')

    def invoice_q1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q1')

    def invoice_q2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q2')

    def invoice_q3_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q3')

    def invoice_q4_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q4')

    def intended_program_match_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('intended_program_match')

    def institutional_w9_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('institutional_w9')

    def photos_overview_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('photos_overview')

    def publications_overview_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('publications_overview')

    def budget_modification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget_modification')

    def performance_modification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('performance_modification')

    def scope_modification_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('scope_modification')

    def no_cost_extension_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('no_cost_extension')

    def close_out_finance_document_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('close_out_finance_document')

    def team_photo_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('team_photo')

    def team_biography_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('team_biography')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class IndustryInternship(BaseModel):
    """Industry internship."""

    award_type = models.CharField(
        "Award",
        max_length=128,
        choices=INDUSTRY_AWARD_TYPES,
        help_text="""
            Select the opportunity to which the proposal is being submitted.
            <br><strong>NOTE</strong>:
            The $5000 award with optional match is only available to
            first time applicants.
        """,
    )
    funds_requested = models.IntegerField(help_text="In dollars")
    funds_authorized = models.IntegerField(
        null=True,
        blank=True,
        help_text="In Dollars",
    )
    proposed_match = models.IntegerField("Proposed match (1:1 mimimum)(in $)")
    authorized_match = models.IntegerField(null=True, blank=True)
    source_match = models.CharField("Source(s) of match", max_length=255)
    # Internship opportunity
    discipline = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        choices=DISCIPLINES,
        help_text="""
            Select the discipline within which the
            internship opportunity falls.
        """,
    )
    discipline_other = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="""
            If you have choosen "Other" in the field above,
            please provide the Discipline name here.
        """,
    )
    educational_background = models.TextField(
        # 500 character limit
        null=True,
        blank=True,
        help_text="""
            Provide additional information related to the required educational
            background for the internship opportunity.
        """,
    )
    # Intern Supervisor
    intern_supervisor_name = models.CharField(
        "Name",
        max_length=128,
        null=True,
        blank=True,
    )
    intern_supervisor_job_title = models.CharField(
        "Job title",
        max_length=128,
        null=True,
        blank=True,
    )
    intern_supervisor_cv = models.FileField(
        "Brief Résumé",
        upload_to=partial(upload_to_path, 'Intern_Supervisor_CV'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    # Work description
    objective_technical_approach = models.TextField(
        "Objective and Technical Approach",
        # 2500 character limit
        null=True,
        blank=True,
    )
    background = models.TextField(
        # 2500 character limit
        null=True,
        blank=True,
    )
    background_photo = models.ImageField(
        "Photo",
        upload_to=partial(upload_to_path, 'Background_Photo'),
        validators=PHOTO_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="JPEG only",
    )
    # WorkPlanTask model has a foreign key that references
    # an instance of this model. we can obtain all tasks for
    # an instance with the related name "work_plan_tasks"
    task_schedule = models.FileField(
        upload_to=partial(upload_to_path, 'Task_Schedule'),
        max_length=255,
        null=True,
        blank=True,
        help_text="""
            You must include milestones and the file format must be:
            Excel, Word, or Project.
        """,
    )
    wsgc_goal = models.TextField(
        "WSGC Goal",
        # 500 character limit
        null=True,
        blank=True,
        help_text="""
            How does this internship opportunity address the WSGC goal of
            "Career placements within the aerospace industry in Wisconsin."
        """,
    )
    nasa_mission_relationship = models.TextField(
        "NASA Mission Directorate",
        # 1250 character limit
        null=True,
        blank=True,
        help_text="""
            How does this internship opportunity relate to NASAs mission?
            Can the work be related to a specific NASA center?
        """,
    )
    intern_biography = models.TextField(
        # 1250 character limit
        null=True,
        blank=True,
        help_text="""
            If a candidate student has been identified, provide a brief
            biosketch of the company intern and his or her career goals,
            if available. Though this information is not part of the proposal
            evaluation, it is important to assure that all internships are
            filled with students qualified to be funded through the WSGC.
        """,
    )
    budget = models.FileField(
        upload_to=partial(upload_to_path, 'Budget'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    # grants officer / authorized user field
    grants_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User",
        related_name='iip_grants_officer',
    )
    grants_officer2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Grants Officer / Authorized User 2",
        related_name='iip_grants_officer2',
    )
    # approved files
    invoice_q1 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q1'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q2 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q2'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q3 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q3'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q4 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q4'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    intended_program_match = models.FileField(
        upload_to=partial(upload_to_path, 'Intended_Program_Match'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    close_out_finance_document = models.FileField(
        upload_to=partial(upload_to_path, 'Closeout_Finance_Document'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )

    def __str__(self):
        """Default data for display."""
        return "{0}, {1} [{2}]".format(
            self.user.last_name, self.user.first_name, self.id,
        )

    def get_application_type(self):
        """Application type title for display."""
        return 'Industry Internship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'industry-internship'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'IIP{0}'.format(YEAR_2)

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['intern_supervisor_cv', 'task_schedule', 'budget']

    def intern_supervisor_cv_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('intern_supervisor_cv')

    def task_schedule_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('task_schedule')

    def budget_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('budget')

    def invoice_q1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q1')

    def invoice_q2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q2')

    def invoice_q3_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q3')

    def invoice_q4_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q4')

    def intended_program_match_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('intended_program_match')

    def close_out_finance_document_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('close_out_finance_document')

    def background_photo_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('background_photo')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class ProfessionalProgramStudent(BaseModel):
    """Student Participant in Internship."""

    program = models.CharField(
        "Program Name",
        max_length=128,
        choices=STUDENT_PROFESSIONAL_PROGRAMS,
        help_text="""
            I, as a student, have been selected to participate
            in the above program
        """,
    )
    mentor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='professional_program_student',
    )
    nasa_award_letter = models.FileField(
        "NASA Award Notification Letter",
        upload_to=partial(upload_to_path, 'Nasa_Award_Letter'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="NASA Internship program only. PDF format",
    )
    AerospaceOutreach = models.ForeignKey(
        AerospaceOutreach,
        on_delete=models.SET_NULL,
        related_name='aerospace_outreach_student',
        null=True,
        blank=True,
    )
    HigherEducationInitiatives = models.ForeignKey(
        HigherEducationInitiatives,
        on_delete=models.SET_NULL,
        related_name='higher_education_initiatives_student',
        null=True,
        blank=True,
    )
    IndustryInternship = models.ForeignKey(
        IndustryInternship,
        on_delete=models.SET_NULL,
        related_name='industry_internship_student',
        null=True,
        blank=True,
    )
    NasaCompetition = models.ForeignKey(
        NasaCompetition,
        on_delete=models.SET_NULL,
        related_name='nasa_competition_student',
        null=True,
        blank=True,
    )
    ResearchInfrastructure = models.ForeignKey(
        ResearchInfrastructure,
        on_delete=models.SET_NULL,
        related_name='research_infrastructure_student',
        null=True,
        blank=True,
    )
    EarlyStageInvestigator = models.ForeignKey(
        EarlyStageInvestigator,
        on_delete=models.SET_NULL,
        related_name='early_stage_investigator',
        null=True,
        blank=True,
    )
    SpecialInitiatives = models.ForeignKey(
        SpecialInitiatives,
        on_delete=models.SET_NULL,
        related_name='special_initiatives_student',
        null=True,
        blank=True,
    )
    signed_certification = models.BooleanField(
        """
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
        default=False,
    )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Student Participant in Internship"

    def __str__(self):
        """Default data for display."""
        return "Student Participant in Internship"

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )

    def get_application_type(self):
        """Application type title for display."""
        return 'Student Participant in Internship'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'professional-program-student'

    def program_application(self):
        """Return the program associated with this application."""
        program = None
        if self.AerospaceOutreach:
            program = self.AerospaceOutreach
        elif self.HigherEducationInitiatives:
            program = self.HigherEducationInitiatives
        elif self.IndustryInternship:
            program = self.IndustryInternship
        elif self.NasaCompetition:
            program = self.NasaCompetition
        elif self.ResearchInfrastructure:
            program = self.ResearchInfrastructure
        elif self.EarlyStageInvestigator:
            program = self.EarlyStageInvestigator
        elif self.SpecialInitiatives:
            program = self.SpecialInitiatives
        return program

    def program_application_link(self):
        """Construct a link to the program associated with this application."""
        app = self.program_application()
        link = None
        if app:
            # two programs do not have a title so we use app name instead
            try:
                title = app.project_title
            except Exception:
                title = self.program
            url = reverse(
                'application_print',
                kwargs={'application_type': app.get_slug(), 'aid': app.id},
            )
            link = mark_safe('<a href="{0}">{1}</a>'.format(url, title))
        return link

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'PPS{0}_{1}'.format(YEAR_2, self.program)

    def irs_w9(self):
        """Return the user's IRS W9 file object."""
        return self.user.user_files.irs_w9

    def biography(self):
        """Return the user's biography file object."""
        return self.user.user_files.biography

    def mugshot(self):
        """Return the user's mugshot file object."""
        return self.user.user_files.mugshot

    def required_files(self):
        """Used when building a tarball of required files."""
        return []

    def nasa_award_letter_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('nasa_award_letter')


class OtherProgram(BaseModel):
    """Other Program Proposal: Generic program for various funding targets."""

    purpose = models.CharField(
        "Purpose/Destination of funding",
        max_length=128,
        choices=OTHER_PROGRAM_PURPOSE,
        help_text="",
    )
    proposal = models.FileField(
        upload_to=partial(upload_to_path, 'Proposal'),
        validators=FILE_VALIDATORS,
        max_length=255,
        help_text="PDF format",
    )
    invoice_q1 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q1'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    invoice_q2 = models.FileField(
        upload_to=partial(upload_to_path, 'Invoice_Q2'),
        validators=FILE_VALIDATORS,
        max_length=255,
        null=True,
        blank=True,
        help_text="PDF format",
    )

    class Meta:
        """Attributes about the data model and admin options."""

        verbose_name_plural = "Other Programs"
        verbose_name = "Other Program"

    def __str__(self):
        """Default data for display."""
        return "{0}, {1} [{2}]".format(
            self.user.last_name, self.user.first_name, self.id,
        )

    def get_application_type(self):
        """Application type title for display."""
        return 'Other Program'

    def get_slug(self):
        """Slug for the application, used for many things."""
        return 'other-program'

    def get_code(self):
        """Three letter code for WSGC administrative purposes."""
        return 'OPP{0}_{1}'.format(YEAR_2, self.purpose)

    def required_files(self):
        """Used when building a tarball of required files."""
        return ['proposal',]

    def proposal_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('proposal')

    def invoice_q1_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q1')

    def invoice_q2_timestamp(self):
        """Timestamp method for UI level display."""
        return self.get_file_timestamp('invoice_q2')

    def get_absolute_url(self):
        """Returns the absolute URL from root URL."""
        return reverse(
            'application_update',
            kwargs={'application_type': self.get_slug(), 'aid': str(self.id)},
        )


class WorkPlanTask(models.Model):
    """Work plan task data model for the Industry Internship program."""

    industry_internship = models.ForeignKey(
        IndustryInternship,
        on_delete=models.CASCADE,
        #related_name='work_plan_tasks',
    )
    title = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    description = models.TextField(null=True, blank=True)
    hours_percent = models.CharField(max_length=32, null=True, blank=True)
    expected_outcome = models.TextField(null=True, blank=True)

    def __str__(self):
        """Default data for display."""
        return "{0}".format(self.title)

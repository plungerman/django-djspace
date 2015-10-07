# -*- coding: utf-8 -*-
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models.signals import pre_delete

from djspace.core.models import BaseModel
from djspace.registration.choices import WSGC_SCHOOL

from djtools.fields import BINARY_CHOICES, SALUTATION_TITLES, STATE_CHOICES
from djtools.fields import GENDER_CHOICES
from djtools.fields.validators import MimetypeValidator

from taggit.managers import TaggableManager
from uuid import uuid4

WSGC_SCHOOL_OTHER = WSGC_SCHOOL + (('Other','Other'),)

import os

GRAVITY_TRAVEL = (
    ('gravity','Reduced Gravity'),
    ('travel','Student Travel')
)
FIRST_NATIONS_ROCKET_COMPETITIONS = (
    ('Tribal','Tribal'),
    ('AISES','AISES'),
)
TIME_FRAME = (
    ('Summer','Summer'),
    ('Summer and fall','Summer and fall'),
    ('Fall','Fall'),
    ('Spring','Spring'),
    ('Summer, fall, and spring','Summer, fall, and spring'),
    ('Fall and spring','Fall and spring')
)
PROJECT_CATEGORIES = (
    (
        'Pre-College Program (Formal Education Outreach - K-12)',
        'Pre-College Program (Formal Education Outreach - K-12)'
    ),
    (
        'Informal Education Program (Museums, Planetariums, etc.)',
        'Informal Education Program (Museums, Planetariums, etc.)'
    )
)
ACADEMIC_INSTITUTIONS = (
    (
        'Two-year Academic Institution Opportunity (Fall)',
        'Two-year Academic Institution Opportunity (Fall)'
    ),
    (
        'All Academic Institution Opportunity (Spring)',
        'All Academic Institution Opportunity (Spring)'
    )
)
INDUSTRY_AWARD_TYPES = (
    (
        'Industry Internship: $5000 award with a required 1:1 match',
        'Industry Internship: $5000 award with a required 1:1 match'
    ),
    (
        'Industry Internship: $5000 award with an optional match',
        'Industry Internship: $5000 award with an optional match'
    ),
    (
        'Technical Apprenticeship: $2500 for two-year schools with a 1:1 match',
        'Technical Apprenticeship: $2500 for two-year schools with a 1:1 match'
    ),
)
DISCIPLINES = (
    ('Engineering','Engineering'),
    ('Biology','Biology'),
    ('Technical (2 year)','Technical (2 year)'),
    ('Other','Other')
)
# Correspond to Tags
ROCKET_COMPETITIONS = [
    "Collegiate Rocket Competition",
    "First Nations Rocket Competition",
    "Midwest High Powered Rocket Competition"
]


def upload_to_path(self, filename):
    """
    Generates the path as a string for file field.
    """
    ext = filename.split('.')[-1]
    # set filename as random string
    filename = '{}.{}'.format(uuid4().hex, ext)
    ts = self.date_created.strftime("%Y%m%d%H%M%S%f")
    path = "files/applications/{}/{}/{}/".format(
        self.get_slug(), self.user.id, ts
    )
    return os.path.join(path, filename)


class EducationInitiatives(BaseModel):

    # core
    project_title = models.CharField(
        "Title of project", max_length=255
    )
    funds_requested = models.IntegerField(help_text="In dollars")
    funds_authorized = models.IntegerField(
        null = True, blank = True,
        help_text="In Dollars"
    )
    proposed_match = models.IntegerField(
        "Proposed match (1:1 mimimum)(in $)",
    )
    authorized_match = models.IntegerField(
        null = True, blank = True
    )
    source_match = models.CharField(
        "Source(s) of match", max_length=255
    )
    time_frame = models.DateField(
        "Time frame that best suits your project",
    )
    location = models.CharField(
        "Location of project", max_length=255
    )
    synopsis = models.TextField(
        help_text = '''
            Please include a short synopsis of your project
            (no more than 200 characters) outlining its purpose
            in terms understandable by the general reader.
            If your project is selected for funding, this
            wording will be used on our website.
        '''
    )
    proposal = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )

    class Meta:
        abstract = True


class HigherEducationInitiatives(EducationInitiatives):

    def __unicode__(self):
        return "Higher Education Initiatives"

    def get_application_type(self):
        return "Higher Education Initiatives"

    def get_slug(self):
        return "higher-education-initiatives"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])

    class Meta:
        verbose_name_plural = "Higher Education Initiatives"


class ResearchInfrastructure(EducationInitiatives):

    def __unicode__(self):
        return "Research Infrastructure"

    def get_application_type(self):
        return "Research Infrastructure"

    def get_slug(self):
        return "research-infrastructure"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])

    class Meta:
        verbose_name_plural = "Research Infrastructure"


class AerospaceOutreach(EducationInitiatives):

    project_category = models.CharField(
        max_length=128,
        choices=PROJECT_CATEGORIES
    )
    other_funding = models.CharField(
        "Are you seeking other WSGC funding for this project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_funding_explain = models.CharField(
        "If yes, please explain",
        max_length=255,
        null = True, blank = True
    )
    finance_officer_name = models.CharField(
        "Name",
        max_length=128
    )
    finance_officer_address = models.TextField("Address")
    finance_officer_email = models.EmailField("Email")
    finance_officer_phone = models.CharField(
        verbose_name='Phone number',
        max_length=12,
        help_text="Format: XXX-XXX-XXXX"
    )

    def __unicode__(self):
        return "Aerospace Outreach"

    def get_application_type(self):
        return "Aerospace Outreach"

    def get_slug(self):
        return "aerospace-outreach"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])

    class Meta:
        verbose_name_plural = "Aerospace Outreach"


class SpecialInitiatives(EducationInitiatives):

    project_category = models.CharField(
        max_length=128,
        choices=PROJECT_CATEGORIES
    )
    other_funding = models.CharField(
        "Are you seeking other WSGC funding for this project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_funding_explain = models.CharField(
        "If yes, please explain",
        max_length=255,
        null = True, blank = True
    )
    finance_officer_name = models.CharField(
        "Name",
        max_length=128
    )
    finance_officer_address = models.TextField("Address")
    finance_officer_email = models.EmailField("Email")
    finance_officer_phone = models.CharField(
        verbose_name='Phone number',
        max_length=12,
        help_text="Format: XXX-XXX-XXXX"
    )

    def __unicode__(self):
        return "Special Initiatives"

    def get_application_type(self):
        return "Special Initiatives"

    def get_slug(self):
        return "special-initiatives"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])

    class Meta:
        verbose_name_plural = "Special Initiatives"


class RocketLaunchTeam(BaseModel):

    # core
    name = models.CharField(
        "Team name",
        max_length=255
    )
    academic_institution_name = models.CharField(
        "Academic institution",
        choices=WSGC_SCHOOL_OTHER,
        max_length=128,
    )
    academic_institution_other = models.CharField(
        "Other",
        max_length=128,
        null = True, blank = True,
        help_text="""
            If your academic institution does not appear in the list above,
            please provide it here.
        """
    )
    leader = models.ForeignKey(
        User,
        related_name="rocket_launch_team_leader",
        null = True, blank = True
    )
    members = models.ManyToManyField(
        User, related_name="rocket_launch_team_members",
        null = True, blank = True
    )
    industry_mentor_name = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    industry_mentor_email = models.EmailField(
        max_length=75,
        null = True, blank = True
    )
    intent_compete = models.TextField(
        "Notification of Intent to Compete"
    )
    wsgc_acknowledgement = models.FileField(
        "WSGC institutional representative acknowledgement",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text="""
            [PDF format]<br>
            NOTE: Only required for the Collegiate Rocket Competition<br>
            and the Midwest High-Powered Rocket Competition.
        """
    )
    budget = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text="""
            Rocket supplies and travel. [PDF format]<br>
            NOTE: Only required for the
            Midwest High-Powered Rocket Competition.
        """
    )
    member_1 = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    member_2 = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    member_3 = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    member_4 = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    member_5 = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    member_6 = models.CharField(
        max_length=128,
        null = True, blank = True
    )
    # meta
    tags = TaggableManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'Rocket Launch Team (NOI)'
        verbose_name_plural = 'Rocket Launch Team (NOI)'

    def __unicode__(self):
        return u"{}".format(self.name)

    def get_application_type(self):
        return "Rocket Launch Team"

    def get_slug(self):
        return "rocket-launch-team"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class MidwestHighPoweredRocketCompetition(BaseModel):

    # core
    team = models.ForeignKey(RocketLaunchTeam)
    cv = models.FileField(
        "Résumé",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    prior_experience = models.TextField(
        "Prior Rocket Experience"
    )

    def __unicode__(self):
        return "Midwest High-Powered Rocket Competition"

    def get_application_type(self):
        return "Midwest High-Powered Rocket Competition"

    def get_slug(self):
        return "midwest-high-powered-rocket-competition"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class CollegiateRocketCompetition(BaseModel):

    # core
    team = models.ForeignKey(RocketLaunchTeam)
    cv = models.FileField(
        "Résumé",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )

    def __unicode__(self):
        return "Collegiate Rocket Competition"

    def get_application_type(self):
        return "Collegiate Rocket Competition"

    def get_slug(self):
        return "collegiate-rocket-competition"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class FirstNationsRocketCompetition(BaseModel):

    # core
    team = models.ForeignKey(RocketLaunchTeam)
    competition = models.CharField(
        "Rocket Competition",
        max_length=128,
        choices=FIRST_NATIONS_ROCKET_COMPETITIONS
    )
    cv = models.FileField(
        "Résumé",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )

    def __unicode__(self):
        return "First Nations Rocket Competition"

    def get_application_type(self):
        return "First Nations Rocket Competition"

    def get_slug(self):
        return "first-nations-rocket-competition"

    def team_name(self):
        return self.team.name

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class HighAltitudeBalloon(BaseModel):

    class Meta:
        abstract = True

    # core
    letter_interest = models.FileField(
        "Letter of interest",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="""
            Letter must include two faculty members' names, emails,
            and phone numbers, who can be contacted as references.
            [PDF format]
        """
    )
    cv = models.FileField(
        "Résumé",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class HighAltitudeBalloonLaunch(HighAltitudeBalloon):

    def __unicode__(self):
        return "High Altitude Balloon Launch"

    def get_application_type(self):
        return "High Altitude Balloon Launch"

    def get_slug(self):
        return "high-altitude-balloon-launch"

    class Meta:
        verbose_name_plural = "High altitude balloon launch"

class HighAltitudeBalloonPayload(HighAltitudeBalloon):

    def __unicode__(self):
        return "High Altitude Balloon Payload"

    def get_application_type(self):
        return "High Altitude Balloon Payload"

    def get_slug(self):
        return "high-altitude-balloon-payload"

    class Meta:
        verbose_name_plural = "High altitude balloon payload"


class Fellowship(BaseModel):

    class Meta:
        abstract = True

    # core
    signed_certification = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text=mark_safe('''
            Before beginning the application process,
            please print, obtain signatures, and scan the<br>
            <a href="/live/files/1808-pdf" target="_blank">
            signed certification document
            </a>.
        ''')
    )
    anticipating_funding = models.CharField(
        "Are you anticipating other funding this year?",
        max_length=4,
        choices=BINARY_CHOICES,
        help_text="Grants/Scholarships/etc."
    )
    project_title = models.CharField(
        "Title of project", max_length=255
    )
    time_frame = models.CharField(
        "Time frame that best suits your project",
        max_length=128,
        choices=TIME_FRAME
    )
    funds_requested = models.IntegerField(help_text="In Dollars")
    funds_authorized = models.IntegerField(
        null = True, blank = True,
        help_text="In Dollars"
    )
    synopsis = models.TextField(
        help_text = '''
            Please include a short synopsis of your project
            (no more than 200 characters) outlining its purpose
            in terms understandable by the general reader.
            If your project is selected for funding, this
            wording will be used on our website.
        '''
    )
    proposal = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    cv = models.FileField(
        "Résumé",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    budget = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    undergraduate_transcripts = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    graduate_transcripts = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    recommendation_1 = models.FileField(
        "Recommendation letter 1",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null=True,blank=True,
        help_text=mark_safe('''
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">
                spacegrant@carthage.edu</a>.
            [PDF format]
        ''')
    )
    recommendation_2 = models.FileField(
        "Recommendation letter 2",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text=mark_safe('''
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">
                spacegrant@carthage.edu</a>.
            [PDF format]
        ''')
    )

    def __unicode__(self):
        return u"{}".format(self.project_title)

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class ClarkGraduateFellowship(Fellowship):

    def get_application_type(self):
        return "Dr. Laurel Salton Clark Memorial Research Fellowship"

    def get_slug(self):
        return "clark-graduate-fellowship"


class GraduateFellowship(Fellowship):

    def get_application_type(self):
        return "WSGC Graduate &amp; Professional Research Fellowship"

    def get_slug(self):
        return "graduate-fellowship"


class UndergraduateResearch(BaseModel):

    # core
    signed_certification = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text=mark_safe('''
            Before beginning the application process,
            please print, obtain signatures, and scan the<br>
            <a href="/live/files/1827-pdf" target="_blank">
            signed certification document
            </a>
        ''')
    )
    project_title = models.CharField(
        "Title of project", max_length=255
    )
    academic_institution = models.CharField(
        "Application submitted for", max_length=128,
        choices=ACADEMIC_INSTITUTIONS
    )
    funds_requested = models.IntegerField(help_text="In Dollars")
    funds_authorized = models.IntegerField(
        null = True, blank = True,
        help_text="In Dollars"
    )
    time_frame = models.CharField(
        "Time frame that best suits your project",
        max_length=128,
        choices=TIME_FRAME
    )
    synopsis = models.TextField(
        help_text = '''
            Please include a short synopsis of your project
            (no more than 200 characters) outlining its purpose
            in terms understandable by the general reader.
            If your project is selected for funding, this
            wording will be used on our website. [PDF format]
        '''
    )
    proposal = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    high_school_transcripts = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text="First and second year students only. [PDF format]"
    )
    undergraduate_transcripts = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    wsgc_advisor_recommendation = models.FileField(
        "Faculty Research Advisor Recommendation Letter",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text=mark_safe('''
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">spacegrant@carthage.edu</a>.
            [PDF format]
        ''')
    )
    recommendation = models.FileField(
        """
            Additional Letter of Recommendation
            (faculty member or other professional reference)
        """,
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text=mark_safe('''
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">
                spacegrant@carthage.edu</a>.
            [PDF format]
        ''')
    )

    def __unicode__(self):
        return u"{}".format(self.project_title)

    def get_application_type(self):
        return "Undergraduate Research Fellowship"

    def get_slug(self):
        return "undergraduate-research"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])

    class Meta:
        verbose_name_plural = "Undergraduate Research"


class UndergraduateScholarship(BaseModel):

    # core
    signed_certification = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text=mark_safe('''
            Before beginning the application process,
            please print, obtain signatures, and scan the<br>
            <a href="/live/files/1827-pdf" target="_blank">
            signed certification document
            </a>
        ''')
    )
    statement = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text=mark_safe('''Maximum two-page statement containing the following:
            <ol style="font-weight:bold;color:#000;list-style-type:upper-alpha;margin-left:25px;">
            <li>a clear and concise account of your reasons
            for seeking this scholarship</li>
            <li>evidence of previous interest and experience
            in space, aerospace, or space-related studies</li>
            <li>description of your present interest in the
            space sciences</li>
            <li>a description of the program of space-related
            studies you plan to pursue during the period of this
             award.</li></ol> [PDF format]
        ''')
    )
    high_school_transcripts = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text="First and second year students only. [PDF format]"
    )
    undergraduate_transcripts = models.FileField(
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    wsgc_advisor_recommendation = models.FileField(
        "Faculty Research Advisor Recommendation Letter",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text=mark_safe('''
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">spacegrant@carthage.edu</a>.
            [PDF format]
        ''')
    )
    recommendation = models.FileField(
        """
            Additional Letter of Recommendation
            (faculty member or other professional reference)
        """,
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        null = True, blank = True,
        help_text=mark_safe('''
            Recommendation letter is required for the application but may be
            emailed by Advisor directly to WSGC at
            <a href="mailto:spacegrant@carthage.edu">spacegrant@carthage.edu</a>.
            [PDF format]
        ''')
    )

    def __unicode__(self):
        return "Undergraduate Scholarship"

    def get_application_type(self):
        return "Undergraduate Scholarship"

    def get_slug(self):
        return "undergraduate-scholarship"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


class WorkPlanTask(models.Model):
    title = models.CharField(
        max_length = 128,
        default = "Task title",
        null = True, blank = True
    )
    description = models.TextField(
        null = True, blank = True
    )
    hours_percent = models.CharField(
        max_length = 32,
        null = True, blank = True
    )
    expected_outcome = models.TextField(
        null = True, blank = True
    )

    def __unicode__(self):
        return u"{}".format(self.title)

class IndustryInternship(BaseModel):

    award_type = models.CharField(
        "Award",
        max_length = 128,
        choices = INDUSTRY_AWARD_TYPES,
        null = True, blank = True,
        help_text = """
            Select the opportunity to which the proposal is being submitted.
            <br><strong>NOTE</strong>:
            The $5000 award with optional match is only available to
            first time applicants.
        """
    )
    # Internship opportunity
    discipline = models.CharField(
        max_length = 128,
        choices = DISCIPLINES,
        null = True, blank = True,
        help_text = """
            Select the discipline within which the opportunity falls.
        """
    )
    discipline_other = models.CharField(
        max_length = 128,
        null = True, blank = True,
        help_text = '''
            If you have choosen "Other" in the field above,
            please provide the Discipline name here.
        '''
    )
    educational_background = models.TextField(
        # 500 character limit
        null = True, blank = True,
        help_text = """
            Provide additional information and its relevancy
            in terms of its relationship to the internship opportunity.
        """
    )
    # Intern Supervisor
    intern_supervisor_name = models.CharField(
        "Name",
        max_length = 128,
        null = True, blank = True
    )
    intern_supervisor_job_title = models.CharField(
        "Job title",
        max_length = 128,
        null = True, blank = True
    )
    intern_supervisor_cv = models.FileField(
        "Résumé",
        upload_to = upload_to_path,
        validators = [MimetypeValidator('application/pdf')],
        max_length = 768,
        null = True, blank = True,
        help_text = "PDF format"
    )
    # Work description
    objective_technical_approach = models.TextField(
        # 2500 character limit
        null = True, blank = True
    )
    background = models.TextField(
        # 2500 character limit
        null = True, blank = True
    )
    background_photo = models.ImageField(
        "Photo",
        upload_to = upload_to_path,
        validators = [MimetypeValidator('image/jpeg')],
        max_length = 768,
        null = True, blank = True,
        help_text = "JPEG only"
    )
    # Work Plan (add another, up to 10)
    work_plan = models.ManyToManyField(
        WorkPlanTask,
        related_name = "industry_internship_work_plan",
        null = True, blank = True
    )
    task_schedule = models.FileField(
        upload_to = upload_to_path,
        max_length = 768,
        null = True, blank = True,
        help_text = """
            You must include milestones and the file format must be:
            Excel, Word, or Project.
        """
    )
    wsgc_goal = models.TextField(
        # 500 character limit
        null = True, blank = True,
        help_text = '''
            How does this internship opportunity address the WSGC goal of
            "Career placements within the aerospace industry in Wisconsin".
        '''
    )
    nasa_mission_relationship = models.TextField(
        # 1250 character limit
        null = True, blank = True,
        help_text = '''
            How does this internship opportunity relate to NASAs mission?
            Can the work be related to a specific NASA center?
        '''
    )
    intern_biography = models.TextField(
        # 1250 character limit
        null = True, blank = True,
        help_text = '''
            If a candidate student has been identified, provide a brief
            biosketch of the company intern and his or her career goals,
            if available. Though this information is not part of the proposal
            evaluation, it is important to assure that all internships are
            filled with students qualified to be funded through the WSGC.
        '''
    )
    budget = models.FileField(
        upload_to = upload_to_path,
        validators = [MimetypeValidator('application/pdf')],
        max_length = 768,
        null = True, blank = True,
        help_text = "PDF format"
    )

    def __unicode__(self):
        return u"{}, {}".format(self.user.last_name, self.user.first_name)

    def get_application_type(self):
        return "Industry Internship"

    def get_slug(self):
        return "industry-internship"

    @models.permalink
    def get_absolute_url(self):
        return ('application_update', [self.get_slug(), str(self.id)])


'''
"""
Signals
"""

def remove_member(sender, instance, *args, **kwargs):
    instance.team.members.remove(instance.user)

pre_delete.connect(remove_member, sender=MidwestHighPoweredRocketCompetition)
pre_delete.connect(remove_member, sender=CollegiateRocketCompetition)
pre_delete.connect(remove_member, sender=FirstNationsRocketCompetition)
'''

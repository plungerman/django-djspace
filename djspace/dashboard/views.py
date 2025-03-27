# -*- coding: utf-8 -*-

import json

import django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from djspace.application.forms import *
from djspace.application.models import ROCKET_COMPETITIONS_EXCLUDE
from djspace.core.forms import UserFilesForm
from djspace.core.models import UserFiles
from djspace.core.utils import PROFESSIONAL_PROGRAMS
from djspace.core.utils import get_start_date
from djspace.core.utils import profile_status
from djspace.dashboard.forms import UserForm
from djspace.dashboard.forms import UserProfileForm
from djspace.registration.forms import FacultyForm
from djspace.registration.forms import GraduateForm
from djspace.registration.forms import GrantsOfficerForm
from djspace.registration.forms import HighSchoolForm
from djspace.registration.forms import ProfessionalForm
from djspace.registration.forms import TechnicalAdvisorForm
from djspace.registration.forms import UndergraduateForm
from djtools.utils.convert import str_to_class


UPLOAD_FORMS = {
    'highereducationinitiatives': HigherEducationInitiativesUploadsForm,
    'earlystageinvestigator': EarlyStageInvestigatorUploadsForm,
    'researchinfrastructure': ResearchInfrastructureUploadsForm,
    'aerospaceoutreach': AerospaceOutreachUploadsForm,
    'specialinitiatives': SpecialInitiativesUploadsForm,
    'undergraduatescholarship': UndergraduateScholarshipUploadsForm,
    'stembridgescholarship': StemBridgeScholarshipUploadsForm,
    'womeninaviationscholarship': WomenInAviationScholarshipUploadsForm,
    'undergraduateresearch': UndergraduateResearchUploadsForm,
    'graduatefellowship': GraduateFellowshipUploadsForm,
    'clarkgraduatefellowship': ClarkGraduateFellowshipUploadsForm,
    'undergraduateaerospacedesignresearchscholarship': UndergraduateAerospaceDesignResearchScholarshipUploadsForm,
    'rocketlaunchteam': RocketLaunchTeamUploadsForm,
    'firstnationsrocketcompetition': FirstNationsRocketCompetitionUploadsForm,
    'midwesthighpoweredrocketcompetition': MidwestHighPoweredRocketCompetitionUploadsForm,
    'collegiaterocketcompetition': CollegiateRocketCompetitionUploadsForm,
    'nasacompetition': NasaCompetitionUploadsForm,
    'otherprogram': OtherProgramUploadsForm,
    'industryinternship': IndustryInternshipUploadsForm,
    'professionalprogramstudent': ProfessionalProgramStudentUploadsForm,
    'unmannedaerialvehiclesresearchscholarship': UnmannedAerialVehiclesResearchScholarshipUploadsForm,
}


@login_required
def home(request):
    """User dashboard home."""
    user = request.user
    try:
        files = UserFiles.objects.get(user=user)
    except Exception:
        files = None

    mugshot_status = None
    biography_status = None
    irs_w9_status = None

    user_files = UserFilesForm(instance=files)
    try:
        mod = django.apps.apps.get_model(
            app_label='registration', model_name=user.profile.registration_type,
        )
        reg = mod.objects.get(user=user)
    except Exception:
        reg = None

    # if the user does not have any applications, the gm2m
    # field will throw an error at apps.all()
    try:
        apps = user.profile.applications
        # current grant cycle applications
        current_apps = []
        # current approved
        approved = []
        # past grant cycle applications
        past_apps = []
        start_date = get_start_date()
        for app in apps.all().order_by('-id'):
            if app.date_created >= start_date:
                current_apps.append(app)
                if app.status:
                    approved.append(app)
            elif app.multi_year and app.status:
                past_apps.append(app)
    except Exception:
        apps = None

    status = profile_status(user)

    if files:
        mugshot_status = files.status('mugshot')
        biography_status = files.status('biography')
        irs_w9_status = files.status('irs_w9')

    return render(
        request, 'dashboard/home.html', {
            'user_files': user_files,
            'reg': reg,
            'status': status,
            'approved': approved,
            'mugshot_status': mugshot_status,
            'biography_status': biography_status,
            'irs_w9_status': irs_w9_status,
            'current_apps': current_apps,
            'past_apps': past_apps,
            'professional_programs': [
                'aerospaceoutreach',
                'earlystageinvestigator',
                'highereducationinitiatives',
                'nasacompetition',
                'researchinfrastructure',
                'specialinitiatives',
            ],
            'rocket_competitions': ROCKET_COMPETITIONS_EXCLUDE,
        },
    )


@csrf_exempt
@login_required
def get_users(request):
    """AJAX GET for retrieving users via auto-complete."""
    query = request.GET.get('term', '')

    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query),
    ).order_by('last_name')

    auto_complete = []
    for user in users:
        user_json = {}
        name = "{0}, {1}".format(user.last_name, user.first_name)
        user_json['id'] = user.id
        user_json['label'] = name
        user_json['value'] = name
        auto_complete.append(user_json)

    return HttpResponse(
        json.dumps(auto_complete),
        content_type='application/json; charset=utf-8',
    )


@csrf_exempt
@login_required
def registration_type(request):
    """AJAX post for retrieving registration forms based on type."""
    jason = {}
    if request.method == 'POST':
        reg_type = request.POST.get('registration_type')
        try:
            mod = django.apps.apps.get_model(
                app_label='registration', model_name=reg_type,
            )
            reg = mod.objects.get(user=request.user)
        except Exception:
            reg = None
        try:
            reg_form = str_to_class(
                'djspace.registration.forms', '{0}Form'.format(reg_type),
            )(instance=reg, prefix='reg', use_required_attribute=False)
        except Exception:
            raise Http404
        reggie = None
        if reg:
            reggie = model_to_dict(reg)
            # remove some fields because json barfs on them and we don't need it
            for key in {'cv', 'programs'}:
                if key in reggie.keys():
                    reggie[key] = ''

        template = loader.get_template('dashboard/registration_form.inc.html')
        context = {'reg_form': reg_form, 'reg_type': reg_type}
        jason = {
            'form': template.render(context, request),
            'reg': reggie,
            'reg_type': reg_type,
        }
    return HttpResponse(
        json.dumps(jason),
        content_type='application/json; charset=utf-8',
    )


@login_required
def profile_form(request):
    """Form method that handles user profile data."""
    user = request.user
    profile = user.profile
    reg_type = profile.registration_type
    # user may have changed registration type
    mod_reg = (
        request.method == 'POST' and
        request.POST.get('pro-registration_type') != '' and
        reg_type != request.POST.get('pro-registration_type')
    )
    if mod_reg:
        reg_type = request.POST.get('pro-registration_type')
    try:
        mod = django.apps.apps.get_model(
            app_label='registration', model_name=reg_type,
        )
        reg = mod.objects.get(user=user)
    except Exception:
        reg = None
    if request.method == 'POST':
        reg_form = str_to_class(
            'djspace.registration.forms', '{0}Form'.format(reg_type),
        )(
            instance=reg,
            prefix='reg',
            label_suffix='',
            data=request.POST,
            files=request.FILES,
            use_required_attribute=False,
        )

        pro_form = UserProfileForm(
            instance=profile,
            data=request.POST,
            prefix='pro',
            label_suffix='',
            use_required_attribute=False,
        )
        usr_form = UserForm(
            prefix='usr',
            data=request.POST,
            label_suffix='',
            use_required_attribute=False,
        )
        if pro_form.is_valid() and reg_form.is_valid() and usr_form.is_valid():
            # User
            usr = usr_form.cleaned_data
            user.first_name = usr['first_name']
            user.last_name = usr['last_name']
            user.save()
            # registration type: undergrad, grad, faculty, grants, pro
            reg = reg_form.save(commit=False)
            reg.user = user
            reg.updated_by = user
            reg.save()
            if reg_type == 'TechnicalAdvisor':
                # delete all objects, then add current list because that is easier.
                reg.programs.clear()
                for prog in request.POST.getlist('reg-programs'):
                    reg.programs.add(prog)
            reg.save()
            # UserProfile
            pro = pro_form.save(commit=False)
            pro.salutation = usr['salutation']
            pro.second_name = usr['second_name']
            pro.updated_by = user
            pro.user = user
            # delete all objects, then add current list because that is easier.
            pro.race.clear()
            for raza in request.POST.getlist('pro-race'):
                pro.race.add(raza)
            pro.save()

            # redirect to dashboard with message
            messages.add_message(
                request,
                messages.SUCCESS,
                'Your profile has been saved.',
                extra_tags='success',
            )
            return HttpResponseRedirect(reverse('dashboard_home'))
    else:
        usr_form = UserForm(
            initial={
                'salutation': profile.salutation,
                'first_name': user.first_name,
                'second_name': profile.second_name,
                'last_name': user.last_name,
            },
            prefix='usr',
            label_suffix='',
            use_required_attribute=False,
        )
        reg_form = str_to_class(
            'djspace.registration.forms', '{0}Form'.format(reg_type),
        )(
            instance=reg,
            prefix='reg',
            label_suffix='',
            use_required_attribute=False,
        )
        pro_form = UserProfileForm(
            instance=profile,
            prefix='pro',
            label_suffix='',
            use_required_attribute=False,
        )
    return render(
        request,
        'dashboard/profile_form.html',
        {
            'pro_form': pro_form,
            'reg_form': reg_form,
            'usr_form': usr_form,
            'reg_type': reg_type,
        },
    )


@csrf_exempt
@login_required
def set_val(request):
    """AJAX POST for setting arbitrary values to an object."""
    user = request.user
    msg = "fail"
    instance = None
    if request.method == 'POST':
        cid = request.POST.get('cid')
        oid = request.POST.get('oid')
        field = request.POST.get('field')
        instance_value = request.POST.get('value')

        try:
            ct = ContentType.objects.get(pk=int(cid))
            mod = ct.model_class()
            instance = mod.objects.get(pk=int(oid))
        except Exception:
            msg = """
                Could not retrieve ContentType ({0}) or object ({1})
            """.format(cid, oid)

        if instance:
            # team leaders, co-advisors, and grants officers can upload files
            # for rocket launch teams and professional programs
            manager = False
            try:
                goid = instance.grants_officer.id
            except Exception:
                goid = None
            try:
                goid2 = instance.grants_officer2.id
            except Exception:
                goid2 = None
            try:
                coid1 = instance.co_advisor1.id
            except Exception:
                coid1 = None
            try:
                coid2 = instance.co_advisor2.id
            except Exception:
                coid2 = None
            try:
                coid3 = instance.co_advisor3.id
            except Exception:
                coid3 = None
            if ct.model == 'rocketlaunchteam':
                # this should be optimized
                if instance.leader.id == user.id or goid == user.id or goid2 == user.id or coid1 == user.id or coid2 == user.id or coid3 == user.id:
                    manager = True
            if ct.model in PROFESSIONAL_PROGRAMS:
                if goid == user.id or goid2 == user.id:
                    manager = True
            # is someone being naughty?
            if instance.user != user and not manager:
                msg = "Something is rotten in Denmark"
            else:
                setattr(instance, field, instance_value)
                msg = "success"
            instance.save()
    else:
        msg = "POST required"

    return HttpResponse(msg, content_type='text/plain; charset=utf-8')

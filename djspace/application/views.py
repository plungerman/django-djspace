# -*- coding: utf-8 -*-

import os
import datetime
import django

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from djspace.application.forms import *
from djspace.application.models import EDUCATION_INITITATIVES_PROGRAMS
from djspace.application.models import PROFESSIONAL_PROGRAMS
from djspace.application.models import ROCKET_LAUNCH_COMPETITION_WITH_LIMIT
from djspace.application.models import STUDENT_PROFESSIONAL_PROGRAMS
from djspace.application.models import ProfessionalProgramStudent
from djspace.core.forms import UserFilesForm
from djspace.core.models import UserFiles
from djspace.core.utils import profile_status
from djtools.fields.helpers import handle_uploaded_file
from djtools.utils.convert import str_to_class
from djtools.utils.mail import send_mail


@login_required
def application_form(request, application_type, aid=None):
    """All purpose view for all program applications."""
    # munge the application type
    slug_list = application_type.split('-')
    app_name = slug_list.pop(0).capitalize()
    for name in slug_list:
        app_name += ' {0}'.format(name.capitalize())
    app_type = ''.join(app_name.split(' '))

    # we need the application model now and if it barfs
    # we throw a 404
    try:
        mod = django.apps.apps.get_model(
            app_label='application', model_name=app_type,
        )
    except Exception:
        raise Http404
    # supes can update someone else's application
    superuser = request.user.is_superuser
    # fetch object if update
    app = None
    user = request.user
    if aid:
        # allow managers to update applications, so we set user to the owner,
        # otherwise the user is the person signed in.
        if superuser:
            app = get_object_or_404(mod, pk=aid)
            user = app.user
        else:
            # prevent users from managing apps that are not theirs
            try:
                app = mod.objects.get(pk=aid, user=user)
            except Exception:
                return HttpResponseRedirect(reverse('dashboard_home'))
            # verify that create_date is after grant cycle began
            # or that if the app is complete:
            # otherwise redirect to dashboard home
            if app.complete:
                return HttpResponseRedirect(reverse('dashboard_home'))

    # verify that the user has completed registration
    reg_type = user.profile.registration_type
    try:
        mod = django.apps.apps.get_model(
            app_label='registration', model_name=reg_type,
        )
    except Exception:
        if not superuser:
            # redirect to dashboard
            return HttpResponseRedirect(reverse('dashboard_home'))

    # verify that the user has an up to date registration
    if not profile_status(user) and not superuser:
        # redirect to dashboard
        return HttpResponseRedirect(reverse('dashboard_home'))

    # check rocket competition teams and member limits.
    # currently, FNL does not have a limit so we can exclude it.
    teams = None
    if 'rocket-competition' in application_type:
        teams = RocketLaunchTeam.objects.filter(
            competition__contains=app_name[:12],
        )

        if application_type != 'first-nations-rocket-competition':
            teams = teams.annotate(
                count=Count('members'),
            ).exclude(
                count__gte=settings.ROCKET_LAUNCH_COMPETITION_TEAM_LIMIT,
            ).order_by('name')

        if not teams:
            return render(
                request,
                'application/form.html',
                {'form': None, 'app_name': app_name},
            )

    # rocket launch team co-advisor
    coa_orig1 = None
    coa_orig2 = None
    coa_orig3 = None
    # rocket launch team team leader
    tl_orig = None
    # grants officer
    go_orig = None
    go2_orig = None
    if app:
        # we want to remove the old person if a new one is submitted
        # and add the new one to the application gm2m relationship
        # so that they can upload files on the dashboard
        if application_type == 'rocket-launch-team' and app.co_advisor1:
            # for autocomplete form field at the UI level
            request.session['co_advisor1_name'] = '{0}, {1}'.format(
                app.co_advisor1.last_name, app.co_advisor1.first_name,
            )
            coa_orig1 = app.co_advisor1
        if application_type == 'rocket-launch-team' and app.co_advisor2:
            # for autocomplete form field at the UI level
            request.session['co_advisor2_name'] = '{0}, {1}'.format(
                app.co_advisor2.last_name, app.co_advisor2.first_name,
            )
            coa_orig2 = app.co_advisor2
        if application_type == 'rocket-launch-team' and app.co_advisor3:
            # for autocomplete form field at the UI level
            request.session['co_advisor3_name'] = '{0}, {1}'.format(
                app.co_advisor3.last_name, app.co_advisor3.first_name,
            )
            coa_orig3 = app.co_advisor3

        if application_type == 'rocket-launch-team' and app.leader:
            # for autocomplete form field at the UI level
            request.session['leader_name'] = '{0}, {1}'.format(
                app.leader.last_name, app.leader.first_name,
            )
            tl_orig = app.leader

        if app.get_content_type().model in EDUCATION_INITITATIVES_PROGRAMS \
          or application_type == 'rocket-launch-team':
            if app.grants_officer:
                # for autocomplete form field at the UI level
                request.session['grants_officer_name'] = '{0}, {1}'.format(
                    app.grants_officer.last_name, app.grants_officer.first_name,
                )
                go_orig = app.grants_officer
            if app.grants_officer2:
                # for autocomplete form field at the UI level
                request.session['grants_officer2_name'] = '{0}, {1}'.format(
                    app.grants_officer2.last_name, app.grants_officer2.first_name,
                )
                go2_orig = app.grants_officer2

    # fetch the form class
    formclass = str_to_class(
        'djspace.application.forms', '{0}Form'.format(app_type),
    )
    # fetch the form instance
    try:
        form = formclass(
            instance=app, label_suffix='', use_required_attribute=False,
        )
    except Exception:
        # app_type does not match an existing form
        raise Http404
    # GET or POST
    if request.method == 'POST':
        post = request.POST
        try:
            # rocket launch team and Student Participant in Internship
            # forms need request context
            program = (
                application_type == 'rocket-launch-team' or
                application_type == 'professional-program-student' or
                application_type.replace('-', '') in PROFESSIONAL_PROGRAMS
            )
            if program:
                form = formclass(
                    instance=app,
                    data=post,
                    files=request.FILES,
                    request=request,
                    label_suffix='',
                    use_required_attribute=False,
                )
            else:
                form = formclass(
                    instance=app,
                    data=post,
                    files=request.FILES,
                    label_suffix='',
                    use_required_attribute=False,
                )
        except Exception:
            # app_type does not match an existing form
            raise Http404

        if form.is_valid():
            cd = form.cleaned_data
            data = form.save(commit=False)
            # we do not want to change owner of an application if a manager
            # is updating it
            if not app:
                data.user = user
            data.updated_by = user

            if application_type == 'rocket-launch-team':
                # limit number of team members if need be
                if data.competition in ROCKET_LAUNCH_COMPETITION_WITH_LIMIT:
                    data.limit = settings.ROCKET_LAUNCH_COMPETITION_TEAM_LIMIT
                else:
                    data.limit = 0

            # we should do this as a signal on user create
            try:
                uf = user.user_files
            except Exception:
                uf = UserFiles(user=user)

            # deal with FK relationships for programs
            if application_type == 'professional-program-student':
                program = cd['program']
                excludes = [
                    'CaNOP',
                    'MicroPropellantGauging',
                    'NasaInternship',
                    'SecondStageSpaceSciences',
                    'Student Ambassador',
                ]
                if program not in excludes:
                    mod = django.apps.apps.get_model(
                        app_label='application', model_name=program,
                    )
                    pk = request.POST.get('program_submissions')
                    if pk:
                        submission = mod.objects.get(pk=int(pk))
                        setattr(data, program, submission)

                        # set the others to None
                        for spp in STUDENT_PROFESSIONAL_PROGRAMS:
                            if spp[0] != program:
                                setattr(data, spp[0], None)

            # final save before clean up and mailing
            data.save()

            # add user to RocketLaunchTeam member m2m
            if 'rocket-competition' in application_type:
                data.team.members.add(data.user)

            # add work plan tasks for industry internship
            if application_type == 'industry-internship':
                tid = request.POST.getlist('tid[]')
                title = request.POST.getlist('title[]')
                description = request.POST.getlist('description[]')
                percent = request.POST.getlist('hours_percent[]')
                expected_outcome = request.POST.getlist('expected_outcome[]')

                # remove deleted tasks
                task_list = [t.id for t in data.workplantask_set.all()]
                dif = set(task_list).difference(tid)
                if len(dif) > 0:
                    for t in list(dif):
                        task = WorkPlanTask.objects.get(pk=int(t))
                        task.delete()
                # add or update tasks
                # len could use any of the above 5 lists from POST
                for i in range(0, len(tid)):
                    try:
                        task = WorkPlanTask.objects.get(pk=tid[i])
                    except Exception:
                        task = WorkPlanTask()
                        task.industry_internship = data
                    task.title = title[i]
                    task.description = description[i]
                    task.hours_percent = percent[i]
                    task.expected_outcome = expected_outcome[i]
                    task.save()

            # if not update add generic many-to-many relationship (gm2m)
            if not aid:
                date = data.date_created
                user.profile.applications.add(data)
            else:
                date = data.date_updated

            # add co-advisor to generic many-to-many relationsip (gm2m) if new
            # and remove the old one if need be
            if application_type == 'rocket-launch-team':
                coa1 = data.co_advisor1
                # we have a co_advisor1, check if the old matches new
                if (coa_orig1 and coa1) and coa1.id != coa_orig1.id:
                    # update
                    coa1.profile.applications.add(data)
                    # delete the old co_advisor1
                    coa_orig1.profile.applications.remove(data)
                elif coa_orig1 and not coa1:
                    # delete the old co_advisor1 because they removed
                    # the co_advisor1 from the field
                    coa_orig1.profile.applications.remove(data)
                elif coa1 and not coa_orig1:
                    # new application or new co_advisor1 on update
                    coa1.profile.applications.add(data)

                coa2 = data.co_advisor2
                # we have a co_advisor2, check if the old matches new
                if (coa_orig2 and coa2) and coa2.id != coa_orig2.id:
                    # update
                    coa2.profile.applications.add(data)
                    # delete the old co_advisor2
                    coa_orig2.profile.applications.remove(data)
                elif coa_orig2 and not coa2:
                    # delete the old co_advisor2 because they removed
                    # the co_advisor2 from the field
                    coa_orig2.profile.applications.remove(data)
                elif coa2 and not coa_orig2:
                    # new application or new co_advisor2 on update
                    coa2.profile.applications.add(data)

                coa3 = data.co_advisor3
                # we have a co_advisor3, check if the old matches new
                if (coa_orig3 and coa3) and coa3.id != coa_orig3.id:
                    # update
                    coa3.profile.applications.add(data)
                    # delete the old co_advisor3
                    coa_orig3.profile.applications.remove(data)
                elif coa_orig3 and not coa3:
                    # delete the old co_advisor3 because they removed
                    # the co_advisor3 from the field
                    coa_orig3.profile.applications.remove(data)
                elif coa3 and not coa_orig3:
                    # new application or new co_advisor3 on update
                    coa3.profile.applications.add(data)

            # add leader to generic many-to-many relationsip (gm2m) if new
            # and remove the old one if need be
            if application_type == 'rocket-launch-team':
                tl = data.leader
                # we have a co-advisor, check if the old matches new
                if (tl_orig and tl) and tl.id != tl_orig.id:
                    # update
                    tl.profile.applications.add(data)
                    # delete the old leader
                    tl_orig.profile.applications.remove(data)
                elif tl_orig and not tl:
                    # delete the old leader because they removed
                    # the leader from the field
                    tl_orig.profile.applications.remove(data)
                elif tl and not tl_orig:
                    # new application or new leader on update
                    tl.profile.applications.add(data)

            # add grants officer(s) to generic many-to-many relationsip if new
            # and remove the old one if need be
            if data.get_content_type().model in EDUCATION_INITITATIVES_PROGRAMS \
              or application_type == 'rocket-launch-team':
                # if we have grants officer, check if the old matches new
                go = data.grants_officer
                if (go_orig and go) and go.id != go_orig.id:
                    # update
                    go.profile.applications.add(data)
                    # delete the old grants officer
                    go_orig.profile.applications.remove(data)
                elif go_orig and not go:
                    # delete the old grants officer because they removed
                    # the grants officer from the field
                    go_orig.profile.applications.remove(data)
                elif go and not go_orig:
                    # new application or new co-advisor on update
                    go.profile.applications.add(data)
                # if we have grants officer2, check if the old matches new
                go2 = data.grants_officer2
                if (go2_orig and go2) and go2.id != go2_orig.id:
                    # update
                    go2.profile.applications.add(data)
                    # delete the old grants officer
                    go2_orig.profile.applications.remove(data)
                elif go2_orig and not go2:
                    # delete the old grants officer because they removed
                    # the grants officer from the field
                    go2_orig.profile.applications.remove(data)
                elif go2 and not go2_orig:
                    # new application or new co-advisor on update
                    go2.profile.applications.add(data)
            # email confirmation
            template = 'application/email/{0}.html'.format(application_type)
            if not settings.DEBUG:
                # email distribution list and bcc parameters
                to_list = [settings.WSGC_APPLICATIONS]
                bcc = [settings.ADMINS[0][1], settings.WSGC_EMAIL]
                # send confirmation email to WSGC staff and applicant
                to_list.append(data.user.email)
                # add folks for rocket competitions
                if 'rocket' in application_type:
                    to_list.append(settings.WSGC_ROCKET_EMAIL)
                if aid:
                    app_name += ' (UPDATED)'
                subject = '{0} {1}: {2}, {3}'.format(
                    app_name,
                    date,
                    data.user.last_name,
                    data.user.first_name,
                )
                frum = data.user.email
                send_mail(
                    request,
                    to_list,
                    subject,
                    frum,
                    template,
                    data,
                    reply_to=[frum,],
                    bcc=bcc,
                )
                return HttpResponseRedirect(reverse('application_success'))
            else:
                return render(
                    request,
                    template,
                    {'data': data, 'form': form},
                )
            return HttpResponseRedirect(reverse('application_success'))
    else:
        if not app:
            # set session values to null for GET requests that are not updates
            request.session['grants_officer_id'] = ''
            request.session['grants_officer'] = ''
            request.session['leader_id'] = ''
            request.session['leader_name'] = ''
            request.session['co_advisor1_id'] = ''
            request.session['co_advisor1_name'] = ''
    return render(
        request,
        'application/form.html',
        {
            'form': form,
            'app_name': app_name,
            'obj': app,
        },
    )


@csrf_exempt
@login_required
def get_program_submissions(request):
    """Obtain the program submissions."""
    programs = None

    if request.method == 'POST':
        program = request.POST.get('program')
        mentor_id = request.POST.get('mentor_id')
        aid = None
        if request.POST.get('aid') != '0':
            pk = int(request.POST.get('aid'))
            app = ProfessionalProgramStudent.objects.get(pk=pk)
            app_prog = getattr(app, program)

            if app_prog:
                aid = app_prog.id

        user = User.objects.get(pk=mentor_id)
        try:
            mod = django.apps.apps.get_model(
                app_label='application', model_name=program,
            )
            programs = mod.objects.filter(user=user)
        except Exception:
            programs = None

    template = loader.get_template('application/get_program_submissions.inc.html')
    template = template.render({'programs': programs, 'aid': aid}, request)
    return HttpResponse(template, content_type='text/plain; charset=utf-8')


@staff_member_required
def application_print(request, application_type, aid):
    """Print view for applications. AKA: the demographic page/view."""
    user = request.user
    # munge the application type
    slug_list = application_type.split('-')
    app_name = slug_list.pop(0).capitalize()
    for slug in slug_list:
        app_name += ' {0}'.format(slug.capitalize())
    app_type = ''.join(app_name.split(' '))
    mod = django.apps.apps.get_model(
        app_label='application', model_name=app_type,
    )
    content_type = ContentType.objects.get_for_model(mod)
    instance = get_object_or_404(mod, pk=aid)
    if instance.user == user or user.is_superuser:
        try:
            files = instance.user.user_files
        except Exception:
            files = None
        if files:
            instance.mugshot_status = files.status('mugshot')
            instance.biography_status = files.status('biography')
            instance.irs_w9_status = files.status('irs_w9')
            instance.content_type = content_type.id
        response = render(
            request,
            'application/email/{0}.html'.format(application_type),
            {
                'data': instance,
            },
        )
    else:
        response = HttpResponseRedirect(reverse('dashboard_home'))

    return response


@staff_member_required
def application_export(request, application_type):
    """Export applications."""
    users = User.objects.all().order_by('last_name')

    today = datetime.date.today()
    exports = []
    for user in users:
        try:
            apps = user.profile.applications.all()
        except Exception:
            apps = None
        if apps:
            for app in apps:
                if app.get_slug() == application_type:
                    exports.append({'user': user, 'app': app})
                    program = app.get_application_type()

    if settings.DEBUG:
        response = render(
            request,
            'application/export.html',
            {'exports': exports, 'program': program, 'year': today.year},
            content_type='text/plain; charset=utf-8',
        )
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(
            application_type,
        )

        template = loader.get_template('application/export.html')
        context = {
            'exports': exports,
            'program': program,
            'year': today.year,
        }
        response.write(template.render(context, request))

    return response

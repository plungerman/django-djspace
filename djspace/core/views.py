# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from djspace.dashboard.views import UPLOAD_FORMS
from djspace.core.forms import PhotoForm, UserFilesForm
from djspace.core.forms import EmailApplicantsForm
from djspace.core.models import UserFiles
from djspace.core.utils import files_status
from djspace.application.models import *

from djtools.utils.mail import send_mail


@staff_member_required
def sendmail(request, redirect):
    """
    Send emails to program applicants.
    POST from admin action email_applicants.
    """

    redirect = '{}/{}'.format(settings.ROOT_URL, redirect)
    if request.POST:
        # form stuff
        form = EmailApplicantsForm(request.POST)
        form.is_valid()
        data = form.cleaned_data
        # content type
        ct = ContentType.objects.get_for_id(data['content_type'])
        # program ids
        pids = request.POST.getlist('pids[]')
        # email subject
        sub = "WSGC: Information about your {} application".format(
            data['title']
        )
        BCC = [request.user.email,settings.SERVER_MAIL]
        for pid in pids:
            obj = ct.get_object_for_this_type(pk=pid)
            to = [obj.user.email]
            send_mail(
                request, to, sub, settings.SERVER_EMAIL,
                'admin/email_data.html',
                {'obj':obj,'content':data['content']},BCC
            )
        messages.add_message(
            request, messages.SUCCESS,
            'Your message was sent successfully.',
            extra_tags='success'
        )
        return HttpResponseRedirect(redirect)
    else:
        return HttpResponseRedirect(redirect)


import logging
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def photo_upload(request):
    """
    AJAX POST for uploading a photo for any given application
    """

    user = request.user
    response = None
    if request.is_ajax() and request.method == 'POST':
        form = PhotoForm(
            data=request.POST, files=request.FILES
        )
        logger.debug("files = {}".format(request.FILES))
        if form.is_valid():
            ct = request.POST.get('content_type')
            oid = request.POST.get('oid')
            if ct and oid:
                ct = ContentType.objects.get(pk=ct)
                mod = ct.model_class()
                #try:
                if True:
                    obj = mod.objects.get(pk=oid)
                    phile = form.save(commit=False)
                    phile.content_object = obj
                    phile.save()
                    response = render(
                        request, 'dashboard/view_photo.ajax.html', {
                            'photo':phile,'ct':ct,'oid':oid
                        }
                    )
                #except Exception, e:
                else:
                    #msg = "Fail: {}".format(str(e))
                    msg = "Fail"
            else:
                msg = "Fail: No Content Type or Object ID Provided"
        else:
            msg = "Fail: {}".format(form.errors)
    else:
        msg = "AJAX POST required"

    if not response:
        response = HttpResponse(
            msg, content_type='text/plain; charset=utf-8'
        )

    return response


@csrf_exempt
@login_required
def user_files(request):
    """
    update user files via ajax post
    """
    user = request.user
    response = None
    if request.method != 'POST':
        msg = "POST required"
    else:
        ct = request.POST.get('content_type')
        if ct:
            ct = ContentType.objects.get(pk=ct)
            mod = ct.model_class()
            obj = mod.objects.get(pk=request.POST.get('oid'))
            # team leaders can upload files for rocket launch teams
            leader = False
            co_advisor = False
            if ct.model == 'rocketlaunchteam':
                if obj.leader.id == user.id:
                    leader = True
                elif obj.co_advisor and obj.co_advisor.id == user.id:
                    co_advisor = True
            # is someone being naughty?
            if obj.user != user and not (leader or co_advisor):
                return HttpResponse(
                    "Something is rotten in Denmark",
                    content_type='text/plain; charset=utf-8'
                )
            else:
                form = UPLOAD_FORMS[ct.model](
                    data=request.POST, files=request.FILES, instance=obj
                )
        else:
            try:
                instance = UserFiles.objects.get(user=user)
            except:
                instance = None
            form = UserFilesForm(
                data=request.POST, files=request.FILES, instance=instance
            )
        field_name = request.POST.get('field_name')
        if form.is_valid():
            msg = 'Success'
            phile = form.save(commit=False)
            if not ct:
                phile.user = user
            phile.save()
            earl = getattr(phile,field_name)
            response = render(
                request, 'dashboard/view_file.ajax.html', {
                    'earl':earl.url,'field_name':field_name
                }
            )
        else:
            msg = 'Fail: {}'.format(form.errors)

    if not response:
        response = HttpResponse(
            msg, content_type='text/plain; charset=utf-8'
        )
    return response


@csrf_exempt
@login_required
def check_files_status(request):
    """
    Determine if the user has all of her files uploaded or not.
    Method: ajax post
    Return: True or False
    """
    user = request.user
    response = None
    if request.method != 'POST':
        status = "POST required"
    else:
        status = files_status(request.user)

    return HttpResponse(
        status, content_type='text/plain; charset=utf-8'
    )


@csrf_exempt
def user_files_test(request):

    user = request.user
    response = None
    valid='get'
    if request.method == 'POST':
        valid='no'
        ct = request.POST.get('ct')
        ct = ContentType.objects.get(pk=ct)
        mod = ct.model_class()
        obj = mod.objects.get(pk=request.POST.get('oid'))
        form = UPLOAD_FORMS[ct.model](
            data=request.POST, files=request.FILES, instance=obj
        )
        if form.is_valid():
            form.save()
            valid='yes'
        else:
            valid=form.errors
    else:
        ct = request.GET.get('ct')
        ct = ContentType.objects.get(pk=ct)
        mod = ct.model_class()
        obj = mod.objects.get(pk=request.GET.get('oid'))
        form = UPLOAD_FORMS[ct.model](instance=obj)
    return render(
        request, 'dashboard/test.html', {
            'form':form, 'valid':valid
        }
    )


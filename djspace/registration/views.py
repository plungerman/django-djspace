from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response, get_object_or_404

from djspace.registration.forms import UndergraduateInformationForm
from djtools.utils.mail import send_mail


def undergrad(request):
    form = UndergraduateInformationForm()

    return render_to_response(
        "registration/form.html",
        {"form": form,},
        context_instance=RequestContext(request)
    )



def myview(request,pid):
    if settings.DEBUG:
        TO_LIST = [settings.SERVER_EMAIL,]
    else:
        TO_LIST = [settings.MY_APP_EMAIL,]
    BCC = settings.MANAGERS

    if request.method=='POST':
        form = MyForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            email = settings.DEFAULT_FROM_EMAIL
            if data.email:
                email = data.email
            subject = "[Submit] %s %s" % (data.first_name,data.last_name)
            send_mail(
                request,TO_LIST, subject, email,"myapp/email.html", data, BCC
            )
            return HttpResponseRedirect(
                reverse_lazy("myapp_success")
            )
    else:
        form = MyForm()
    return render_to_response(
        "myapp/form.html",
        {"form": form,},
        context_instance=RequestContext(request)
    )

def search(request):
    return render_to_response(
        "myapp/search.html",
        context_instance=RequestContext(request)
    )


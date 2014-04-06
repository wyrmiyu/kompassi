# encoding: utf-8

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods, require_GET

from core.forms import PersonForm
from core.models import Event, Person
from core.utils import initialize_form, url, json_response, render_string

from ..forms import SignupForm, SignupAdminForm
from ..helpers import labour_admin_required
from ..models import LabourEventMeta, Qualification, PersonQualification, Signup, JobCategory

from .view_helpers import initialize_signup_forms


@labour_admin_required
def labour_admin_dashboard_view(request, vars, event):
    vars.update(
        signups=event.signup_set.order_by('-created_at')[:5]
    )

    return render(request, 'labour_admin_dashboard_view.jade', vars)


@labour_admin_required
@require_http_methods(['GET', 'POST'])
def labour_admin_signup_view(request, vars, event, person_id):
    person = get_object_or_404(Person, pk=int(person_id))
    signup = get_object_or_404(Signup, person=person, event=event)

    old_state = signup.state

    signup_form, signup_extra_form = initialize_signup_forms(request, event, signup,
        readonly=True
    )
    signup_admin_form = initialize_form(SignupAdminForm, request,
        instance=signup, 
        prefix='admin',
    )
    person_form = initialize_form(PersonForm, request,
        instance=signup.person,
        prefix='person',
        submit_button=False,
        readonly=True
    )

    if request.method == 'POST':
        if signup_admin_form.is_valid():
            signup_admin_form.save()
            signup.state_change_from(old_state)
            messages.success(request, u'Tiedot tallennettiin.')

    vars.update(
        person_form=person_form,
        signup=signup,
        signup_admin_form=signup_admin_form,
        signup_extra_form=signup_extra_form,
        signup_form=signup_form,
    )

    return render(request, 'labour_admin_signup_view.jade', vars)


@labour_admin_required
def labour_admin_signups_view(request, vars, event):
    signups = event.signup_set.all().order_by('person__surname', 'person__first_name')

    vars.update(
        signups=signups,
    )

    return render(request, 'labour_admin_signups_view.jade', vars)


def labour_admin_roster_vars(request, event):
    from programme.utils import full_hours_between

    hours = full_hours_between(event.labour_event_meta.work_begins, event.labour_event_meta.work_ends)

    return dict(
        hours=hours,
        num_hours=len(hours)
    )


@labour_admin_required
def labour_admin_roster_view(request, vars, event):
    vars.update(
        **labour_admin_roster_vars(request, event)
    )

    return render(request, 'labour_admin_roster_view.jade', vars)


@labour_admin_required
def labour_admin_roster_job_category_fragment(request, vars, event, job_category):
    job_category = get_object_or_404(JobCategory, event=event, pk=job_category)

    vars.update(
        **labour_admin_roster_vars(request, event)
    )

    hours = vars['hours']

    vars.update(
        job_category=job_category,
        totals=[0 for i in hours],
    )

    return json_response(dict(
        replace='#jobcategory-{0}-placeholder'.format(job_category.pk),
        content=render_string(request, 'labour_admin_roster_job_category_fragment.jade', vars)
    ))


@labour_admin_required
@require_GET
def labour_admin_mail_view(request, vars, event):
    from mailings.models import Message

    messages = Message.objects.filter(event=event)

    vars.update(
        messages=messages
    )

    return render(request, 'labour_admin_mail_view.jade', vars)


@labour_admin_required
@require_http_methods(['GET', 'POST'])
def labour_admin_mail_editor_view(request, vars, event, message_id=None):
    from mailings.models import Message
    from mailings.forms import MessageForm

    if message_id:
        message = get_object_or_404(Message, event=event, pk=int(message_id))
    else:
        message = None

    form = initialize_form(MessageForm, request, instance=message)

    if request.method == 'POST':
        if form.is_valid():
            message = form.save(commit=False)

            message.app_label = 'labour'
            message.event = event
            message.save()

            return redirect('labour_admin_mail_preview_view', event.slug, message.pk)
        else:
            messages.error(request, u'Ole hyvä ja tarkasta lomake.')

    vars.update(
        message=message,
        form=form,
        sender="TODO",
    )

    return render(request, 'labour_admin_mail_editor_view.jade', vars)

@labour_admin_required
@require_http_methods(['GET', 'POST'])
def labour_admin_mail_preview_view(request, vars, event, message_id=None):
    message = get_object_or_404(Message, event=event, pk=int(message_id))    

    vars.update(
        message=message
    )

    return render(request, 'labour_admin_mail_preview_view.jade', vars)

@labour_admin_required
@require_GET
def labour_admin_mail_preview_fragment(request, vars, event, message_id, person_username):
    pass


def labour_admin_menu_items(request, event):
    dashboard_url = url('labour_admin_dashboard_view', event.slug)
    dashboard_active = request.path == dashboard_url
    dashboard_text = u"Kojelauta"

    signups_url = url('labour_admin_signups_view', event.slug)
    signups_active = request.path.startswith(signups_url)
    signups_text = u"Tapahtumaan ilmoittautuneet henkilöt"

    mail_url = url('labour_admin_mail_view', event.slug)
    mail_active = request.path.startswith(mail_url)
    mail_text = u"Työvoimaviestit"

    # roster_url = url('labour_admin_roster_view', event.slug)
    # roster_active = request.path == roster_url
    # roster_text = u"Työvuorojen suunnittelu"

    return [
        (dashboard_active, dashboard_url, dashboard_text),
        (signups_active, signups_url, signups_text),
        (mail_active, mail_url, mail_text),
        # (roster_active, roster_url, roster_text),
    ]

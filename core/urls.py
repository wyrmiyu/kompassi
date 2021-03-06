from django.conf.urls import patterns, include, url
from django.shortcuts import redirect
from django.contrib.auth.views import logout

from .forms import LoginForm
from .views import (
    core_admin_impersonate_view,
    core_email_verification_request_view,
    core_email_verification_view,
    core_event_view,
    core_frontpage_view,
    core_login_view,
    core_logout_view,
    core_password_reset_request_view,
    core_password_reset_view,
    core_password_view,
    core_personify_view,
    core_profile_view,
    core_registration_view,
)


urlpatterns = patterns(
    '',

    url(r'^$', core_frontpage_view, name='core_frontpage_view'),
    url(r'^events/(?P<event_slug>[a-z0-9-]+)/?$', core_event_view, name='core_event_view'),
    url(r'^login$', core_login_view, name='core_login_view'),
    url(r'^logout$', core_logout_view, name='core_logout_view'),
    url(r'^register$', core_registration_view, name='core_registration_view'),
    url(r'^profile$', core_profile_view, name='core_profile_view'),
    url(r'^profile/new$', core_personify_view, name='core_personify_view'),
    url(r'^profile/password$', core_password_view, name='core_password_view'),
    url(r'^profile/password/reset$', core_password_reset_request_view, name='core_password_reset_request_view'),
    url(r'^profile/password/reset/(?P<code>[a-f0-9]+)$', core_password_reset_view, name='core_password_reset_view'),
    url(r'^profile/email/verify$', core_email_verification_request_view, name='core_email_verification_request_view'),
    url(r'^profile/email/verify/(?P<code>[a-f0-9]+)$', core_email_verification_view, name='core_email_verification_view'),
    url(r'^impersonate/(?P<username>[a-zA-Z0-9_-]+)$', core_admin_impersonate_view, name='core_admin_impersonate_view'),
)

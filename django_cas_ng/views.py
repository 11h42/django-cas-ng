"""CAS login/logout replacement views"""

from __future__ import absolute_import
from __future__ import unicode_literals

from django.utils.six.moves import urllib_parse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import (
    logout as auth_logout,
    login as auth_login,
    authenticate
)
from django.contrib import messages
from django.contrib.sessions.models import Session

from datetime import timedelta

from .models import ProxyGrantingTicket, SessionTicket
from .utils import (get_cas_client, get_service_url,
                    get_protocol, get_redirect_url)

__all__ = ['login', 'logout', 'callback']


@csrf_exempt
def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""
    service_url = get_service_url(request, next_page)
    client = get_cas_client(service_url=service_url)

    if request.method == 'POST' and request.POST.get('logoutRequest'):
        for slo in client.get_saml_slos(request.POST.get('logoutRequest')):
            try:
                SessionTicket.objects.get(ticket=slo.text).session.delete()
            except SessionTicket.DoesNotExist:
                pass
    if not next_page:
        next_page = get_redirect_url(request)
    if request.user.is_authenticated():
        message = "You are logged in as %s." % request.user.get_username()
        messages.success(request, message)
        return HttpResponseRedirect(next_page)

    ticket = request.GET.get('ticket')
    if ticket:
        user = authenticate(ticket=ticket,
                            service=service_url,
                            request=request)
        pgtiou = request.session.get("pgtiou")
        if user is not None:
            auth_login(request, user)
            if not request.session.exists(request.session.session_key):
                request.session.create()
            session = Session.objects.get(
                session_key=request.session.session_key
            )
            SessionTicket.objects.create(
                session=session,
                ticket=ticket
            )

            if pgtiou and settings.CAS_PROXY_CALLBACK:
                # Delete old PGT
                ProxyGrantingTicket.objects.filter(
                    user=user,
                    session=session
                ).delete()
                # Set new PGT ticket
                try:
                    pgt = ProxyGrantingTicket.objects.get(pgtiou=pgtiou)
                    pgt.user = user
                    pgt.session = session
                    pgt.save()
                except ProxyGrantingTicket.DoesNotExist:
                    pass
                del request.session["pgtiou"]

            name = user.get_username()
            message = "Login succeeded. Welcome, %s." % name
            messages.success(request, message)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(client.get_login_url())
        else:
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(client.get_login_url())


def logout(request, next_page=None):
    """Redirects to CAS logout page"""
    auth_logout(request)
    next_page = next_page or get_redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        protocol = get_protocol(request)
        host = request.get_host()
        redirect_url = urllib_parse.urlunparse(
            (protocol, host, next_page, '', '', ''),
        )
        client = get_cas_client()
        return HttpResponseRedirect(client.get_logout_url(redirect_url))
    else:
        # This is in most cases pointless if not CAS_RENEW is set. The user will
        # simply be logged in again on next request requiring authorization.
        return HttpResponseRedirect(next_page)


@csrf_exempt
def callback(request):
    """Read PGT and PGTIOU send by CAS"""
    if request.method == 'POST':
        if request.POST.get('logoutRequest'):
            client = get_cas_client()
            slos = client.get_saml_slos(request.POST.get('logoutRequest'))
            ProxyGrantingTicket.objects.filter(pgt__in=slos).delete()
        return HttpResponse("ok\n", content_type="text/plain")
    elif request.method == 'GET':
        pgtid = request.GET.get('pgtId')
        pgtiou = request.GET.get('pgtIou')
        pgt = ProxyGrantingTicket.objects.create(pgtiou=pgtiou, pgt=pgtid)
        pgt.save()
        ProxyGrantingTicket.objects.filter(
            session=None,
            date__lt=(timezone.now() - timedelta(seconds=60))
        ).delete()
        return HttpResponse("ok\n", content_type="text/plain")

Django CAS NG
=============

.. image:: https://travis-ci.org/mingchen/django-cas-ng.svg?branch=master
    :target: https://travis-ci.org/mingchen/django-cas-ng


``django-cas-ng`` is CAS (Central Authentication Service) client implementation.
This project inherit from `django-cas`_.
`django-cas`_ is not updated since 2013-4-1. This project will include new bugfix
and new feature development.


Features
--------

- Support CAS_ version 1.0, 2.0 and 3.0.
- Support Django 1.5, 1.6, 1.7 with `User custom model`_
- Support Python 2.7, 3.x


Installation
------------

Install with `pip`_::

    pip install django-cas-ng


Install the latest code::

    pip install https://github.com/mingchen/django-cas-ng/archive/master.zip


Install from source code::

    python setup.py install


Settings
--------

Now add it to the middleware and authentication backends in your settings.
Make sure you also have the authentication middleware installed.
Here's an example::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        ...
    )

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )

Set the following required setting in ``settings.py``:

* ``CAS_SERVER_URL``: This is the only setting you must explicitly define.
   Set it to the base URL of your CAS source (e.g. https://account.example.com/cas/).

Optional settings include:

* ``CAS_ADMIN_PREFIX``: The URL prefix of the Django administration site.
  If undefined, the CAS middleware will check the view being rendered to
  see if it lives in ``django.contrib.admin.views``.
* ``CAS_CREATE_USER``: Create a user when the CAS authentication is successful.
  The default is ``True``.
* ``CAS_EXTRA_LOGIN_PARAMS``: Extra URL parameters to add to the login URL
  when redirecting the user. Example::

    CAS_EXTRA_LOGIN_PARAMS = {'renew': true}

* ``CAS_RENEW``: whether pass ``renew`` parameter on login and verification
  of ticket to enforce that the login is made with a fresh username and password
  verification in the CAS server. Default is ``False``.
* ``CAS_IGNORE_REFERER``: If ``True``, logging out of the application will
  always send the user to the URL specified by ``CAS_REDIRECT_URL``.
* ``CAS_LOGOUT_COMPLETELY``: If ``False``, logging out of the application
  won't log the user out of CAS as well.
* ``CAS_REDIRECT_URL``: Where to send a user after logging in or out if
  there is no referrer and no next page set. Default is ``/``.
* ``CAS_RETRY_LOGIN``: If ``True`` and an unknown or invalid ticket is
  received, the user is redirected back to the login page.
* ``CAS_VERSION``: The CAS protocol version to use. ``'1'`` and ``'2'`` are
  supported, with ``'2'`` being the default.
* ``CAS_USERNAME_ATTRIBUTE``: The CAS user name attribute from response. The default is ``uid``.
* ``CAS_PROXY_CALLBACK``: The full url to the callback view if you want to
  retrive a Proxy Granting Ticket

Make sure your project knows how to log users in and out by adding these to
your URL mappings::

    (r'^accounts/login$', 'django_cas_ng.views.login'),
    (r'^accounts/logout$', 'django_cas_ng.views.logout'),

You should also add an URL mapping for the ``CAS_PROXY_CALLBACK`` settings::

    (r'^accounts/callback$', 'django_cas_ng.views.callback'),

Users should now be able to log into your site using CAS.

Signals
-------

``django_cas_ng.signals.cas_user_authenticated``

Sent on successful authentication, the ``CASBackend`` will fire the ``cas_user_authenticated`` signal.

**Arguments sent with this signal**

**sender**
  The authentication backend instance that authenticated the user.

**user**
  The user instance that was just authenticated.

**created**
  Boolean as to whether the user was just created.

**attributes**
  Attributes returned during by the CAS during authentication.

**ticket**
  The ticket used to authenticate the user with the CAS.

**service**
  The service used to authenticate the user with the CAS.


Testing
-------

Every code commit triggers a **travis-ci** build. checkout current build status at https://travis-ci.org/mingchen/django-cas-ng

Testing is managed by ``pytest`` and ``tox``.
Before run install, you need install required packages for testing::

    pip install -r requirements-dev.txt


To run testing on locally::

    py.test


To run all testing on all enviroments locally::

    tox


Contribution
------------

Contributions are welcome!

If you would like to contribute this project.
Please feel free to fork and send pull request.
Please make sure tests are passed.
Also welcome to add your name to **Credits** section of this document.

New code should follow both `PEP8`_ and the `Django coding style`_.


Credits
-------

* `django-cas`_.
* `Stefan Horomnea`_.
* `Piotr Buliński`_.
* `Piper Merriam`_.
* `Nathan Brown`_.
* `Jason Brownbridge`_.
* `Bryce Groff`_.
* `Jeffrey P Gill`_.
* `timkung1`_.
* `Domingo Yeray Rodríguez Martín`_.
* `Rayco Abad-Martín`_.
* `Édouard Lopez`_.
* `Guillaume Vincent`_.

References
----------

* `django-cas`_
* `CAS protocol`_
* `Jasig CAS server`_

.. _CAS: https://www.apereo.org/cas
.. _CAS protocol: https://www.apereo.org/cas/protocol
.. _django-cas: https://bitbucket.org/cpcc/django-cas
.. _pip: http://www.pip-installer.org/
.. _PEP8: http://www.python.org/dev/peps/pep-0008
.. _Django coding style: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style
.. _User custom model: https://docs.djangoproject.com/en/1.5/topics/auth/customizing/
.. _Jasig CAS server: http://jasig.github.io/cas
.. _Piotr Buliński: https://github.com/piotrbulinski
.. _Stefan Horomnea: https://github.com/choosy
.. _Piper Merriam: https://github.com/pipermerriam
.. _Nathan Brown: https://github.com/tsitra
.. _Jason Brownbridge: https://github.com/jbrownbridge
.. _Bryce Groff: https://github.com/bgroff
.. _Jeffrey P Gill: https://github.com/jpg18
.. _timkung1: https://github.com/timkung1
.. _Domingo Yeray Rodríguez Martín: https://github.com/dyeray
.. _Rayco Abad-Martín: https://github.com/Rayco
.. _Édouard Lopez: https://github.com/edouard-lopez
.. _Guillaume Vincent: https://github.com/guillaumevincent

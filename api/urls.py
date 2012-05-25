# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource
from andaluciapeople.api.handlers import *
from piston.doc import documentation_view
from piston.authentication import HttpBasicAuthentication, OAuthAuthentication

auth = HttpBasicAuthentication(realm='AndaluciaPeople API')
oauth = OAuthAuthentication()

sitio_handler = Resource(SitioHandler, authentication=oauth)

urlpatterns = patterns('',
   url(r'^sitio/$', sitio_handler),

   url(r'^$', documentation_view),
)

urlpatterns += patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)
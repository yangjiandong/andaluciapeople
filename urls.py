# -*- coding: utf-8 -*-
'''
    andaluciapeople.com
    Copyright (C) 2008-2009  Manuel Martín Salvador <draxus@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
	#(r'^admin/filebrowser/', include('filebrowser.urls')),
    (r'^admin/(.*)', include(admin.site.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    #(r'^facebook/', include('facebookconnect.urls')),
    #(r'^facebook/', include('django_facebook.urls')),
    (r'^captcha/', include('captcha.urls')),
    #(r'^api/', include('api.urls')),
    #(r'^oauth/', include('oauth_provider.urls')),
    (r'^auth/', include('andaluciapeople.oauth_access.urls')),
    (r'^m/', include('andaluciapeople.sitios.urls'), {'mobile': True}),
    (r'^rosetta/', include('andaluciapeople.rosetta.urls')),
    (r'^localeurl/', include('localeurl.urls')),
    (r'^', include('andaluciapeople.sitios.urls')),
)


if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
  );

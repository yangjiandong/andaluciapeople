# -*- coding: utf-8 -*-
# Django settings for AndaluciaPeople project.
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

from os import path
import re

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASEDIR = path.dirname(path.abspath(__file__))

BASEURL = 'http://127.0.0.1:8000/'

ADMINS = (
     ('Administrador', '<EMAIL>'),
)
MANAGERS = ADMINS

BUG_EMAIL = '<EMAIL>'
EMAIL = '<EMAIL>'
DEFAULT_FROM_EMAIL = EMAIL
EMAIL_USE_TLS = True
EMAIL_HOST = '<HOST>'
EMAIL_HOST_USER = '<USER>'
EMAIL_HOST_PASSWORD = '<PASSWORD>'
EMAIL_PORT = 3306

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'anda',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}

CACHE_BACKEND = 'locmem:///'
#CACHE_BACKEND = 'db://cache_table?max_entries=5000'
CACHE_MIDDLEWARE_ALIAS = 'andpeople'
CACHE_MIDDLEWARE_SECONDS = 300


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-es'

SITE_ID = 2 # IMPORTANTE: Ajustar para las flatpages

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

DEFAULT_CHARSET = 'utf-8'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = '/var/www/django/andaluciapeople/media/'
MEDIA_ROOT = path.join(BASEDIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '<SECRET_KEY>'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'andaluciapeople.messages.context_processors.inbox',
    'andaluciapeople.sitios.context_processors.ip_address',
    'andaluciapeople.sitios.context_processors.pretitle',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'localeurl.middleware.LocaleURLMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'andaluciapeople.facebook.djangofb.FacebookMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'andaluciapeople.facebookconnect.middleware.FacebookConnectMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    #'django.middleware.http.SetRemoteAddrFromForwardedFor', #para que funcione bien REMOTE_ADDR
    'andaluciapeople.tracking.middleware.VisitorTrackingMiddleware',
    'andaluciapeople.tracking.middleware.VisitorCleanUpMiddleware',
    'andaluciapeople.tracking.middleware.BannedIPMiddleware',
    'andaluciapeople.minidetector.Middleware',
)

ROOT_URLCONF = 'andaluciapeople.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(BASEDIR, 'templates'),
    path.join(BASEDIR, 'blogapp', 'templates'),
    #path.join(BASEDIR, 'facebookconnect', 'templates'),
    path.join(BASEDIR, 'piston', 'templates'),
    #path.join(path.dirname(__file__), 'templates').replace('\\','/'),
)

AUTHENTICATION_BACKENDS = (
    #'andaluciapeople.facebookconnect.models.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    #'oauth_provider',
    'localeurl',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sitemaps',
    'django.contrib.databrowse',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.comments',
    'andaluciapeople.sitios',
    'andaluciapeople.registration',
    'andaluciapeople.sorl.thumbnail',
    'andaluciapeople.blogapp',
    'andaluciapeople.trackback',
    'andaluciapeople.tracking',
    'andaluciapeople.messages',
    #'andaluciapeople.facebookconnect',
    'andaluciapeople.captcha',
    'andaluciapeople.api',
    'andaluciapeople.oauth_access',
    'andaluciapeople.rosetta',
    'andaluciapeople.haystack',
    'andaluciapeople.hitcount',
    'django_extensions',
    'south'
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CACHE_DEF_EXPIRE = 60 * 60 * 24

LANGUAGES = (
    ('es-es', u'Español'),
    ('en', u'English'),
)

AUTH_PROFILE_MODULE = "sitios.datosusuario"
ACCOUNT_ACTIVATION_DAYS = 2
THUMBNAIL_DEBUG = True
THUMBNAIL_SUBDIR = 'mini'
LOGIN_URL = '/register/'
LOGIN_REDIRECT_URL = '/profile/'

FACEBOOK_API_ID = '<FACEBOOK_API_ID>'
FACEBOOK_APP_SECRET = '<FACEBOOK_APP_SECRET>'

OAUTH_ACCESS_SETTINGS = {
        'facebook': {
            'keys': {
                'KEY': '<FACEBOOK_API_ID>',
                'SECRET': '<FACEBOOK_APP_SECRET>',
            },
            'endpoints': {
                'access_token': 'https://graph.facebook.com/oauth/access_token',
                'authorize': 'https://graph.facebook.com/oauth/authorize',
                'provider_scope': '',
                'callback': 'andaluciapeople.sitios.oauth_callbacks.FacebookCallback',
            }
        },
        'twitter': {
            'keys': {
                'KEY': '<TWITTER_API_KEY>',
                'SECRET': '<TWITTER_API_SECRET>',
            },
            'endpoints': {
                'request_token': 'https://api.twitter.com/oauth/request_token',
                'access_token': 'https://api.twitter.com/oauth/access_token',
                'authorize': 'https://api.twitter.com/oauth/authorize',
                'provider_scope': '',
                'callback': 'andaluciapeople.sitios.oauth_callbacks.TwitterCallback',
            }
        },
        'google': {
            'keys': {
                'KEY': '<GOOGLE_API_KEY>',
                'SECRET': '<GOOGLE_API_SECRET>',
            },
            'endpoints': {
                'request_token': 'https://www.google.com/accounts/OAuthGetRequestToken',
                'access_token': 'https://www.google.com/accounts/OAuthGetAccessToken',
                'authorize': 'https://www.google.com/accounts/OAuthAuthorizeToken',
                'provider_scope': '',
                'callback': 'andaluciapeople.sitios.oauth_callbacks.GoogleCallback',
            }
        },
        'foursquare': {
            'keys': {
                'KEY': '<FOURSQUARE_API_KEY>',
                'SECRET': '<FOURSQUARE_API_SECRET>',
            },
            'endpoints': {
                'request_token': 'http://foursquare.com/oauth/request_token',
                'access_token': 'http://foursquare.com/oauth/access_token',
                'authorize': 'http://foursquare.com/oauth/authorize',
                'provider_scope': '',
                'callback': 'andaluciapeople.sitios.oauth_callbacks.FoursquareCallback',
            }
        }
    }

CAPTCHA_FONT_PATH=BASEDIR+"/captcha/fonts/ttf-bitstream-vera-1.10/Vera.ttf"
CAPTCHA_FONT_SIZE=30
CAPTCHA_BACKGROUND_COLOR='#EFEACF'
#CAPTCHA_FILTER_FUNCTIONS=()

LASTFM_API_KEY='<LASTFM_API_KEY>'
LASTFM_SECRET_KEY='<LASTFM_SECRET_KEY>'

GOOGLE_MAPS_KEY='<GOOGLE_MAPS_KEY>'
GOOGLE_API_KEY='<GOOGLE_API_KEY>'

LAYAR_DEVELOPER_KEY='<LAYAR_DEVELOPER_KEY>'

NVIVO_KEY = '<NVIVO_KEY>'

MAINTITLE=u'AndalucíaPeople'

HAYSTACK_SITECONF = 'andaluciapeople.search_sites'
HAYSTACK_INCLUDE_SPELLING = True
HAYSTACK_SEARCH_ENGINE = 'dummy'
HAYSTACK_XAPIAN_PATH = path.join(BASEDIR, 'xapian_index')

HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 7 }
#HITCOUNT_HITS_PER_IP_LIMIT = 0
#HITCOUNT_EXCLUDE_USER_GROUP = ( 'Editor', )

PREFIX_DEFAULT_LOCALE = False

LOCALE_INDEPENDENT_PATHS = (
    re.compile('^/localeurl/change/'),
    re.compile('^/.*/nvivo/'),
    re.compile('^/.*/eventos/list/'),
    re.compile('^/.*/sitios\.json/.*'),
)

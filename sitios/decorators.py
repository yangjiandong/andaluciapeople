# -*- coding: utf-8 -*-
'''
    andaluciapeople.com
    Copyright (C) 2010  Manuel Martín Salvador <draxus@gmail.com>

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
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

LISTA_CIUDADES_SLUG = ['almeria',
    'cadiz',
    'cordoba',
    'granada',
    'huelva',
    'jaen',
    'malaga',
    'sevilla'
]

LISTA_CIUDADES = [u'Almería',
    u'Cádiz',
    u'Córdoba',
    u'Granada',
    u'Huelva',
    u'Jaén',
    u'Málaga',
    u'Sevilla'
]

def city_session(view_func):
    
    def _decorated(request, ciudad, *args, **kwargs):
        assert hasattr(request, 'session'), "The Django admin requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
        request.session['city_name'] = LISTA_CIUDADES[cod_ciudad-1]
        return view_func(request, ciudad, *args, **kwargs)
    return wraps(view_func)(_decorated)
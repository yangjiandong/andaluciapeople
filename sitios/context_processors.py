# -*- coding: utf-8 -*-
import settings
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

def ip_address(request):
    return {'ip_address': request.META['REMOTE_ADDR']}

def pretitle(request):
    try:
        city_name = request.session['city_name']
        pretitle = "%sPeople" % city_name
    except:
        pretitle = 'AndalucíaPeople'
    return {'pretitle': pretitle}

def google_api_key(request):
    try:
        google_api_key = settings.GOOGLE_API_KEY
    except:
        google_api_key = 'CONFIG YOUR API KEY IN settings'
    return {'google_api_key': google_api_key}
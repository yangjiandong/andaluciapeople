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

from andaluciapeople.sitios.models import Sitio
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

def add_sitio(request):
    return render_to_response(
        "admin/sitios/sitio/add_form.html",
        RequestContext(request, {}),
    )
add_sitio = staff_member_required(add_sitio)

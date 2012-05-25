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

from django.contrib.sitemaps import Sitemap
from andaluciapeople.sitios.models import *
from localeurl.utils import locale_url
 
class SitioSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def __init__(self, language):
        self.language = language
    
    def items(self):
        return Sitio.objects.all()
    
    def lastmod(self, obj):
        return obj.fecha
    
    def location(self, obj):
        return locale_url(obj.get_absolute_url(), self.language)

class UsuarioSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def __init__(self, language):
        self.language = language
    
    def items(self):
        return DatosUsuario.objects.all()
    
    def lastmod(self, obj):
        return obj.user.last_login
    
    def location(self, obj):
        return locale_url(obj.get_absolute_url(), self.language)

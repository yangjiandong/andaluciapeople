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

from haystack import site
from sitios.models import Sitio
from django.contrib.auth.models import User
from haystack.indexes import SearchIndex
from haystack.fields import CharField, IntegerField, MultiValueField

class SitioIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    ciudad = IntegerField(model_attr='ciudad', faceted=True)
    tipo = MultiValueField()
    tags = MultiValueField()

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Sitio.objects.all()
    
    def prepare_tipo(self, obj):
        return [tipo.tipo for tipo in obj.tipo.all()]
    
    def prepare_tags(self, obj):
        return [tag.tag.tag for tag in obj.get_tags()]

class UserIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return User.objects.all()
    
site.register(Sitio, SitioIndex)
#site.register(User, UserIndex)
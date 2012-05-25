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

from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from andaluciapeople.sitios.models import Sitio, Comentario, Foto

LISTA_CIUDADES = [ u'Almería',
			  	   u'Cádiz',
				   u'Córdoba',
			  	   u'Granada',
			  	   u'Huelva',
			  	   u'Jaén',
			  	   u'Málaga',
			  	   u'Sevilla'
				 ]

LISTA_CIUDADES_SLUG = [ 'almeria',
						'cadiz',
						'cordoba',
						'granada',
						'huelva',
						'jaen',
						'malaga',
						'sevilla'
					  ]
				
class Ciudad:
	def __init__(self, slug):
		self.slug = slug
		i = LISTA_CIUDADES_SLUG.index(slug)
		self.nombre = LISTA_CIUDADES[i]
		self.id = i+1
	
	def get_absolute_url(self):
		return '/%s/' % (self.slug)
	
class FeedSitios(Feed):
    # http://docs.djangoproject.com/en/dev/ref/contrib/syndication/#a-complex-example
    #title_template = "sitios_title.html"
    #description_template = "sitios_description.html"

    def get_object(self, campos):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(campos) != 1:
            raise ObjectDoesNotExist
        obj = Ciudad(campos[0])
        return obj

    def title(self, obj):
        return u"andaluciapeople.com | Últimos sitios de %s" % (obj.nombre)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return u"Últimos sitios de %s añadidos en andaluciapeople.com" % (obj.nombre)

    def items(self, obj):
       return Sitio.objects.filter(ciudad=obj.id).order_by('-id')[:5]
    
    def item_link(self, item):
    	return item.get_absolute_url()

class FeedComentarios(Feed):
    #title_template = "comentarios_title.html"
    description_template = "comentarios_description.html"

    def get_object(self, campos):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(campos) != 1:
            raise ObjectDoesNotExist
        obj = Ciudad(campos[0])
        return obj

    def title(self, obj):
        return u"andaluciapeople.com | Últimos comentarios de %s" % (obj.nombre)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return u"Últimos comentarios en sitios de %s" % (obj.nombre)

    def items(self, obj):
       return Comentario.objects.filter(sitio__ciudad=obj.id).order_by('-id')[:5]
    
    def item_link(self, item):
    	return item.get_absolute_url()

class FeedFotos(Feed):
    #title_template = "fotos_title.html"
    description_template = "fotos_description.html"

    def get_object(self, campos):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(campos) != 1:
            raise ObjectDoesNotExist
        obj = Ciudad(campos[0])
        return obj

    def title(self, obj):
        return u"andaluciapeople.com | Últimas fotos de %s" % (obj.nombre)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return u"Últimas fotos de sitios de %s" % (obj.nombre)

    def items(self, obj):
       return Foto.objects.filter(sitio__ciudad=obj.id).order_by('-id')[:5]
    
    def item_link(self, item):
    	return "/%s/sitio/%s/" % (LISTA_CIUDADES_SLUG[item.sitio.ciudad-1], item.sitio.slug)

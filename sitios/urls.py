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
from django.views.generic.simple import redirect_to
from sitios.models import Tipo
from sitios.feeds import FeedSitios, FeedComentarios, FeedFotos
from sitios.sitemaps import SitioSitemap, UsuarioSitemap

ciudades = "almeria|cadiz|cordoba|granada|huelva|jaen|malaga|sevilla"
campos = "nombre|zona|localidad|rank"
lista_tipos = [item.slug for item in Tipo.objects.all()]
tipos = "|".join(lista_tipos)
feed_dict = {
    'sitios': FeedSitios,
    'comentarios': FeedComentarios,
    'fotos': FeedFotos
}
sitemaps = {
    'sitios': SitioSitemap('es-es'),
    'sitios-en': SitioSitemap('en'),
    'usuarios': UsuarioSitemap('es-es'),
    'usuarios-en': UsuarioSitemap('en'),
}

urlpatterns = patterns('',
    url(r'^ajax/hit/$', 'hitcount.views.update_hit_count_ajax', name='hitcount_update_ajax'),
    (r'^informe/error/$', 'sitios.views.informar_error'),
    (r'^informe/abuso/$', 'sitios.views.informar_abuso'),
    (r'^register/$', 'sitios.views.register'),
    (r'^forgot/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^forgot/$', 'sitios.views.forgot'),
    (r'^invitacion/enviar/(?P<num>[0-9]+)/$', 'sitios.views.enviar_invitaciones'),
    (r'^invitacion/aceptar/(?P<codigo>[a-zA-Z0-9]+)/$', 'sitios.views.aceptar_invitacion'),
    (r'^invitacion/$', 'sitios.views.invitacion'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'base_login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^profile/$', 'sitios.views.profile'), #redirección a /user/username/
    (r'^voto/save/$', 'sitios.views.guardar_voto'),
    (r'^user/recomendaciones/resultados/$', 'sitios.views.buscar_recomendaciones_usuario'),
    (r'^user/recomendaciones/$', 'sitios.views.recomendaciones_usuario'),
    (r'^user/mensajes/', include('andaluciapeople.messages.urls')),
    (r'^user/ajustes/$', 'sitios.views.ajustes_usuario'),
    (r'^user/ajustes/guardar_pesos/$', 'sitios.views.guardar_pesos'),
    (r'^user/ayuda/$', 'sitios.views.ayuda_usuario'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/comment/(?P<id>[0-9]+)/del/$', 'sitios.views.del_comentario'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/photo/(?P<id>[0-9]+)/del/$', 'sitios.views.del_foto'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/fav/(?P<id>[0-9]+)/add/$', 'sitios.views.add_favorito'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/fav/(?P<id>[0-9]+)/del/$', 'sitios.views.del_favorito'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/add/$', 'sitios.views.add_amigo'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/del/$', 'sitios.views.del_amigo'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/amigos/(?P<page>[0-9]+)/$', 'sitios.views.paginar_amigos'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/fotos/(?P<page>[0-9]+)/$', 'sitios.views.paginar_fotos_usuario'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/comentarios/(?P<page>[0-9]+)/$', 'sitios.views.paginar_comentarios_usuario'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/favoritos/(?P<page>[0-9]+)/$', 'sitios.views.paginar_favoritos_usuario'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/sitios/(?P<page>[0-9]+)/$', 'sitios.views.paginar_sitios_usuario'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/similares/$', 'sitios.views.ver_usuarios_similares'),
    (r'^user/(?P<username>[a-zA-Z0-9_\-\.]+)/$', 'sitios.views.ver_usuario'),
    (r'^usuarios.json/lookup/$', 'sitios.views.json_lookup_usuarios'),
    (r'^usuarios/top/$', 'sitios.views.listar_top_usuarios'),
    (r'^usuarios/ultimos/$', 'sitios.views.listar_ultimos_usuarios'),
    (r'^usuarios/(?P<username>[a-zA-Z0-9_\-\.]+)/$', 'sitios.views.buscar_usuarios'),
    (r'^usuarios/$', 'sitios.views.listar_usuarios'),
    (r'^layar/$', 'sitios.views.buscar_puntos_de_interes'),
    (r'^(?P<ciudad>'+ciudades+')/nochevieja/$', 'sitios.views.especial_nochevieja'),
    (r'^(?P<ciudad>'+ciudades+')/eventos/list/$', 'sitios.views.listar_eventos_rss'),
    (r'^(?P<ciudad>'+ciudades+')/eventos/$', 'sitios.views.listar_eventos'),
    (r'^(?P<ciudad>'+ciudades+')/sitios.json/lat/(?P<lat>(\-)?[0-9]+(\.)[0-9]+)/lng/(?P<lng>(\-)?[0-9]+(\.)[0-9]+)/$', 'sitios.views.buscar_sitios_cercanos_coordenadas'),
    (r'^(?P<ciudad>'+ciudades+')/sitios.json/lookup/$', 'sitios.views.json_lookup_sitios'),
    (r'^(?P<ciudad>'+ciudades+')/sitios.json/random/(?P<num>[0-9]+)/$', 'sitios.views.json_random_sitios'),
    (r'^(?P<ciudad>'+ciudades+')/sitios.json/(?P<tags>[a-z0-9-\+]+)/$', redirect_to, {'url': '/%(ciudad)s/sitios.json/?q=%(tags)s'}),
    (r'^(?P<ciudad>'+ciudades+')/sitios.json/$', 'sitios.views.buscar_sitios_json2'),
    (r'^(?P<ciudad>'+ciudades+')/sitios/top/$', 'sitios.views.listar_top_sitios'),
    (r'^(?P<ciudad>'+ciudades+')/sitios/ultimos/$', 'sitios.views.listar_ultimos_sitios'),
    #(r'^(?P<ciudad>'+ciudades+')/sitios/(?P<slug>'+tipos+')/(?P<orderby>(\-)?('+campos+'))/$', 'sitios.views.listar_sitios_tipo'),
    #(r'^(?P<ciudad>'+ciudades+')/sitios/(?P<slug>'+tipos+')/$', 'sitios.views.listar_sitios_tipo'),
    #(r'^(?P<ciudad>'+ciudades+')/sitios/(?P<tags>[a-z0-9-\+]*)/(?P<orderby>(\-)?('+campos+'))/$', 'sitios.views.buscar_sitios2'),
    (r'^(?P<ciudad>'+ciudades+')/sitios/(?P<tags>[a-z0-9-\+]+)/$', redirect_to, {'url': '/%(ciudad)s/sitios/?q=%(tags)s'}),
    (r'^(?P<ciudad>'+ciudades+')/sitios/$', 'sitios.views.buscar_sitios2'),
    (r'^(?P<ciudad>'+ciudades+')/sitio/add/$', 'sitios.views.add_sitio'),
    (r'^(?P<ciudad>'+ciudades+')/sitio/(?P<slug>[a-z0-9\-]+)/cercanos.json/$', 'sitios.views.buscar_sitios_cercanos'),
    (r'^(?P<ciudad>'+ciudades+')/sitio/(?P<slug_sitio>[a-z0-9\-]+)/del_tag/(?P<slug_tag>[a-z0-9\-]+)/$', 'sitios.views.del_tag'),
    (r'^(?P<ciudad>'+ciudades+')/sitio/(?P<slug>[a-z0-9\-]+)/iframe/(?P<width>[0-9]+)/(?P<height>[0-9]+)/(?P<controls>[0-9]+)/$', 'sitios.views.iframe_sitio'),
    (r'^(?P<ciudad>'+ciudades+')/sitio/(?P<slug>[a-z0-9\-]+)/$', 'sitios.views.ver_sitio'),
    (r'^(?P<ciudad>'+ciudades+')/sitio/add_tag/$', 'sitios.views.add_tag'),
    (r'^(?P<ciudad>'+ciudades+')/mapa/(?P<tags>[a-z0-9\-\+]+)/$', redirect_to, {'url': '/%(ciudad)s/mapa/?q=%(tags)s'}),
    (r'^(?P<ciudad>'+ciudades+')/mapa/$', 'sitios.views.mapa'),
    (r'^(?P<ciudad>'+ciudades+')/iframe/(?P<tags>[a-z0-9\-\+]+)/$', redirect_to, {'url': '/%(ciudad)s/iframe/?q=%(tags)s'}),
    (r'^(?P<ciudad>'+ciudades+')/iframe/$', 'sitios.views.iframe_mapa'),
    (r'^(?P<ciudad>'+ciudades+')/hoteles/$', 'sitios.views.hoteles'),
    (r'^(?P<ciudad>'+ciudades+')/kedin/', 'sitios.views.eventos_kedin'),
    (r'^(?P<ciudad>'+ciudades+')/nvivo/', 'sitios.views.eventos_nvivo'),
    (r'^(?P<ciudad>'+ciudades+')/$', 'sitios.views.index'),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feed_dict}),
    (r'^feeds/$', 'sitios.views.feeds_index'),
    (r'^prensa/$', 'sitios.views.prensa'),
    (r'^publicidad/$', 'sitios.views.publicidad'),
    (r'^blog/', include('andaluciapeople.blogapp.urls')),
    (r'^contacto/', 'sitios.views.contacto'),
    (r'^about/', 'sitios.views.acerca_de'),
    (r'^legal/', 'sitios.views.legal'),
    (r'^licencias/', 'sitios.views.licencias'),
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^ping/', include('andaluciapeople.trackback.urls')),
    (r'^$', 'sitios.views.superindex'),
)

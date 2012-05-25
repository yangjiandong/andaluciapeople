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

from django.contrib import admin
from sitios.models import Tipo, Sitio, SitioPatrocinado, SitioNochevieja,\
    Jerarquia, Etiqueta, ObjetoEtiquetado, Voto, Comentario, Foto, DatosUsuario,\
    PesosTipoJerarquia, Amigo, Invitacion, Banner


class TipoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('tipo',)}
    list_display = ('tipo', 'slug')
    search_fields = ['tipo', 'slug']

class SitioAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    list_display = ('nombre', 'zona', 'get_ciudad', 'user', 'cerrado', 'traslado', 'cambio_nombre', 'incorrecto')
    search_fields = ['nombre', ]
    date_hierarchy = 'fecha'
    list_filter = ('ciudad', 'tipo', 'cerrado', 'traslado', 'cambio_nombre', 'incorrecto')

class SitioPatrocinadoAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'precio')
    search_fields = ['sitio', 'descripcion']

class SitioNocheviejaAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'precio')
    search_fields = ['sitio', 'info']

class JerarquiaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ['nombre',]

class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('tag', 'padre')
    search_fields = ['tag',]
    list_filter = ('padre', )

class ObjetoEtiquetadoAdmin(admin.ModelAdmin):
    list_display = ('tag', 'user', 'sitio', 'fecha')
    search_fields = ['tag__tag', 'user__username', 'sitio__nombre']
    date_hierarchy = 'fecha'

class VotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'sitio', 'get_valoracion', 'fecha')
    search_fields = ['user__username', 'sitio__nombre']
    date_hierarchy = 'fecha'

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'sitio', 'mensaje', 'fecha')
    search_fields = ['user__username', 'sitio__nombre', 'mensaje']
    date_hierarchy = 'fecha'

class FotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'sitio', 'foto', 'fecha')
    search_fields = ['user__username', 'sitio__nombre']
    date_hierarchy = 'fecha'

class DatosUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'sexo', 'nacimiento', 'boletin', 'notificaciones', 'idioma', 'puntos')
    search_fields = ['user__username',]
    list_filter = ('sexo', 'boletin', 'notificaciones')

class PesosTipoJerarquiaAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'jerarquia', 'peso')
    search_fields = ['user__username', 'tipo__slug', 'jerarquia__slug']

class AmigoAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend')
    search_fields = ['user__username',]

class InvitacionAdmin(admin.ModelAdmin):
    list_display = ('email', 'enviada', 'codigo', 'aceptada')
    search_fields = ['email',]

class BannerAdmin(admin.ModelAdmin):
    list_display = ('link', 'img', 'alt', 'posicion', 'get_ciudad', 'activo')
    search_fields = ['link',]

admin.site.register(Tipo, TipoAdmin)
admin.site.register(Sitio, SitioAdmin)
admin.site.register(SitioPatrocinado, SitioPatrocinadoAdmin)
admin.site.register(SitioNochevieja, SitioNocheviejaAdmin)
admin.site.register(Jerarquia, JerarquiaAdmin)
admin.site.register(Etiqueta, EtiquetaAdmin)
admin.site.register(ObjetoEtiquetado, ObjetoEtiquetadoAdmin)
admin.site.register(Voto, VotoAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Foto, FotoAdmin)
admin.site.register(DatosUsuario, DatosUsuarioAdmin)
admin.site.register(PesosTipoJerarquia, PesosTipoJerarquiaAdmin)
admin.site.register(Amigo, AmigoAdmin)
admin.site.register(Invitacion, InvitacionAdmin)
admin.site.register(Banner, BannerAdmin)
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

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
import recommender
import settings
import slughifi
import urllib #@UnresolvedImport
from django.db import connection
import feedparser

fs = FileSystemStorage(location=settings.MEDIA_ROOT)

CH_SEXO = (('H', 'Hombre'),
           ('M', 'Mujer'),
           ('I', 'Indeterminado'),
           )

CH_CIUDAD = ((1, 'Almería'),
             (2, 'Cádiz'),
             (3, 'Córdoba'),
             (4, 'Granada'),
             (5, 'Huelva'),
             (6, 'Jaén'),
             (7, 'Málaga'),
             (8, 'Sevilla'),
             (9, 'Todas')
             )

CH_RANK = (('0', 'Indefinido'),
           ('0.5', 'Muy malo'),
           ('1', 'Malo'),
           ('1.5', 'No demasiado malo'),
           ('2', 'Regular'),
           ('2.5', 'Ni bueno ni malo'),
           ('3', 'Casi bueno'),
           ('3.5', 'Bueno'),
           ('4', 'Muy Bueno'),
           ('4.5', 'Excelente'),
           ('5', 'Perfecto'),
           )

CH_IDIOMA = (('es', 'Español'),
             ('en', 'English'),
             )

CH_ICONO = (('bar.png', 'Bar'),
            ('bowling.png', 'Bolera'),
            ('cinema.png', 'Cine'),
            ('club.png', 'Sala'),
            ('coffee.png', 'Cafetería'),
            ('fastfood.png', 'Comida Rápida'),
            ('pizza.png', 'Pizzería'),
            ('restaurant.png', 'Restaurante'),
            ('restaurantchinese.png', 'Restaurante Chino'),
            ('restaurantjapanese.png', 'Restaurante Japonés'),
            ('theater.png', 'Teatro'),
            )

LISTA_CIUDADES = [u'Almería',
    u'Cádiz',
    u'Córdoba',
    u'Granada',
    u'Huelva',
    u'Jaén',
    u'Málaga',
    u'Sevilla'
]

LISTA_CIUDADES_SLUG = ['almeria',
    'cadiz',
    'cordoba',
    'granada',
    'huelva',
    'jaen',
    'malaga',
    'sevilla'
]

CH_BANNERS = (('webs_amigas', 'Webs amigas'),
              ('eventos_destacados', 'Eventos destacados'),
              ('banner_superior', 'Banner superior')
              )
########
# Tipo #
########
class Tipo(models.Model):
    tipo = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)

    def __unicode__(self):
        return self.tipo

    class Meta:
        ordering = ('tipo', )

    # TODO: sobrecargar la función save (o create) para que se creen los pesos


#########
# Sitio #
#########
class Sitio(models.Model):		
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    direccion = models.CharField(u'Dirección', max_length=100, null=True, blank=True)
    zona = models.CharField(max_length=50)
    ciudad = models.IntegerField(max_length=1, choices=CH_CIUDAD)
    tipo = models.ManyToManyField(Tipo)
    lat = models.FloatField(u'Latitud')
    lng = models.FloatField(u'Longitud')
    telefono = models.CharField(u'Teléfono', max_length=20, null=True, blank=True)
    web = models.URLField(null=True, blank=True)
    lastfm = models.IntegerField(max_length=8, null=True, blank=True)
    patrocinado = models.BooleanField(default=False)
    rank = models.FloatField(default=0)
    num_votos = models.IntegerField(default=0)
    user = models.ForeignKey(User)
    fecha = models.DateTimeField()
    ip = models.IPAddressField(max_length=15, null=True, blank=True)
    cerrado = models.NullBooleanField(null=True, default=False)
    traslado = models.NullBooleanField(null=True, default=False)
    cambio_nombre = models.NullBooleanField(null=True, default=False)
    incorrecto = models.NullBooleanField(null=True, default=False)

    class Meta:
        unique_together = ("slug", "ciudad") # El par (slug, ciudad) debe ser único
        ordering = ('nombre',)

    def get_ciudad(self):
        return LISTA_CIUDADES[self.ciudad-1]
    get_ciudad.admin_order_field = 'ciudad'

    def get_lat_long(self, location):
        key = settings.GOOGLE_API_KEY
        output = "csv"
        location = urllib.quote_plus(location)
        request = "http://maps.google.com/maps/geo?q=%s&output=%s&key=%s" % (location, output, key)
        data = urllib.urlopen(request).read()
        dlist = data.split(',')
        if dlist[0] == '200':
            return "%s, %s" % (dlist[2], dlist[3])
        else:
            return ''

    def sitios_cercanos(self):

        radio = 1 #en kilometros
        cursor = connection.cursor() #@UndefinedVariable
        #TODO Obtener el nombre de la tabla de algún sitio
        #Sentencia extraída de http://code.google.com/apis/maps/articles/phpsqlsearch.html#findnearsql
        cursor.execute("SELECT id, ( 6371 * acos( cos( radians(" + str(self.lat) + ") ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(" + str(self.lng) + ") ) + sin( radians(" + str(self.lat) + ") ) * sin( radians( lat ) ) ) ) AS distance FROM sitios_sitio HAVING distance < " + str(radio) + " ORDER BY distance LIMIT 0 , 20;")

        sitios_ids = [item[0] for item in cursor.fetchall()]
        return Sitio.objects.filter(id__in=sitios_ids).exclude(id=self.id).order_by('?')

    def actualizar_rank(self):
        cursor = connection.cursor() #@UndefinedVariable
        #TODO Obtener el nombre de la tabla de algún sitio
        cursor.execute("SELECT sitio_id, SUM(valoracion), COUNT(*) FROM sitios_voto WHERE sitio_id=%s GROUP BY sitio_id", [self.id])
        row = cursor.fetchone()
        if row is not None:
            sum_votos = row[1]
            num_votos = row[2]
            self.rank = round(2 * sum_votos / num_votos) / 2
            self.num_votos = num_votos
            self.save()

        return self

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return "/%s/sitio/%s/" % (LISTA_CIUDADES_SLUG[self.ciudad-1], self.slug)

    def get_estrellas(self):
        html = '<form class="estrellas" action="/voto/save/" method="post">'
        html += '<input name="sitio" value="' + str(self.id) + '" type="hidden" />'
        html += '<input name="action" value="voto" type="hidden" />'
        star = 0.5
        while star < self.rank:
            html += '<input name="valoracion" type="radio" value="' + str(star) + '"  />'
            star += 0.5

        if self.rank > 0:
            html += '<input name="valoracion" type="radio" value="' + str(star) + '" checked="checked" />'
            star += 0.5

        while star < 5.5:
            html += '<input name="valoracion" type="radio" value="' + str(star) + '"  />'
            star += 0.5

        html += '</form>'
        return html

    def get_tags(self):
        return ObjetoEtiquetado.objects.filter(sitio=self) #limitar en caso de que se necesite

    def eventos(self):
        if self.lastfm > 0:
            f = feedparser.parse('http://ws.audioscrobbler.com/1.0/venue/%s/events.rss' % (self.lastfm))
            return f.entries

        else:
            return []

    def sitios_similares(self):
        return recommender.sitios_similares(self)

    def prediction(self, user):
        return recommender.prediction(self, user)
    
    def get_comentarios_count(self):
        return Comentario.objects.filter(sitio=self).count()
    
    def get_fotos_count(self):
        return Foto.objects.filter(sitio=self).count()

####################
# SitioPatrocinado #
####################
class SitioPatrocinado(models.Model):		
    sitio = models.ForeignKey('Sitio', limit_choices_to={'patrocinado': True}, unique=True)
    #sólo escojo aquellos sitios que ya tienen el fag de patrocinado activo
    descripcion = models.TextField(u'Descripción', null=True, blank=True)
    imagen = models.ImageField(storage=fs, upload_to='sitios/patrocinados', null=True, blank=True)
    icono = models.CharField(max_length=30, choices=CH_ICONO, null=True, blank=True)
    precio = models.FloatField(default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        ordering = ('sitio',)
        verbose_name_plural = "sitios patrocinados"

    def __unicode__(self):
        return self.sitio.nombre + " / " + self.sitio.get_ciudad()
    """
		Sobreescribo el save y el delete porque en la clase Sitio he añadido un flag
		para saber si un sitio está patrocinado o no. De esta manera nos ahorramos meter
		estos datos en la tabla de Sitios, por lo que se supone que será más eficiente
		(habrá muy pocos patrocinados en relación a los no patrocinados).
		El flag tiene sentido a la hora de realizar las búsquedas, para que no haya que consultar
		siempre dos tablas si no es necesario.
		
		TODO: Habría que controlar que cuando a un sitio se le pase la fecha de fin, haya que
		desactivar el flag patrocinado en la tabla de Sitios.
	"""
    #def save(self, force_insert=False, force_update=False):
        #super(SitioPatrocinado, self).save(force_insert, force_update)
        #self.sitio.patrocinado = True
        #self.sitio.save()

    def delete(self):
        self.sitio.patrocinado = False
        self.sitio.save()
        super(SitioPatrocinado, self).delete()

####################
# SitioNochevieja #
####################
class SitioNochevieja(models.Model):
    sitio = models.ForeignKey('Sitio', unique=True)
    precio = models.FloatField(default=0)
    info = models.TextField(u'Información', null=True, blank=True)
    imagen = models.ImageField(storage=fs, upload_to='sitios/nochevieja', null=True, blank=True)

    def __unicode__(self):
        return self.sitio.nombre + " / " + self.sitio.get_ciudad()

#############
# Jerarquia #
#############
class Jerarquia(models.Model):
    nombre = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True)

    def __unicode__(self):
        return self.nombre

    def get_tags(self):
        return Etiqueta.objects.filter(padre=self).order_by('tag')

    def slugify(self, nombre):
        return slughifi(nombre)

############
# Etiqueta #
############
class Etiqueta(models.Model):
    tag = models.SlugField(max_length=32, unique=True)
    padre = models.ForeignKey(Jerarquia, blank=True, null=True)

    def __unicode__(self):
        return self.tag

    def slugify(self, tag):
        return slughifi(tag)

####################
# ObjetoEtiquetado #
####################
class ObjetoEtiquetado(models.Model):
    tag = models.ForeignKey(Etiqueta)
    user = models.ForeignKey(User)
    sitio = models.ForeignKey(Sitio)
    fecha = models.DateTimeField()
    ip = models.IPAddressField()

    class Meta:
        unique_together = ("tag", "user", "sitio") # El trío (tag, user, sitio) debe ser único
        verbose_name_plural = "objetos etiquetados"

########
# Voto #
########
class Voto(models.Model):
    user = models.ForeignKey(User)
    sitio = models.ForeignKey(Sitio)
    valoracion = models.FloatField(u'Valoración', choices=CH_RANK)
    fecha = models.DateTimeField()
    ip = models.IPAddressField()

    class Meta:
        unique_together = ("user", "sitio") # El par (user, sitio) debe ser único

    def __unicode__(self):
        return self.user.username + " en " + self.sitio.nombre

    def get_valoracion(self):
        return self.valoracion
    get_valoracion.admin_order_field = 'valoracion'


##############
# Comentario #
##############
class Comentario(models.Model):
    user = models.ForeignKey(User)
    sitio = models.ForeignKey(Sitio)
    mensaje = models.TextField()
    fecha = models.DateTimeField()
    ip = models.IPAddressField()

    def __unicode__(self):
        return self.user.username + " en " + self.sitio.nombre

    def get_absolute_url(self):
        return "/%s/sitio/%s/#comment%s" % (LISTA_CIUDADES_SLUG[self.sitio.ciudad-1], self.sitio.slug, self.id)


    def get_estrellas(self):
        try:
            voto = Voto.objects.get(user=self.user, sitio=self.sitio)
            valor = voto.valoracion
        except:
            valor = 0

        html = '<form class="estrellas">'
        star = 0.5
        while star < valor:
            html += '<input type="radio" value="' + str(star) + '" disabled="disabled"  />'
            star += 0.5

        if valor > 0:
            html += '<input type="radio" value="' + str(star) + '" disabled="disabled" checked="checked" />'
            star += 0.5

        while star < 5.5:
            html += '<input type="radio" value="' + str(star) + '" disabled="disabled"  />'
            star += 0.5

        html += '</form>'
        return html

########
# Foto #
########
class Foto(models.Model):
    user = models.ForeignKey(User)
    sitio = models.ForeignKey(Sitio)
    foto = models.ImageField(storage=fs, upload_to='sitios')
    fecha = models.DateTimeField()
    ip = models.IPAddressField()
    flickr = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username + " en " + self.sitio.nombre

    def get_original_flickr(self):
        url, npi, size = self.foto.url.split("_")
        return url + '_' + npi + '.jpg'

    def get_path(self):
        return 'sitios/' + str(self.sitio.id) + '/' + str(self.foto)
        #return '/media/sitios/' + str(self.sitio.id) + '/' + self.foto

    def delete(self):
        if not self.flickr:
            import os
            try:
                os.remove(settings.MEDIA_ROOT + '/' + self.get_path())
                #TODO Borrar los crops en mini
            except BaseException, e:
                print "Error borrando el archivo" + self.get_path()
                print e

        super(Foto, self).delete()

################
# DatosUsuario #
################
class DatosUsuario(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    web = models.URLField(null=True, blank=True)
    imagen = models.ImageField(storage=fs, upload_to='miembros')
    boletin = models.BooleanField()
    sexo = models.CharField(max_length=1, choices=CH_SEXO, null=True, blank=True)
    nacimiento = models.DateField(null=True, blank=True)
    notificaciones = models.BooleanField()
    idioma = models.CharField(max_length=2, choices=CH_IDIOMA, null=True, blank=True)
    favoritos = models.ManyToManyField(Sitio, null=True, blank=True)
    puntos = models.IntegerField(default=0)
    gustos = models.ManyToManyField(Etiqueta, null=True, blank=True)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return "/user/%s/" % (self.user.username)

    def get_sexo(self):
        for s in CH_SEXO:
            if s[0] == self.sexo:
                return s[1]

    def get_path_imagen(self):
        return "%s" % (self.imagen)

    def similitud(self, user_2, self_votos=None, user_2_votos=None):
        return recommender.similitud(self, user_2, self_votos, user_2_votos)

    def usuarios_similares(self):
        return recommender.usuarios_similares(self)
    
    def sitios_recomendados(self):
        return recommender.sitios_similares(self)
    def sitios_mejor_valorados(self):
        #TODO Comprobar que funciona
        votos_buenos = Voto.objects.filter(user=self.user, valoracion__gte=4)
        lista_sitios = [v.sitio for v in votos_buenos]
        return lista_sitios

    def is_betatester(self):
        try:
            from django.contrib.auth.models import Group
            grupos = self.user.groups.all()
            beta = Group.objects.get(name='Betatesters')
            return (beta in grupos)
        except:
            return False

    def is_facebook_user(self):
        try:
            from oauth_access.models import UserAssociation
            fbuser = UserAssociation.objects.get(user=self.user, service='facebook')
            return True
        except:
            return False

    def perfil_completado(self):
        votos = (Voto.objects.filter(user=self.user).count() >= 5)
        sitios = (Sitio.objects.filter(user=self.user).count() >= 1)
        amigos = (Amigo.objects.filter(user=self.user).count() >= 1)
        comentarios = (Comentario.objects.filter(user=self.user).count() >= 1)
        fotos = (Foto.objects.filter(user=self.user).count() >= 1)
        gustos = (self.gustos.count() >= 1)
        favoritos = (self.favoritos.count() >= 1)
        foto_perfil = (self.imagen.name != 'miembros/default.png')

        pasos = [votos, sitios, amigos, comentarios, fotos, gustos, favoritos, foto_perfil]

        sum = 0.0
        for p in pasos:
            if p:
                sum += 1

        porcentaje = int((sum / len(pasos)) * 100)

        return porcentaje

    def votos_completado(self):
        return not (Voto.objects.filter(user=self.user).count() >= 5)

    def sitios_completado(self):
        return not (Sitio.objects.filter(user=self.user).count() >= 1)

    def amigos_completado(self):
        return not (Amigo.objects.filter(user=self.user).count() >= 1)

    def comentarios_completado(self):
        return not (Comentario.objects.filter(user=self.user).count() >= 1)

    def fotos_completado(self):
        return not (Foto.objects.filter(user=self.user).count() >= 1)

    def gustos_completado(self):
        return not (self.gustos.count() >= 1)

    def favoritos_completado(self):
        return not (self.favoritos.count() >= 1)

    def foto_perfil_completado(self):
        return not (self.imagen.name != 'miembros/default.png')

######################
# PesosTipoJerarquia #
######################
class PesosTipoJerarquia(models.Model):
    user = models.ForeignKey(User)
    tipo = models.ForeignKey(Tipo)
    jerarquia = models.ForeignKey(Jerarquia)
    peso = models.FloatField()

    class Meta:
        unique_together = ("user", "tipo", "jerarquia")

    def __unicode__(self):
        return "Peso de " + self.user.username + " para " + self.jerarquia.slug + " en " + self.tipo.slug

#########
# Amigo #
#########
class Amigo(models.Model):
    user = models.ForeignKey(User, related_name='from')
    friend = models.ForeignKey(User, related_name='to')

    class Meta:
        unique_together = ("user", "friend") # El par (user, friend) debe ser único

    def __unicode__(self):
        return self.friend.username

##############
# Invitacion #
##############
class Invitacion(models.Model):
    email = models.EmailField()
    enviada = models.BooleanField()
    codigo = models.CharField(max_length=10)
    aceptada = models.BooleanField()

    def __unicode__(self):
        return self.email

##########
# Banner #
##########
class Banner(models.Model):
    link = models.URLField(null=True, blank=True)
    img = models.ImageField(storage=fs, upload_to='webs_amigas', null=True, blank=True)
    alt = models.CharField(max_length=255, blank=True)
    posicion = models.CharField(max_length=100, choices=CH_BANNERS, blank=True)
    ciudad = models.IntegerField(max_length=1, choices=CH_CIUDAD)
    activo = models.BooleanField()

    def __unicode__(self):
        return self.link
    
    def get_ciudad(self):
        return LISTA_CIUDADES[self.ciudad-1]
    get_ciudad.admin_order_field = 'ciudad'

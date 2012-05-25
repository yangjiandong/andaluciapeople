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
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import EmailMessage
from django.core.mail import mail_admins
from django.core.mail import send_mail
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.generic import list_detail
from django.views.decorators.cache import cache_page
from haystack.views import basic_search
from haystack.query import SearchQuerySet
from sitios.decorators import city_session
from sitios.models import DatosUsuario, Sitio, Comentario, Foto,\
    SitioPatrocinado, Jerarquia, Tipo, Etiqueta, ObjetoEtiquetado, Voto, Amigo,\
    Banner, PesosTipoJerarquia, Invitacion, SitioNochevieja
from sitios.recommender import generar_pesos_usuario,\
    probabilidades_para_un_sitio, recomendar_sitios_tipo_con_valoracion
from sitios.forms import NewUserForm, NewPassForm, BuscaSitiosForm, VoteForm,\
    CommentForm, FotoForm, TagForm, BuscaUsuariosForm, SitioForm,\
    DatosUsuarioForm, PasswordChangeForm, UsernameChangeForm,\
    RecomiendaSitiosForm, PublicidadForm, ContactForm
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from hitcount.models import HitCount
import random #@UnresolvedImport
import string #@UnresolvedImport
import jsonpickle
import os
import slughifi
import urllib2 #@UnresolvedImport
import datetime

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

DICT_CIUDADES = [('almeria', u'Almería'),
    ('cadiz', u'Cádiz'),
    ('cordoba', u'Córdoba'),
    ('granada', u'Granada'),
    ('huelva', u'Huelva'),
    ('jaen', u'Jaén'),
    ('malaga', u'Málaga'),
    ('sevilla', u'Sevilla')
]

TEXTO_HB = {'almeria': 'HostelBookers ofrece una amplia selección de <a href="http://es.hostelbookers.com/albergues/espana/almeria/" target="_blank">hostales en Almería</a>. Compara precios, lee los comentarios de nuestros clientes y reserva el hostal que más se adapte a tus necesidades al precio mínimo garantizado',
        'cadiz': 'Cádiz es uno de los destinos más populares de Andalucía y cuenta con una amplia gama de alojamiento económico. En HostelBookers podrás encontrar <a href="http://es.hostelbookers.com/albergues/espana/cadiz/" target="_blank">hostales en Cádiz</a> al mejor precio y reservar sin tener que pagar comisión.',
        'cordoba': 'Encuentra y reserva <a href="http://es.hostelbookers.com/albergues/espana/cordoba/" target="_blank">hostales en Córdoba</a> con HostelBookers y aprovéchate de nuestra política de precios mínimos garantizados. Mira las fotos de los hostales y lee los comentarios de nuestros clientes para poder elegir el hostal que mejor se adapte a tus necesidades.',
        'granada': '¿Necesitas encontrar <a href="http://es.hostelbookers.com/albergues/espana/granada/" target="_blank">hostales en Granada</a>? En HostelBookers podrás ver una amplia selección de albergues en Andalucía, leer los comentarios y valoraciones de los clientes y reservar el hostal que más se adapte a tus necesidades sin pagar comisión por reserva.',
        'huelva': 'Huelva ofrece una amplia gama de alojamiento económico para los viajeros que visitan la ciudad. En HostelBookers podrás encontrar una gran selección de <a href="http://es.hostelbookers.com/albergues/espana/huelva/" target="_blank">hostales en Huelva</a> que destacan por su excelente relación calidad-precio y hacer tu reserva sin pagar comisiones.',
        'jaen': '<a href="http://es.hostelbookers.com/" target="_blank">HostelBookers</a> es una de las compañías online líderes en alojamiento de bajo coste. Ofrece una amplia gama de alojamiento incluyendo albergues juveniles, hostales, hoteles, bed &amp; breakfast y apartamentos en más de 3.500 destinos a nivel mundial.',
        'malaga': 'Los <a href="http://es.hostelbookers.com/albergues/espana/malaga/" target="_blank">hostales en Málaga</a> son una de las formas de alojamiento más demandadas por los viajeros que visitan la ciudad. HostelBookers ofrece una amplia gama de albergues en esta popular provincia andaluza y ofrece el precio mínimo garantizado a todos sus clientes.',
        'sevilla': 'HostelBookers, compañía líder en el sector del alojamiento de bajo coste, ofrece una amplia gama de <a href="http://es.hostelbookers.com/albergues/espana/sevilla/" target="_blank">hostales en Sevilla</a>. Podrás leer los comentarios y valoraciones de los clientes, ver fotos y reservar de forma fácil y sencilla el hostal que más se adapte a tus necesidades.'}

TEXTO_HB_EN = {'almeria': 'If you are looking for budget accommodation, HostelBookers offers a lowest price guarantee on <a href="http://www.hostelbookers.com/hostels/spain/almeria/">Almeria hostels</a>. There is no booking fee and you can read reviews from previous guests.',
        'cadiz': 'Save money and book a <a href="http://www.hostelbookers.com/hostels/spain/cadiz/">Cadiz hostel</a> with HostelBookers. Choose from a great range of boutique hostels offering a free breakfast, sunny terraces and plenty of activities where you can meet fellow travellers.',
        'cordoba': 'HostelBookers offer <a href="http://www.hostelbookers.com/hostels/spain/cordoba/">cheap hostels in Cordoba</a> with plenty of character and history. Many are decorated in the Mudejar style and boast roof terraces with views of the city. Private and shared rooms are available from as little as €18 per night.',
        'granada': 'Read reviews by previous guests of <a href="http://www.hostelbookers.com/hostels/spain/granada/">cheap hostels in Granada</a>. HostelBookers offers a number of boutique central hostels with free city tours, games rooms and self-catering facilities from €13 per night.',
        'huelva': 'In <a href="http://www.hostelbookers.com/hostels/spain/">Spain hostels</a> are a cheap solution for travellers looking for budget accommodation in Huelva. HostelBookers offers a lowest price guarantee, no booking fee and customer reviews.',
        'jaen': 'HostelBookers have excellent hostels in Spain for travellers on any budget. Read reviews and view photos before booking your stay.',
        'malaga': 'If you are looking for a <a href="http://www.hostelbookers.com/hostels/spain/">hostel Malaga</a> offers budget accommodation both in the city centre and close to the beach. HostelBookers does not charge a booking fee and provides a lowest price guarantee.',
        'sevilla': 'HostelBookers offers <a href="http://www.hostelbookers.com/hostels/spain/seville/">cheap hostels in Seville</a> with roof terraces, a free breakfast and air-conditioning. Book private or shared rooms from as little as €12 per night and there is absolutely no booking fee.'}

################################################

def profile(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/user/%s/' % (request.user.username))
    else:
        return HttpResponseRedirect('/login/')

################################################

def create_user_profile(user, username, password=None, servicio=None):
    
    datos_user = DatosUsuario(user=user, boletin=True, notificaciones=True, imagen='miembros/default.png')
    datos_user.save()
    
    generar_pesos_usuario(user)
    
    try:
        asunto = _(u'AndaluciaPeople.com - Datos de tu cuenta')
        if password:
            mensaje = _(u'Hola %(user)s!\nGracias por registrarte en AndaluciaPeople.com. Tus datos de acceso son:\n* Usuario: %(user)s\n* Contraseña: %(password)s\nPuedes acceder a tu cuenta en http://andaluciapeople.com/login/') % {'user': username, 'password': password}
        else: 
            mensaje = _(u'Hola %(user)s!\nGracias por registrarte en AndaluciaPeople.com. Te has registrado usando tu cuenta de %(servicio)s\nPuedes acceder a tu cuenta en http://andaluciapeople.com/login/') % {'user': username, 'servicio': servicio}
        send_mail(asunto, mensaje, settings.EMAIL, [user.email,])
    except:
        pass
    
    try:
        asunto = _(u'AndaluciaPeople.com - Nuevo usuario registrado')
        mensaje = u'http://andaluciapeople.com/user/%s' % (user.username)
        mail_admins(asunto, mensaje)
    except:
        pass
    
    return datos_user
    
def register(request):
    referer = request.META.get("HTTP_REFERER", "")
    referer = referer.replace(settings.BASEURL, '/')
    
    
    error = None
    registrado = False
    if request.method == 'POST':
        if settings.DEBUG: print "Registrando usuario"
        if settings.DEBUG: print request.POST
        form = NewUserForm(request.POST)
        if form.is_valid():
            if settings.DEBUG: print "Formulario correcto"
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                new_user.save()
                if settings.DEBUG: print "Registrando usuario"
                create_user_profile(new_user, username, password=password)
                if settings.DEBUG: print "Datos de usuario creados correctamente"
                registrado = True
            except BaseException, e:
                error = str(e)
                if settings.DEBUG: print error
        else:
            error = _("Comprueba que todos los campos del formulario son correctos")
            registrado = False
    else:
        form = NewUserForm()
    
    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    
    #form_login = AuthenticationForm()    
    
    c = {'title': _(u'Registro'),
        'form': form,
        #'form_login': form_login,
        'ciudad': ciudad,
        'registrado': registrado,
        'error': error,
        'next': request.GET.get("next", referer),
    }

    t = get_template('register.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def register_privado(request, mobile=False):

    if request.user.is_authenticated():
        try:
            ciudad = request.session['ciudad']
        except:
            ciudad = 'granada'
        return HttpResponseRedirect('/%s/' % (ciudad))

    next = request.REQUEST.get('next', '')

    form_login = AuthenticationForm()

    c = {'title': _(u'Registro'),
        'form_login': form_login,
        'next': next,
    }

    if mobile:
        t = get_template('mobile/register_privado.html')
    else:
        t = get_template('register_privado.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def forgot(request):

    if request.method == 'POST':
        form = NewPassForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return HttpResponseRedirect('/forgot/done/')
            except:
                return HttpResponse(_(u'Hubo un error al enviar el correo, inténtelo más tarde.'))
        else:
            return HttpResponse(_(u'Hubo un error, comprueba que el email es correcto.'))

    form = NewPassForm()
    c = {'title': _(u'Reestablecer contraseña'),
        'form': form,
    }
    t = get_template('registration/password_reset_form.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

'''
OBSOLETE
@city_session
def listar_sitios(request, ciudad, mobile=False):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    
    if request.method == 'POST':
        busca_sitios_form = BuscaSitiosForm(request.POST)
        if busca_sitios_form.is_valid():
            return HttpResponseRedirect(busca_sitios_form.cleaned_data['s'].replace(" ", "+"))
	
    if request.method == 'GET' and request.GET.has_key('s'):
        s = slughifi.slughifi(request.GET.get('s', ''))
        return HttpResponseRedirect(s.replace("-", "+"))
	
    c = {'title': _(u'Búsqueda de sitios'),
        'user': request.user,
        'ciudad': ciudad,
        'busca_sitios_form': BuscaSitiosForm(),
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        'sitios_populares': Sitio.objects.filter(ciudad=cod_ciudad).order_by('-num_votos', '-rank')[:5],
        'ultimos_sitios': Sitio.objects.filter(ciudad=cod_ciudad).order_by('-id')[:5],
        'sitios_patrocinados': Sitio.objects.filter(ciudad=cod_ciudad, patrocinado=True),
        }
	
    try:
        c['betatester'] = DatosUsuario.objects.get(user=request.user).is_betatester()
    except:
        pass
		
    if mobile:
        c['sitio_list'] = ''
        t = get_template('mobile/sitios/sitio_list.html')
    else:
        t = get_template('sitios/sitio_list.html')

    sitios = Sitio.objects.filter(ciudad=cod_ciudad).order_by('nombre')
    paginator = Paginator(sitios, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        sitios = paginator.page(page)
    except (EmptyPage, InvalidPage):
        sitios = paginator.page(paginator.num_pages)
    
    c['sitios'] = sitios
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)
'''
################################################
'''
OBSOLETE
@city_session
def listar_sitios_tipo(request, ciudad, slug, orderby='nombre', mobile=False):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    
    if request.method == 'POST':
        busca_sitios_form = BuscaSitiosForm(request.POST)
        if busca_sitios_form.is_valid():
            return HttpResponseRedirect(busca_sitios_form.cleaned_data['s'].replace(" ", "+"))
	
    ciudad_unicode = LISTA_CIUDADES[cod_ciudad-1]
    tipo = Tipo.objects.get(slug=slug)
	
    if tipo.tipo == 'Bar':
        tipo_plural = 'Bares'
    else:
        tipo_plural = tipo.tipo + 's'
	
    title = _(u'%(tipo)s de %(ciudad)s') % {'tipo': tipo_plural, 'ciudad': ciudad_unicode}
	
    c = {'title': title,
        'user': request.user,
        'ciudad': ciudad,
        'busca_sitios_form': BuscaSitiosForm(),
        'tags': slug,
        'orderby': orderby,
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        }
	
    if mobile:
        c['tipos'] = ''
        template_name = 'mobile/sitios/sitio_list.html'
    else:
        template_name = 'sitios/sitio_list.html'
	
    return list_detail.object_list(request,
                                   queryset=Sitio.objects.filter(ciudad=cod_ciudad, tipo=tipo).order_by(orderby),
                                   allow_empty=True,
                                   paginate_by=20,
                                   template_object_name='sitio',
                                   template_name=template_name,
                                   extra_context=c)
'''
################################################

@city_session
def listar_top_sitios(request, ciudad, mobile=False):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    
    c = {'title': _(u'Mejores sitios'),
        'user': request.user,
        'ciudad': ciudad,
        }

    if mobile:
        template_name = 'mobile/sitios/sitio_list.html'
    else:
        template_name = 'sitios/sitio_list.html'

    return list_detail.object_list(request,
                                   queryset=Sitio.objects.filter(ciudad=cod_ciudad).order_by('-num_votos', '-rank'),
                                   allow_empty=True,
                                   paginate_by=20,
                                   template_object_name='sitio',
                                   template_name=template_name,
                                   extra_context=c)
  
################################################

@city_session
def listar_ultimos_sitios(request, ciudad, mobile=False):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    
    c = {'title': _(u'Búsqueda de sitios'),
        'user': request.user,
        'ciudad': ciudad,
        }

    if mobile:
        template_name = 'mobile/sitios/sitio_list.html'
    else:
        template_name = 'sitios/sitio_list.html'

    return list_detail.object_list(request,
                                   queryset=Sitio.objects.filter(ciudad=cod_ciudad).order_by('-id'),
                                   allow_empty=True,
                                   paginate_by=20,
                                   template_object_name='sitio',
                                   template_name=template_name,
                                   extra_context=c)

################################################

@city_session
def buscar_sitios_cercanos(request, ciudad, slug):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    sitio = Sitio.objects.get(slug=slug, ciudad=cod_ciudad)

    sitios_ok = sitio.sitios_cercanos()

    res = []
    for sitio in sitios_ok:
        nombre = sitio.nombre
        slug = sitio.slug
        tipos = [x.tipo for x in sitio.tipo.all()]
        lat = sitio.lat
        lng = sitio.lng
        direccion = sitio.direccion
        zona = sitio.zona
        ciudad = sitio.ciudad
        rank = sitio.rank
        comentarios = Comentario.objects.filter(sitio=sitio).count()
        fotos = Foto.objects.filter(sitio=sitio).count()
        patrocinado = sitio.patrocinado
        if patrocinado:
            logo = SitioPatrocinado.objects.get(sitio=sitio).imagen.url
        else:
            logo = ''

        res.append({"nombre": nombre,
                   "slug": slug,
                   "tipos": tipos,
                   "lat": lat,
                   "lng": lng,
                   "direccion": direccion,
                   "zona": zona,
                   "ciudad": ciudad,
                   "rank": rank,
                   "comentarios": comentarios,
                   "fotos": fotos,
                   "patrocinado": patrocinado,
                   "logo": logo
                   })

    response = HttpResponse()
    response.write(simplejson.dumps(res))
    response['mimetype'] = "text/json"
    return response

################################################

@city_session
def buscar_sitios_cercanos_coordenadas(request, ciudad, lat, lng):

    cursor = connection.cursor() #@UndefinedVariable

    sitios_ids = []

    radio = 1 #en kilometros

    while len(sitios_ids) == 0 and radio < 15:

        #TODO Obtener el nombre de la tabla de algún sitio
        #Sentencia extraída de http://code.google.com/apis/maps/articles/phpsqlsearch.html#findnearsql
        cursor.execute("SELECT id, ( 6371 * acos( cos( radians(" + str(lat) + ") ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(" + str(lng) + ") ) + sin( radians(" + str(lat) + ") ) * sin( radians( lat ) ) ) ) AS distance FROM sitios_sitio HAVING distance < " + str(radio) + " ORDER BY distance LIMIT 0 , 20;")

        sitios_ids = [item[0] for item in cursor.fetchall()]

        radio += 5

    sitios_ok = Sitio.objects.filter(id__in=sitios_ids)

    res = []
    for sitio in sitios_ok:
        nombre = sitio.nombre
        slug = sitio.slug
        tipos = [x.tipo for x in sitio.tipo.all()]
        lat = sitio.lat
        lng = sitio.lng
        direccion = sitio.direccion
        zona = sitio.zona
        ciudad = sitio.ciudad
        rank = sitio.rank
        comentarios = Comentario.objects.filter(sitio=sitio).count()
        fotos = Foto.objects.filter(sitio=sitio).count()
        patrocinado = sitio.patrocinado
        if patrocinado:
            logo = SitioPatrocinado.objects.get(sitio=sitio).imagen.url
        else:
            logo = ''

        res.append({"nombre": nombre,
                   "slug": slug,
                   "tipos": tipos,
                   "lat": lat,
                   "lng": lng,
                   "direccion": direccion,
                   "zona": zona,
                   "ciudad": ciudad,
                   "rank": rank,
                   "comentarios": comentarios,
                   "fotos": fotos,
                   "patrocinado": patrocinado,
                   "logo": logo
                   })

    response = HttpResponse()
    response.write(simplejson.dumps(res))
    response['mimetype'] = "text/json"
    return response

################################################

# Ejemplo de URL
# http://draxus.no-ip.org:8000/layar/?userId=42241049345&developerId=101&developerHash=4a542795f8ca57d1348bfd025831334fb9d1b026&timestamp=1242207092430&layerName=hyves&lat=37.176487&lon=-3.597929&accuracy=350&radius=2500

class PointOfInterest:
    def __init__(self):
        self.actions = []
        self.attribution = ''
        self.distance = 0
        self.id = 0
        self.imageURL = ''
        self.lat = 0
        self.lon = 0
        self.line2 = ''
        self.line3 = ''
        self.line4 = ''
        self.title = ''
        self.type = ''

def buscar_puntos_de_interes(request):

    ####################################
    # LEEMOS LOS PARÁMETROS DE ENTRADA #
    ####################################

    params = request.GET

    userId = params.get('userId', '')					#string
    developerId = params.get('developerId', '')			#string
    developerHash = params.get('developerHash', '')		#string
    timestamp = params.get('timestamp', '')				#integer
    layerName = params.get('layerName', '')				#string
    lat = params.get('lat', '')							#decimal
    lon = params.get('lon', '')							#decimal
    accuracy = params.get('accuracy', '')				#integer
    RADIOLIST = params.get('RADIOLIST', '')				#string optional
    SEARCHBOX = params.get('SEARCHBOX', '')				#string optional
    radius = params.get('radius', '')					#integer (meters)
    CUSTOM_SLIDER = params.get('CUSTOM_SLIDER', '')		#float/integer optional
    pageKey = params.get('pageKey', '')					#string optional

    radius = int(radius) / 1000.0 #para pasarlo a kilometros

    ##########################
    # PROCESAMOS LA PETICIÓN #
    ##########################
    cursor = connection.cursor() #@UndefinedVariable


    #TODO Obtener el nombre de la tabla de algún sitio
    #Sentencia extraída de http://code.google.com/apis/maps/articles/phpsqlsearch.html#findnearsql
    cursor.execute("SELECT id, ( 6371 * acos( cos( radians(" + str(lat) + ") ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(" + str(lon) + ") ) + sin( radians(" + str(lat) + ") ) * sin( radians( lat ) ) ) ) AS distance FROM sitios_sitio HAVING distance < " + str(radius) + " ORDER BY distance LIMIT 0 , 20;")

    sitios_ids_distancia = dict()
    for item in cursor.fetchall():
        sitios_ids_distancia[str(item[0])] = item[1]

    sitios_ids = sitios_ids_distancia.keys()

    queryset = Sitio.objects.filter(id__in=sitios_ids)

    ##########################
    # GENERAMOS LA RESPUESTA #
    ##########################
    hotspots = []
    for sitio in queryset:
        poi = PointOfInterest()
        poi.actions = []
        poi.actions.append({'uri': settings.BASEURL + 'm' + sitio.get_absolute_url(), 'label': _(u'Ver ficha')})
        if sitio.web:
            poi.actions.append({'uri': sitio.web, 'label': _(u'Web oficial')})
        if sitio.telefono:
            poi.actions.append({'uri': 'tel:' + str(sitio.telefono), 'label': _(u'Llamar ahora')})
        poi.attribution = _(u'Ofrecido por AndaluciaPeople.com')
        poi.distance = sitios_ids_distancia[str(sitio.id)]
        poi.id = str(sitio.id)
        poi.imageURL = 'null'
        poi.lat = int(sitio.lat*1000000)
        poi.lon = int(sitio.lng*1000000)
        tipos = ""
        for tipo in sitio.tipo.all():
            tipos += tipo.tipo + " "
        poi.line2 = tipos
        poi.line3 = sitio.direccion + " (" + sitio.zona + ")"
        poi.line4 = _(u'Valoración media: ') + str(sitio.rank)
        poi.title = sitio.nombre
        poi.type = 1
        hotspots.append(poi)

    respuesta = {'hotspots': hotspots,
        'layer': 'andaluciapeople',
        'errorString': 'ok',
        'errorCode': 0,
        'morePages': False,
        'nextPageKey': 'null'}

    response = HttpResponse()
    #json_serializer = serializers.get_serializer("json")()
    #json_serializer.serialize(queryset=queryset, ensure_ascii=False, stream=response)
    #response.write(simplejson.dumps(hotspots))
    response.write(jsonpickle.encode(respuesta))

    response['mimetype'] = "text/json"
    return response

################################################

'''
OBSOLETE
@city_session
def buscar_sitios_json(request, ciudad, tags):
    return buscar_sitios(request, ciudad, tags, json=True)
'''

################################################

@city_session
def buscar_sitios_json2(request, ciudad):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    
    c = {'title': _(u'Búsqueda de sitios'),
        'user': request.user,
        'ciudad': ciudad,
        }
    
    search = basic_search(request, 
                          template='sitios/sitio_list.json', 
                          searchqueryset=SearchQuerySet().filter(ciudad=cod_ciudad).order_by('nombre'), 
                          extra_context=c, 
                          results_per_page=20)
    return search
################################################

@city_session
def buscar_sitios2(request, ciudad):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    
    c = {'title': _(u'Búsqueda de sitios'),
        'user': request.user,
        'ciudad': ciudad,
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        'sitios_populares': Sitio.objects.filter(ciudad=cod_ciudad).order_by('-num_votos', '-rank')[:5],
        #'sitios_hot': [hc.content_object for hc in HitCount.object.order_by('-hits')[:5]],
        'ultimos_sitios': Sitio.objects.filter(ciudad=cod_ciudad).order_by('-id')[:5],
        'sitios_patrocinados': Sitio.objects.filter(ciudad=cod_ciudad, patrocinado=True),
        }
    
    query = request.GET.get('q', None)
    if query:
        c['title'] = _(u'%s en %s' % (query, LISTA_CIUDADES[cod_ciudad-1]))
    
    search = basic_search(request, 
                          template='sitios/sitio_list.html', 
                          searchqueryset=SearchQuerySet().filter(ciudad=cod_ciudad).order_by('nombre').highlight(), 
                          extra_context=c, 
                          results_per_page=20)
    return search

'''
OBSOLETE
@city_session
def buscar_sitios(request, ciudad, tags, json=False, orderby='nombre', mobile=False):

    if request.method == 'POST':
        busca_sitios_form = BuscaSitiosForm(request.POST)
        if busca_sitios_form.is_valid():
            return HttpResponseRedirect(busca_sitios_form.cleaned_data['s'].replace(" ", "+"))

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    lista_tags = tags.split("+")
    lista_stopwords = ['la', 'el', 'los', 'las', 'un', 'una', 'de', 'es', 'y', 'en', 'del', 'para', 'con', 'su', 'ya']
    lista_tags = list(set(lista_tags).difference(set(lista_stopwords)))

    c = {'title': _(u'Búsqueda de sitios'),
        'user': request.user,
        'ciudad': ciudad,
        'busca_sitios_form': BuscaSitiosForm({'s': tags.replace("+", " ")}),
        'tags': tags,
        'search_tags': lista_tags,
        'orderby': orderby,
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        }

    etiquetas = []
    for tag in lista_tags:
        try:
            tags = Etiqueta.objects.filter(tag__icontains=tag)
            for t in tags:
                etiquetas.append(str(t.id))
        except:
            pass

    if len(etiquetas) > 0:
        #print etiquetas
        objs_etiquetados = ObjetoEtiquetado.objects.extra(where=['tag_id IN %s' % repr(etiquetas).replace("[", "(").replace("]", ")").replace("'", "")])

        sitios = []
        for obj in objs_etiquetados:
            sitios.append(str(obj.sitio.id))

        if len(sitios) > 0:
            sitios_ok = Sitio.objects.extra(where=['id IN %s' % repr(sitios).replace("[", "(").replace("]", ")").replace("'", "")]).filter(ciudad=cod_ciudad).order_by(orderby)

            if json:
                res = []
                for sitio in sitios_ok:
                    nombre = sitio.nombre
                    slug = sitio.slug
                    tipos = [x.tipo for x in sitio.tipo.all()]
                    lat = sitio.lat
                    lng = sitio.lng
                    direccion = sitio.direccion
                    zona = sitio.zona
                    ciudad = sitio.ciudad
                    rank = sitio.rank
                    comentarios = Comentario.objects.filter(sitio=sitio).count()
                    fotos = Foto.objects.filter(sitio=sitio).count()
                    patrocinado = sitio.patrocinado
                    if patrocinado:
                        logo = SitioPatrocinado.objects.get(sitio=sitio).imagen.url
                        icono = SitioPatrocinado.objects.get(sitio=sitio).icono
                    else:
                        logo = ''
                        icono = ''

                    res.append({"nombre": nombre,
                               "slug": slug,
                               "tipos": tipos,
                               "lat": lat,
                               "lng": lng,
                               "direccion": direccion,
                               "zona": zona,
                               "ciudad": ciudad,
                               "rank": rank,
                               "comentarios": comentarios,
                               "fotos": fotos,
                               "patrocinado": patrocinado,
                               "logo": logo,
                               "icono": icono
                               })

                response = HttpResponse()
                response.write(simplejson.dumps(res))
                response['mimetype'] = "text/json"
                return response

            if mobile:
                c['sitio_list'] = ''
                t = get_template('mobile/sitios/sitio_list.html')
            else:
                t = get_template('sitios/sitio_list.html')

            sitios = sitios_ok
            paginator = Paginator(sitios, 20)
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
                
            try:
                sitios = paginator.page(page)
            except (EmptyPage, InvalidPage):
                sitios = paginator.page(paginator.num_pages)
            
            c['sitios'] = sitios
            html = t.render(RequestContext(request, c))
            return HttpResponse(html)
        elif json:
            response = HttpResponse()
            response['mimetype'] = "text/json"
            return response

    elif json:
        response = HttpResponse()
        response['mimetype'] = "text/json"
        return response

    if mobile:
        c['tipos'] = ''
        t = get_template('mobile/sitios/sitio_list.html')
    else:
        t = get_template('sitios/sitio_list.html')

    html = t.render(RequestContext(request, c))
    return HttpResponse(html)
'''

################################################

@city_session
def iframe_sitio(request, ciudad, slug, width, height, controls):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    sitio = Sitio.objects.get(ciudad=cod_ciudad, slug=slug)

    c = {'title': sitio.nombre,
        'ciudad': ciudad,
        'slug': slug,
        'width': width,
        'height': height,
        'controls': controls,
        'sitio': sitio,
        'gmaps_key': settings.GOOGLE_MAPS_KEY,
    }

    request.session['ciudad'] = ciudad

    t = get_template('iframe_sitio.html')

    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def guardar_voto(request):

    voto_insertado = False
    voto_error = True
    voto_medio = 0
    num_votos = 0
    msg_error = 'Error'

    if request.method == 'POST' and request.POST['action'] == 'voto':
        vote_form = VoteForm(request.POST)
        if vote_form.is_valid():
            user = request.user
            sitio_id = vote_form.cleaned_data['sitio']
            valoracion = vote_form.cleaned_data['valoracion']
            fecha = datetime.datetime.now()
            ip = request.META['REMOTE_ADDR']
            sitio = Sitio.objects.get(pk=sitio_id)

            # si ha votado anteriormente, eliminamos su voto
            try:
                Voto.objects.get(user=user, sitio=sitio).delete()
            except:
                pass

            nuevo_voto = Voto(user=user, sitio=sitio, valoracion=valoracion, fecha=fecha, ip=ip)
            try:
                nuevo_voto.save()
                sitio = sitio.actualizar_rank()
                voto_insertado = True
                voto_error = False
                voto_medio = sitio.rank
                num_votos = sitio.num_votos
            except BaseException, e:
                msg_error = str(e)
                voto_error = True
        else:
            voto_error = True

    response = HttpResponse()
    response['Cache-Control'] = 'no-cache'
    response['mimetype'] = 'text/json'
    if voto_insertado:
        response.write(simplejson.dumps([{'avg': str(voto_medio), 'votos': str(num_votos)}]))
    else:
        response.write(simplejson.dumps([{'err': msg_error,}]))

    return response


################################################

@city_session	
def ver_sitio(request, ciudad, slug, mobile=False):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    sitio = Sitio.objects.get(ciudad=cod_ciudad, slug=slug)

    c = {'title': sitio.nombre,
        'user': request.user,
        'ciudad': ciudad,
        }

    request.session['ciudad'] = ciudad

    if request.user.is_authenticated():
        datos = DatosUsuario.objects.get(user=request.user)

        c['ha_votado'] = False
        prediccion = 0

        try:
            voto_user = Voto.objects.get(sitio=sitio, user=request.user)
            c['ha_votado'] = True
        except:

            p = probabilidades_para_un_sitio(sitio, request.user)
            prediccion = round(p['media'] * 2) / 2
            if prediccion > 0:
                c['prediccion'] = prediccion
            else:
                c['prediccion'] = 'desconocida'

        if c['ha_votado']:
            valoracion = voto_user.valoracion
        elif prediccion > 0:
            valoracion = prediccion
        else:
            valoracion = 0

        c['vote_form'] = VoteForm(initial={'sitio': sitio.id, 'valoracion': valoracion,})

        c['es_favorito'] = False
        for fav in datos.favoritos.all():
            if fav == sitio:
                c['es_favorito'] = True

        #### Procesamos el formulario de comentarios ####
        if request.method == 'POST' and request.POST['action'] == 'comentario':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                user = request.user
                sitio_id = comment_form.cleaned_data['sitio']
                mensaje = comment_form.cleaned_data['mensaje']
                fecha = datetime.datetime.now()
                ip = request.META['REMOTE_ADDR']

                nuevo_comentario = Comentario(user=user, sitio=Sitio.objects.get(pk=sitio_id), mensaje=mensaje, fecha=fecha, ip=ip)
                nuevo_comentario.save()

                #le damos 1 minipunto por comentar
                datos.puntos += 1
                datos.save()
                c['comentario_insertado'] = True
            else:
                c['comentario_error'] = True
        else:
            comment_form = CommentForm(initial={'sitio': sitio.id})
        c['comment_form'] = comment_form

        #### Procesamos el formulario de fotos ####
        if request.method == 'POST' and request.POST['action'] == 'foto':
            foto_form = FotoForm(request.POST, request.FILES)
            if foto_form.is_valid():
                user = request.user
                sitio_id = foto_form.cleaned_data['sitio']
                fecha = datetime.datetime.now()
                ip = request.META['REMOTE_ADDR']

                fotos = request.FILES.getlist('fotos[]')

                random.seed() #inicializamos la semilla aleatoria
                try:
                    directorio = settings.MEDIA_ROOT + '/sitios/' + str(sitio_id) + '/'
                    if not os.access(directorio, os.F_OK):
                        #si no existe, creamos el directorio
                        os.mkdir(directorio) #por defecto se crea con modo 0777

                    for f in fotos:
                        extension = ''
                        if f.content_type == 'image/gif':
                            extension = '.gif'
                        elif f.content_type == 'image/jpeg':
                            extension = '.jpg'
                        elif f.content_type == 'image/png':
                            extension = '.png'
                        else:
                            raise TypeError, _(u'Formato de archivo incorrecto')

                        aleatorio = random.randint(0, 999)
                        fecha_str = '%s_%s_%s_%s%s%s' % (fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute, fecha.second)
                        filename = '%s_%s%s%s' % (user.username, fecha_str, aleatorio, extension)
                        fullpath = directorio + filename
                        destination = open(fullpath, 'wb+')
                        for chunk in f.chunks():
                            destination.write(chunk)
                        destination.close()

                        nueva_foto = Foto(user=user, sitio=Sitio.objects.get(pk=sitio_id), foto=filename, fecha=fecha, ip=ip)
                        nueva_foto.save()

                        #le damos 1 minipunto por subir una foto
                        datos.puntos += 1
                        datos.save()
                    c['foto_insertada'] = True

                except BaseException, e:
                    print "Error: " + str(e)
                    c['foto_error'] = True
            else:
                c['foto_error'] = True
        else:
            foto_form = FotoForm(initial={'sitio': sitio.id,})
        c['foto_form'] = foto_form

    #### Procesamos el formulario de tags ####
    tag_form = TagForm(initial={'sitio': sitio.id})
    c['tag_form'] = tag_form

    tags = ObjetoEtiquetado.objects.filter(sitio=sitio)
    comentarios = Comentario.objects.filter(sitio=sitio).order_by('-id')
    fotos = Foto.objects.filter(sitio=sitio).order_by('-id')

    rank_form = VoteForm(initial={'sitio': sitio.id, 'valoracion': sitio.rank})
    c['rank_form'] = rank_form

    c['sitio'] = sitio
    c['tags'] = tags
    c['comentarios'] = comentarios
    c['fotos'] = fotos
    c['sitios_similares'] = sitio.sitios_similares()
    c['sitios_cercanos'] = sitio.sitios_cercanos()[:5]
    c['gmaps_key'] = settings.GOOGLE_MAPS_KEY
    c['cerrado'] = sitio.cerrado
    c['traslado'] = sitio.traslado
    c['cambio_nombre'] = sitio.cambio_nombre
    c['incorrecto'] = sitio.incorrecto

    if mobile:
        t = get_template('mobile/base_sitio.html')
    else:
        t = get_template('base_sitio.html')

    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def listar_usuarios(request, mobile=False):

    if request.method == 'POST':
        busca_usuarios_form = BuscaUsuariosForm(request.POST)
        if busca_usuarios_form.is_valid():
            return HttpResponseRedirect(busca_usuarios_form.cleaned_data['s'].replace(" ", "+"))

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Usuarios'),
        'user': request.user,
        'ciudad': ciudad,
        'busca_usuarios_form': BuscaUsuariosForm(),
        'mas_activos': DatosUsuario.objects.exclude(user__username='admin').order_by('-puntos')[:5],
        'ultimos_usuarios': User.objects.exclude(username='admin').order_by('-id')[:5],
        }


    if mobile:
        t = get_template('mobile/sitios/user_list.html')
    else:
        t = get_template('sitios/user_list.html')

    usuarios = DatosUsuario.objects.exclude(user__username='admin').order_by('user__username')
    paginator = Paginator(usuarios, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    try:
        usuarios = paginator.page(page)
    except (EmptyPage, InvalidPage):
        usuarios = paginator.page(paginator.num_pages)
    
    c['usuarios'] = usuarios
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def listar_ultimos_usuarios(request, mobile=False):

    if request.method == 'POST':
        busca_usuarios_form = BuscaUsuariosForm(request.POST)
        if busca_usuarios_form.is_valid():
            return HttpResponseRedirect(busca_usuarios_form.cleaned_data['s'].replace(" ", "+"))

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Últimos Usuarios'),
        'user': request.user,
        'ciudad': ciudad,
        'busca_usuarios_form': BuscaUsuariosForm(),
        }

    admin = User.objects.get(username='admin')

    if mobile:
        template_name = 'mobile/sitios/user_list.html'
    else:
        template_name = 'sitios/user_list.html'

    return list_detail.object_list(request,
                                   queryset=DatosUsuario.objects.exclude(user__in=[admin]).order_by('-user__id'),
                                   allow_empty=True,
                                   paginate_by=20,
                                   template_object_name='user',
                                   template_name=template_name,
                                   extra_context=c,
                                   )

################################################

def listar_top_usuarios(request, mobile=False):

    if request.method == 'POST':
        busca_usuarios_form = BuscaUsuariosForm(request.POST)
        if busca_usuarios_form.is_valid():
            return HttpResponseRedirect(busca_usuarios_form.cleaned_data['s'].replace(" ", "+"))

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Usuarios más activos'),
        'user': request.user,
        'ciudad': ciudad,
        'busca_usuarios_form': BuscaUsuariosForm(),
        }

    admin = User.objects.get(username='admin')

    if mobile:
        template_name = 'mobile/sitios/user_list.html'
    else:
        template_name = 'sitios/user_list.html'

    return list_detail.object_list(request,
                                   queryset=DatosUsuario.objects.exclude(user__in=[admin]).order_by('-puntos'),
                                   allow_empty=True,
                                   paginate_by=20,
                                   template_object_name='user',
                                   template_name=template_name,
                                   extra_context=c,
                                   )

################################################

def buscar_usuarios_json(request):
    return buscar_usuarios(request, request.GET['q'], json=True)

################################################

def buscar_usuarios(request, username, json=False, mobile=False):

    if request.method == 'POST':
        busca_usuarios_form = BuscaUsuariosForm(request.POST)
        if busca_usuarios_form.is_valid():
            return HttpResponseRedirect(busca_usuarios_form.cleaned_data['s'].replace(" ", "+"))

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Búsqueda de usuarios'),
        'user': request.user,
        'ciudad': ciudad,
        'busca_usuarios_form': BuscaUsuariosForm({'s': username}),
        'busqueda': username,
        }

    admin = User.objects.get(username='admin')

    if mobile:
        template_name = 'mobile/sitios/user_list.html'
    else:
        template_name = 'sitios/user_list.html'

    if json:
        queryset = User.objects.filter(username__icontains=username).exclude(username='admin').order_by('username')
        response = HttpResponse()
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(queryset=queryset, ensure_ascii=False, stream=response, fields=('username'))
        response['mimetype'] = "text/json"
        return response
    else:
        return list_detail.object_list(request,
                                       queryset=DatosUsuario.objects.filter(user__username__icontains=username).exclude(user__in=[admin]).order_by('user__username'),
                                       allow_empty=True,
                                       paginate_by=20,
                                       template_object_name='user',
                                       template_name=template_name,
                                       extra_context=c,
                                       )

    t = get_template('sitios/user_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def paginar_amigos(request, username, page):

    _amigos_por_pagina = 5

    lim_inf = int(page) * _amigos_por_pagina
    lim_sup = lim_inf + _amigos_por_pagina
    amigos = [amigo.friend for amigo in Amigo.objects.filter(user__username=username).order_by('friend__username')[lim_inf:lim_sup]]
    datos_amigos = DatosUsuario.objects.filter(user__in=amigos).order_by('user__username')

    c = {'amigos': datos_amigos,
        'tucuenta': request.user == User.objects.get(username=username),
    }

    t = get_template('sitios/friends_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def paginar_fotos_usuario(request, username, page):

    user = User.objects.get(username=username)

    _fotos_por_pagina = 8

    lim_inf = int(page) * _fotos_por_pagina
    lim_sup = lim_inf + _fotos_por_pagina
    fotos = Foto.objects.filter(user=user).order_by('-fecha')[lim_inf:lim_sup]

    c = {'fotos': fotos,
        'tucuenta': request.user == user,
    }

    t = get_template('sitios/fotos_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def paginar_comentarios_usuario(request, username, page):

    user = User.objects.get(username=username)

    _comentarios_por_pagina = 10

    lim_inf = int(page) * _comentarios_por_pagina
    lim_sup = lim_inf + _comentarios_por_pagina
    comentarios = Comentario.objects.filter(user=user).order_by('-fecha')[lim_inf:lim_sup]

    c = {'comentarios': comentarios,
        'tucuenta': request.user == user,
    }

    t = get_template('sitios/comentarios_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def paginar_favoritos_usuario(request, username, page):

    user = User.objects.get(username=username)
    datos = DatosUsuario.objects.get(user=user)

    _favoritos_por_pagina = 10

    lim_inf = int(page) * _favoritos_por_pagina
    lim_sup = lim_inf + _favoritos_por_pagina
    favoritos = datos.favoritos.all().order_by('nombre')[lim_inf:lim_sup]

    c = {'favoritos': favoritos,
        'tucuenta': request.user == user,
    }

    t = get_template('sitios/favoritos_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def paginar_sitios_usuario(request, username, page):

    user = User.objects.get(username=username)

    _sitios_por_pagina = 10

    lim_inf = int(page) * _sitios_por_pagina
    lim_sup = lim_inf + _sitios_por_pagina
    sitios = Sitio.objects.filter(user=user).order_by('nombre')[lim_inf:lim_sup]

    c = {'sitios': sitios,
        'tucuenta': request.user == user,
    }

    t = get_template('sitios/enviados_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################
 
def ver_usuario(request, username, mobile=False):
    user = User.objects.get(username=username)
    datos = DatosUsuario.objects.get(user=user)

    amigos = [amigo.friend for amigo in Amigo.objects.filter(user=user).order_by('friend__username')]
    datos_amigos = DatosUsuario.objects.filter(user__in=amigos).order_by('user__username')
    paginator_amigos = Paginator(datos_amigos, 5)

    favoritos = datos.favoritos.all().order_by('nombre')
    paginator_favoritos = Paginator(favoritos, 10)

    sitios = Sitio.objects.filter(user=user).order_by('nombre')
    paginator_sitios = Paginator(sitios, 10)

    comentarios = Comentario.objects.filter(user=user).order_by('-fecha')
    paginator_comentarios = Paginator(comentarios, 10)

    fotos = Foto.objects.filter(user=user).order_by('-fecha')
    paginator_fotos = Paginator(fotos, 8)

    tuamigo = False
    if request.user.is_authenticated():
        for f in Amigo.objects.filter(user=request.user):
            if f.friend == user:
                tuamigo = True
    try:
        is_facebook_user = datos.is_facebook_user()
    except:
        is_facebook_user = False

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': username,
        'user': request.user,
        'ciudad': ciudad,
        'datos': datos,
        'amigos': paginator_amigos.page(1).object_list,
        'num_amigos': len(amigos),
        'tucuenta': request.user == user,
        'is_facebook_user': is_facebook_user,
        'tuamigo': tuamigo,
        'favoritos': paginator_favoritos.page(1).object_list,
        'num_favoritos': len(favoritos),
        'sitios': paginator_sitios.page(1).object_list,
        'num_sitios': len(sitios),
        'comentarios': paginator_comentarios.page(1).object_list,
        'num_comentarios': len(comentarios),
        'fotos': paginator_fotos.page(1).object_list,
        'num_fotos': len(fotos),
        'betatester': datos.is_betatester(),
        }

    if mobile:
        t = get_template('mobile/user/user.html')
    else:
        t = get_template('user/user.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

class NubeTag:
    def __init__(self, id, tag, count):
        self.id = id
        self.tag = tag
        self.count = count

    def cmp(x, y): #@NoSelf
        if x.tag < y.tag:
            return 1
        if x.tag > y.tag:
            return -1
        return 0

################################################

@city_session
def index(request, ciudad, mobile=False):	
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    nombre_ciudad = LISTA_CIUDADES[cod_ciudad-1]
    ultimos_sitios = Sitio.objects.filter(ciudad=cod_ciudad).order_by('-id')[:5]
    ultimos_comentarios = Comentario.objects.filter(sitio__ciudad__exact=cod_ciudad).order_by('-id')[:5]
    ultimos_usuarios = User.objects.order_by('-id')[:5]
    ultimas_fotos = Foto.objects.filter(sitio__ciudad__exact=cod_ciudad).order_by('-id')[:6]
    fotos_aleatorias = Foto.objects.filter(sitio__ciudad__exact=cod_ciudad, flickr=False).order_by('?')[:10]
    sitios_populares = Sitio.objects.filter(ciudad=cod_ciudad).order_by('-num_votos', '-rank')[:5]
    sitio_recomendado = SitioPatrocinado.objects.filter(sitio__ciudad__exact=cod_ciudad).order_by('?')[:1]
    eventos_destacados = Banner.objects.filter(ciudad__in=[cod_ciudad, '9'], posicion='eventos_destacados', activo=True)
    webs_amigas = Banner.objects.filter(ciudad__in=[cod_ciudad, '9'], posicion='webs_amigas', activo=True)

    ################# Para la nube de tags #################

    max_font_size = 30 #TODO Definir en otro sitio
    min_font_size = 15

    cursor = connection.cursor() #@UndefinedVariable
    sql = "SELECT tag_id, e.tag, COUNT(*) c FROM sitios_objetoetiquetado o, sitios_etiqueta e WHERE sitio_id IN (SELECT id FROM sitios_sitio WHERE ciudad=" + str(cod_ciudad) + ") AND tag_id=e.id GROUP BY tag_id ORDER BY c DESC LIMIT 0, 25"
    cursor.execute(sql)

    nube = []
    for row in cursor.fetchall():
        nube.append(NubeTag(row[0], row[1], row[2]))

    if len(nube) > 0:
        nube_max = nube[0].count
        nube_min = nube[-1].count

        spread = nube_max - nube_min
        if spread == 0: #Divide by zero
            spread = 1
        step = (max_font_size - min_font_size) / float(spread)

        for tag in nube:
            tag.count = int(min_font_size + (tag.count - nube_min) * step)

        nube.sort(cmp=NubeTag.cmp, reverse=True)
    ################# FIN Para la nube de tags #################

    if request.LANGUAGE_CODE=='en':
        texto_hb = TEXTO_HB_EN[ciudad]
    else:
        texto_hb = TEXTO_HB[ciudad]

    c = {'title': _(u'Salir por %(nombre_ciudad)s. Bares de tapas, restaurantes, pubs, discotecas y más sitios de %(nombre_ciudad)s') % {'nombre_ciudad': nombre_ciudad},
        'user': request.user,
        'ciudad': ciudad,
        'cod_ciudad': cod_ciudad-1,
        'ultimos_sitios': ultimos_sitios,
        'ultimos_comentarios': ultimos_comentarios,
        'ultimos_usuarios': ultimos_usuarios,
        'ultimas_fotos': ultimas_fotos,
        'sitios_populares': sitios_populares,
        'tags_populares': nube,
        'fotos_aleatorias': fotos_aleatorias,
        'sitio_recomendado': sitio_recomendado,
        'eventos_destacados': eventos_destacados,
        'webs_amigas': webs_amigas,
        'texto_hostelbookers': texto_hb
        }

    
    if mobile:
        t = get_template('mobile/base_index.html')
    else:
        t = get_template('base_index.html')

    html = t.render(RequestContext(request, c))

    request.session['ciudad'] = ciudad
    return HttpResponse(html)

################################################

def superindex(request, mobile=False):	
    next = request.REQUEST.get('next', '')

    form_login = AuthenticationForm()

    c = {'title': _(u'AndalucíaPeople | Bares, restaurantes, pubs, discotecas y más sitios de ocio de Andalucía'),
        'form_login': form_login,
        'next': next,
        'ciudades': DICT_CIUDADES,
        'tipos': Tipo.objects.all(),
    }

    if mobile:
        t = get_template('mobile/base_superindex.html')
    else:
        t = get_template('base_superindex.html')

    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################
@login_required
def add_amigo(request, username):
    if request.method == 'POST' and request.user.is_authenticated():
        if request.user.username == username:
            return HttpResponse(_(u"No puedes hacerte amigo a ti mismo..."), mimetype="text/plain")
        try:
            friend = User.objects.get(username=username)
            nuevo_amigo = Amigo(user=request.user, friend=friend)
            nuevo_amigo.save()

            #Enviar email al amigo
            asunto = _(u'AndaluciaPeople.com - Nueva petición de amistad')
            mensaje = _(u'El usuario %(user)s te ha añadido como amigo.\n\
						  Puedes ver su perfil en http://andaluciapeople.com/user/%(user)s') % {'user': request.user}
            send_mail(asunto, mensaje, settings.EMAIL, [friend.email,])

            #Le damos 5 minipuntos
            datos_user = DatosUsuario.objects.get(user=request.user)
            datos_user.puntos += 5
            datos_user.save()

            return HttpResponse(username + _(u" es tu nuevo amigo"), mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Ya es tu amigo"), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para añadir a un amigo"), mimetype="text/plain")

################################################
@login_required
def del_amigo(request, username):
    if request.method == 'POST' and request.user.is_authenticated():
        try:
            viejo_amigo = Amigo.objects.get(user=request.user, friend=User.objects.get(username=username))
            viejo_amigo.delete()

            # Le quitamos 5 puntos por perder un amigo
            datos_user = DatosUsuario.objects.get(user=request.user)
            datos_user.puntos -= 5
            datos_user.save()

            return HttpResponse(username + _(u" ha dejado de ser tu amigo"), mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Error: ") + str(e), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para eliminar a un amigo"), mimetype="text/plain")

################################################
@login_required
def add_favorito(request, username, id):
    if request.method == 'POST' and request.user.is_authenticated() and request.user.username == username:
        try:
            sitio = Sitio.objects.get(id=id)
            datos = DatosUsuario.objects.get(user=request.user)
            datos.favoritos.add(sitio)

            #le damos 1 minipunto
            datos.puntos += 1
            datos.save() #hay que hacer save después de añadir un favorito
            return HttpResponse(_(u"Añadido a tus favoritos"), mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Error: ") + str(e), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para añadir un sitio a favoritos"), mimetype="text/plain")

################################################
@login_required
def del_favorito(request, username, id):
    if request.method == 'POST' and request.user.is_authenticated() and request.user.username == username:
        try:
            sitio = Sitio.objects.get(id=id)
            datos = DatosUsuario.objects.get(user=request.user)
            datos.favoritos.remove(sitio)
            #le quitamos 1 minipunto por eliminar un favorito
            datos.puntos -= 1
            datos.save() #hay que hacer save cuando se elimina un favorito
            return HttpResponse(_(u"Eliminado de tus favoritos"), mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Error: ") + str(e), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para eliminar un sitio de tus favoritos"), mimetype="text/plain")

################################################
@login_required
def del_comentario(request, username, id):
    if request.method == 'POST' and request.user.is_authenticated() and request.user.username == username:
        try:
            user = User.objects.get(username=username)
            old_comment = Comentario.objects.get(id=id, user=user)
            old_comment.delete()

            #Le quitamos 1 minipunto
            datos_user = DatosUsuario.objects.get(user=user)
            datos_user.puntos -= 1
            datos_user.save()

            return HttpResponse(_(u"El comentario %s ha sido eliminado correctamente") % id, mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Error: ") + str(e), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para eliminar un comentario"), mimetype="text/plain")

################################################
@login_required
def add_tag(request, ciudad):
    if request.method == 'POST' and request.POST['action'] == 'tag':
        tag_form = TagForm(request.POST)
        if tag_form.is_valid():
            user = request.user
            sitio_id = tag_form.cleaned_data['sitio']
            lista_tags = tag_form.cleaned_data['tag'].split(',')
            fecha = datetime.datetime.now()
            ip = request.META['REMOTE_ADDR']

            for tag in lista_tags:
                etiqueta, creada = Etiqueta.objects.get_or_create(tag=slughifi.slughifi(tag))
                try:
                    nuevo_tag = ObjetoEtiquetado(user=user, sitio=Sitio.objects.get(pk=sitio_id), tag=etiqueta, fecha=fecha, ip=ip)
                    nuevo_tag.save()
                except:
                    pass

            return HttpResponse(_(u"Etiqueta insertada correctamente."), mimetype="text/plain")

        else:
            return HttpResponse(_(u"Error: no se pudo guardar la etiqueta."), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para insertar una etiqueta"), mimetype="text/plain")

################################################
@login_required
def del_tag(request, ciudad, slug_sitio, slug_tag):
    if request.method == 'POST' and request.user.is_authenticated():
        try:
            cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
            tag = Etiqueta.objects.get(tag=slug_tag)
            sitio = Sitio.objects.get(slug=slug_sitio, ciudad=cod_ciudad)
            obj_etiquetado = ObjetoEtiquetado.objects.get(tag=tag, user=request.user, sitio=sitio)
            obj_etiquetado.delete()

            return HttpResponse(_(u"La etiqueta %s ha sido eliminada correctamente") % slug_tag, mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Error: ") + str(e), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para eliminar una etiqueta"), mimetype="text/plain")

################################################
@login_required
def del_foto(request, username, id):
    if request.method == 'POST' and request.user.is_authenticated() and request.user.username == username:
        try:
            user = User.objects.get(username=username)
            old_foto = Foto.objects.get(id=id, user=user)
            old_foto.delete()

            #Le quitamos 1 minipunto
            datos_user = DatosUsuario.objects.get(user=user)
            datos_user.puntos -= 1
            datos_user.save()

            return HttpResponse(_(u"La foto %s ha sido eliminada correctamente") % id, mimetype="text/plain")
        except BaseException, e:
            return HttpResponse(_(u"Error: ") + str(e), mimetype="text/plain")
    else:
        return HttpResponse(_(u"Debes estar identificado para eliminar una foto"), mimetype="text/plain")

################################################
@city_session
@login_required
def add_sitio(request, ciudad):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    c = {'title': _(u'Insertar sitio'),
        'user': request.user,
        'ciudad': ciudad,
        'cod_ciudad': cod_ciudad-1,
        'jerarquias': Jerarquia.objects.all(),
        'gmaps_key': settings.GOOGLE_MAPS_KEY,
        }

    if request.user.is_authenticated():
        if request.method == 'POST':
            sitio_form = SitioForm(request.POST)
            if sitio_form.is_valid():
                nombre = sitio_form.cleaned_data['nombre']
                slug = slughifi.slughifi(nombre)
                ciudad = sitio_form.cleaned_data['ciudad']
                zona = sitio_form.cleaned_data['zona']
                direccion = sitio_form.cleaned_data['direccion']
                lat, lng = sitio_form.cleaned_data['location']
                telefono = sitio_form.cleaned_data['telefono']
                web = sitio_form.cleaned_data['web']
                lista_tipos = sitio_form.cleaned_data['tipo']
                lista_tags = request.POST.getlist('tags')

                user = request.user
                fecha = datetime.datetime.now()
                try:
                    ip = request.META['REMOTE_ADDR']
                except:
                    ip = '127.0.0.1'

                print "ip = %s" % ip
                
                c['sitio_error'] = False
                nuevo_sitio = None
                try:
                    nuevo_sitio = Sitio(nombre=nombre, slug=slug, direccion=direccion, ciudad=ciudad, zona=zona, lat=lat, lng=lng, telefono=telefono, web=web, user=user, fecha=fecha, ip=ip)
                    nuevo_sitio.save()

                    try:
                        for t in lista_tipos:
                            nuevo_sitio.tipo.add(t)
                            #tag_slug = slughifi.slughifi(t)
                            tag_slug = t.slug
                            tag, creada = Etiqueta.objects.get_or_create(tag=tag_slug)
                            ObjetoEtiquetado(tag=tag, user=user, sitio=nuevo_sitio, fecha=fecha, ip=ip).save()
                        try:
                            for t in lista_tags:
                                tag, creada = Etiqueta.objects.get_or_create(tag=t)
                                ObjetoEtiquetado(tag=tag, user=user, sitio=nuevo_sitio, fecha=fecha, ip=ip).save()

                            #tags adicionales: nombre, direccion, zona
                            lista_tags2 = [slughifi.slughifi(nombre), slughifi.slughifi(direccion), slughifi.slughifi(zona)]
                            for t in lista_tags2:
                                tag, creada = Etiqueta.objects.get_or_create(tag=t)
                                ObjetoEtiquetado(tag=tag, user=user, sitio=nuevo_sitio, fecha=fecha, ip=ip).save()

                            #Le damos 10 minipuntos
                            datos_user = DatosUsuario.objects.get(user=user)
                            datos_user.puntos += 10
                            datos_user.save()

                            c['sitio_ok'] = True
                            c['sitio'] = Sitio.objects.get(slug=slug, ciudad=ciudad)

                            try:
                                asunto = _(u'%(nombre_ciudad)sPeople.com - Nuevo sitio: %(nombre_sitio)s') % {'nombre_ciudad': LISTA_CIUDADES[cod_ciudad-1], 'nombre_sitio': nombre}
                                mensaje = _(u'El usuario %(user)s ha añadido el sitio http://andaluciapeople.com/%(ciudad)s/sitio/%(slug)s') % {'user': user, 'ciudad': LISTA_CIUDADES_SLUG[ciudad], 'slug': slug}
                                mail_admins(asunto, mensaje)
                            except:
                                pass

                        except BaseException, e:
                            if settings.DEBUG: print e
                            c['sitio_error'] = True
                            c['mensaje_error'] = _(u"Error: comprueba que todos los campos son correctos.")

                    except BaseException, e:
                        if settings.DEBUG: print e
                        c['sitio_error'] = True
                        c['mensaje_error'] = _(u"Error: comprueba que todos los campos son correctos.")

                except BaseException, e:
                    if settings.DEBUG: print e
                    c['sitio_error'] = True
                    c['mensaje_error'] = _(u"Error: comprueba que todos los campos son correctos.")
                    try:
                        old_sitio = Sitio.objects.get(slug=slug, ciudad=ciudad)
                        c['mensaje_error'] = _(u'Error: ya existe un sitio con ese nombre. Ver <a href="/%(ciudad)s/sitio/%(sitio_slug)s/">%(sitio_nombre)s</a>.') % {'ciudad': LISTA_CIUDADES_SLUG[old_sitio.ciudad-1],  'sitio_slug': old_sitio.slug, 'sitio_nombre': old_sitio.nombre}
                    except BaseException, e:
                        pass

                finally:
                    if c['sitio_error']:
                        try:
                            nuevo_sitio.remove() #borramos el sitio si ha habido algún error
                        except:
                            pass
            else:
                c['sitio_error'] = False
            c['sitio_form'] = sitio_form
        else:
            sitio_form = SitioForm(initial={
                                   'ciudad': cod_ciudad,
                                   })

            c['sitio_form'] = sitio_form

    t = get_template('base_add_sitio.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

@city_session
def mapa(request, ciudad, mobile=False):
    
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    c = {'title': _(u'Mapa de sitios'),
        'user': request.user,
        'cod_ciudad': cod_ciudad-1,
        'ciudad': ciudad,
        'busca_sitios_form': BuscaSitiosForm(),
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        'sitios_populares': Sitio.objects.filter(ciudad=cod_ciudad).order_by('-num_votos', '-rank')[:5],
        'ultimos_sitios': Sitio.objects.filter(ciudad=cod_ciudad).order_by('-id')[:5],
        'sitios_patrocinados': Sitio.objects.filter(ciudad=cod_ciudad, patrocinado=True),
        }
    
    if mobile:
        t = 'mobile/base_mapa.html'
    else:
        t = 'base_mapa.html'

    search = basic_search(request, 
                          template=t, 
                          searchqueryset=SearchQuerySet().filter(ciudad=cod_ciudad).order_by('nombre'), 
                          extra_context=c, 
                          results_per_page=10)
    return search

################################################

@city_session
def iframe_mapa(request, ciudad):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    sitios_patrocinados = Sitio.objects.filter(ciudad=cod_ciudad, patrocinado=True)

    c = {'title': _(u'Mapa de sitios'),
        'user': request.user,
        'cod_ciudad': cod_ciudad-1,
        'ciudad': ciudad,
        'sitios_patrocinados': sitios_patrocinados,
        'busca_sitios_form': BuscaSitiosForm(),
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all()
        }

    if request.GET.has_key('q'):
        c['query'] = request.GET['q']
    
    if request.GET.has_key('page'):
        c['page'] = request.GET['page']
    else:
        c['page'] = 1
        
    t = get_template('iframe_sitios.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

'''
OBSOLETE
@city_session
def buscar_mapa(request, ciudad, tags, mobile=False):

    if request.method == 'POST':
        busca_sitios_form = BuscaSitiosForm(request.POST)
        if busca_sitios_form.is_valid():
            s = busca_sitios_form.cleaned_data['s']
            s = slughifi.slughifi(s)
            s = s.replace("-", "+")
            return HttpResponseRedirect('/' + ciudad + '/mapa/' + s)

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    c = {'title': _(u'Resultados en el mapa para %(tags)s') % {'tags': tags},
        'user': request.user,
        'cod_ciudad': cod_ciudad-1,
        'ciudad': ciudad,
        'busqueda': tags,
        'busca_sitios_form': BuscaSitiosForm({'s': tags.replace("+", " ")}),
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        'gmaps_key': settings.GOOGLE_MAPS_KEY,
        }

    if mobile:
        t = get_template('mobile/base_mapa.html')
    else:
        t = get_template('base_mapa.html')

    html = t.render(RequestContext(request, c))
    return HttpResponse(html)
'''
################################################

'''
OBSOLETE
@city_session
def buscar_iframe_mapa(request, ciudad, tags):

    if request.method == 'POST':
        busca_sitios_form = BuscaSitiosForm(request.POST)
        if busca_sitios_form.is_valid():
            s = busca_sitios_form.cleaned_data['s']
            s = slughifi.slughifi(s)
            s = s.replace("-", "+")
            return HttpResponseRedirect('/' + ciudad + '/iframe/' + s)

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    c = {'title': _(u'Resultados en el mapa para %(tags)s') % {'tags': tags},
        'user': request.user,
        'cod_ciudad': cod_ciudad-1,
        'ciudad': ciudad,
        'busqueda': tags,
        'busca_sitios_form': BuscaSitiosForm({'s': tags.replace("+", " ")}),
        'jerarquias': Jerarquia.objects.all(),
        'tipos': Tipo.objects.all(),
        'gmaps_key': settings.GOOGLE_MAPS_KEY,
        }

    t = get_template('iframe_sitios.html')

    html = t.render(RequestContext(request, c))
    return HttpResponse(html)
'''

################################################

@city_session
def listar_eventos(request, ciudad):

    c = {'title': _(u'Eventos, conciertos, actuaciones'),
        'user': request.user,
        'ciudad': ciudad,
        }

    #TODO url = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&format=json&location=%(location)s&api_key=%(key)s' % {'location': ciudad, 'key': settings.LASTFM_API_KEY}

    t = get_template('base_eventos.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

@city_session
def listar_eventos_rss(request, ciudad):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    c = {'ciudad': ciudad,
        }

    return list_detail.object_list(request,
                                   queryset=Sitio.objects.filter(lastfm__isnull=False, ciudad=cod_ciudad).order_by('nombre'),
                                   allow_empty=True,
                                   paginate_by=10,
                                   template_object_name='sitio',
                                   template_name='sitios/evento_list.html',
                                   extra_context=c)

################################################

@city_session
def hoteles(request, ciudad):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    #Códigos de www.sol.com
    PROVINCIA_SOL = {'almeria': '4',
        'cadiz': '11',
        'cordoba': '14',
        'granada': '18',
        'huelva': '21',
        'jaen': '23',
        'malaga': '29',
        'sevilla': '41'}

    #Códigos de www.hostelbookers.com
    PROVINCIA_HB = {'almeria': '7924',
        'cadiz': '2536',
        'cordoba': '1049',
        'granada': '1056',
        'huelva': '7861',
        'jaen': '0', #no tiene hoteles con HB
        'malaga': '2758',
        'sevilla': '2637'}

    c = {'title': _(u'Hoteles en %(nombre_ciudad)s') % {'nombre_ciudad': LISTA_CIUDADES[cod_ciudad-1]},
        'user': request.user,
        'ciudad': ciudad,
        'id_provincia': PROVINCIA_SOL[ciudad],
        'id_province': PROVINCIA_HB[ciudad],
        }

    t = get_template('base_hoteles.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

@city_session
def json_lookup_sitios(request, ciudad):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            # Ignore queries shorter than length 3
            if len(value) > 2:
                model_results = Sitio.objects.filter(slug__icontains=value, ciudad=cod_ciudad)
                results = [x.slug for x in model_results]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='text/json')

################################################

@city_session
def json_random_sitios(request, ciudad, num):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    sitios = Sitio.objects.filter(ciudad=cod_ciudad)
    id_sitios = sitios.values_list('id', flat=True)

    total_sitios = sitios.count()

    num = int(num)
    if total_sitios<num:
        num = total_sitios
    
    rand_ids = random.sample(id_sitios, num)

    random_sitios = sitios.filter(id__in=rand_ids)[:num]
    
    sitios_patrocinados = Sitio.objects.filter(ciudad=cod_ciudad, patrocinado=True)

    todos_juntos = list(random_sitios) + list(sitios_patrocinados)

    res = []
    for sitio in todos_juntos:
        nombre = sitio.nombre
        slug = sitio.slug
        tipos = [x.tipo for x in sitio.tipo.all()]
        lat = sitio.lat
        lng = sitio.lng
        direccion = sitio.direccion
        zona = sitio.zona
        ciudad = sitio.get_ciudad()
        rank = sitio.rank
        comentarios = Comentario.objects.filter(sitio=sitio).count()
        fotos = Foto.objects.filter(sitio=sitio).count()
        patrocinado = sitio.patrocinado
        if patrocinado:
            logo = SitioPatrocinado.objects.get(sitio=sitio).imagen.url
            icono = SitioPatrocinado.objects.get(sitio=sitio).icono
        else:
            logo = ''
            icono = ''

        res.append({"nombre": nombre,
                   "slug": slug,
                   "tipos": tipos,
                   "lat": lat,
                   "lng": lng,
                   "direccion": direccion,
                   "zona": zona,
                   "ciudad": ciudad,
                   "rank": rank,
                   "comentarios": comentarios,
                   "fotos": fotos,
                   "patrocinado": patrocinado,
                   "logo": logo,
                   "icono": icono
                   })

    response = HttpResponse()
    response.write(simplejson.dumps(res))
    response['mimetype'] = "text/json"
    return response

################################################

@city_session
def json_sitios_patrocinados(request, ciudad):

    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1

    sitios_patrocinados = Sitio.objects.filter(ciudad=cod_ciudad, patrocinado=True)

    response = HttpResponse()
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(queryset=sitios_patrocinados, ensure_ascii=False, stream=response)
    response['mimetype'] = "text/json"
    return response

################################################

def json_lookup_usuarios(request):

    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            # Ignore queries shorter than length 3
            if len(value) > 2:
                model_results = User.objects.filter(username__icontains=value).exclude(username='admin').order_by('username')
                results = [x.username for x in model_results]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='text/json')

################################################

def ver_usuarios_similares(request, username):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    user = DatosUsuario.objects.get(user__username=username)
    c = {'title': _(u'Usuarios similares a %(user)s') % {'user': user},
        'user': request.user,
        'ciudad': ciudad,
        'usuarios_similares': user.usuarios_similares(),
        }

    t = get_template('base_similares.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

@login_required
def recomendaciones_usuario(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    user = DatosUsuario.objects.get(user=request.user)
    c = {'title': _(u'Sitios recomendados para %(user)s') % {'user': user},
        'user': request.user,
        'datos': user,
        'ciudad': ciudad,
        'form': RecomiendaSitiosForm(),
        'betatester': user.is_betatester(),
        }

    t = get_template('user/recomendaciones.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

@login_required
def buscar_recomendaciones_usuario(request):
    if request.method != 'GET':
        return HttpResponse("")

    #user = DatosUsuario.objects.get(user=request.user)
    user = request.user
    tipo = request.GET.get('tipo', '')
    ciudad = request.GET.get('ciudad', '')
    zona = request.GET.get('zona', '')
    #valoracion = int(request.GET.get('valoracion', ''))

    recomendaciones = recomendar_sitios_tipo_con_valoracion(tipo, ciudad, zona, user)

    response = HttpResponse()

    if len(recomendaciones) > 0:
        response = HttpResponse(simplejson.dumps(recomendaciones))
    else:
        tipo = Tipo.objects.get(slug=tipo)
        queryset = Sitio.objects.filter(tipo=tipo, ciudad=ciudad).order_by('-num_votos', '-rank')[:10]
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(queryset=queryset, ensure_ascii=False, stream=response)

    response['mimetype'] = "text/json"
    response['encoding'] = "utf-8"
    return response

################################################

def feeds_index(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'AndalucíaPeople | Suscripción RSS'),
        'user': request.user,
        'ciudad': ciudad,
        'ciudades': DICT_CIUDADES,
        }

    t = get_template('base_feeds.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################
@login_required
def mensajeria_usuario(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    user = DatosUsuario.objects.get(user=request.user)
    c = {'title': _(u'Mensajería de %(user)s') % {'user': user},
        'user': request.user,
        'datos': user,
        'ciudad': ciudad,
        }

    t = get_template('user/mensajes.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################
@login_required
def ajustes_usuario(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    user = request.user
    datos = DatosUsuario.objects.get(user=user)

    tipos = Tipo.objects.all()
    pesos = PesosTipoJerarquia.objects.filter(user=user)
    lista_pesos = []
    for tipo in tipos:
        pesos_tipo = pesos.filter(tipo=tipo)
        peso_musica = int(pesos_tipo.get(jerarquia__slug='musica').peso * 100)
        peso_estilo = int(pesos_tipo.get(jerarquia__slug='estilo').peso * 100)
        peso_instalaciones = int(pesos_tipo.get(jerarquia__slug='instalaciones').peso * 100)
        peso_otros = int(pesos_tipo.get(jerarquia__slug='otros').peso * 100)
        lista_pesos.append({
                           'tipo': tipo,
                           'musica': peso_musica,
                           'estilo': peso_estilo,
                           'instalaciones': peso_instalaciones,
                           'otros': peso_otros,
                           'sum': int(peso_musica + peso_estilo + peso_instalaciones + peso_otros)
                           });

    jerarquias = Jerarquia.objects.all()

    c = {'title': _(u'Ajustes de %(user)s') % {'user': user},
        'user': request.user,
        'datos': datos,
        'ciudad': ciudad,
        'jerarquias': jerarquias,
        'betatester': datos.is_betatester(),
        'lista_pesos': lista_pesos,
        }


    datos_form = DatosUsuarioForm({#'username': user.username,
                                   'web': datos.web,
                                   'imagen': datos.imagen,
                                   'boletin': datos.boletin,
                                   'sexo': datos.sexo,
                                   'nacimiento': datos.nacimiento,
                                   'notificaciones': datos.notificaciones,
                                   'idioma': datos.idioma,
                                   #'gustos': lista_gustos,
                                   'action': 'datos',
                                  })
    change_form = PasswordChangeForm(request.user)
    username_change_form = UsernameChangeForm()

    if request.method == 'POST':
        if request.POST['action'] == 'datos':
            
            datos_form = DatosUsuarioForm(request.POST, request.FILES)
            if datos_form.is_valid():
                datos.web = datos_form.cleaned_data['web']
                datos.boletin = datos_form.cleaned_data['boletin']
                datos.sexo = datos_form.cleaned_data['sexo']
                datos.nacimiento = datos_form.cleaned_data['nacimiento']
                datos.notificaciones = datos_form.cleaned_data['notificaciones']
                datos.idioma = datos_form.cleaned_data['idioma']
                datos.save()

                imagen = request.FILES.getlist('imagen')
                if len(imagen) > 0:
                    f = imagen[0]
                    extension = ''
                    if f.content_type == 'image/gif':
                        extension = '.gif'
                    elif f.content_type == 'image/jpeg':
                        extension = '.jpg'
                    elif f.content_type == 'image/png':
                        extension = '.png'
                    else:
                        raise TypeError, 'Formato de archivo incorrecto'

                    if not f.multiple_chunks(): #TODO
                        if datos.imagen and datos.imagen.name != 'miembros/default.png':
                            datos.imagen.delete() #borramos la anterior
                        datos.imagen.save(user.username + extension, f)

                #gustos_nuevos = datos_form.cleaned_data['gustos']
                gustos_nuevos_ids = request.POST.getlist('gustos')
                if len(gustos_nuevos_ids) > 1:
                    gustos_nuevos_ids = repr(tuple([int(u) for u in gustos_nuevos_ids]))
                    gustos_nuevos = Etiqueta.objects.extra(where=['id IN' + gustos_nuevos_ids])
                elif len(gustos_nuevos_ids) == 1:
                    nuevo_gusto = int(gustos_nuevos_ids[0])
                    gustos_nuevos = [Etiqueta.objects.get(id=nuevo_gusto),]
                else:
                    gustos_nuevos = []

                gustos_previos = datos.gustos.all()

                gustos_add = filter(lambda x:x not in gustos_previos, gustos_nuevos)
                gustos_del = filter(lambda x:x not in gustos_nuevos, gustos_previos)
                if len(gustos_add) > 0:
                    for g in gustos_add:
                        datos.gustos.add(g)

                if len(gustos_del) > 0:
                    for g in gustos_del:
                        datos.gustos.remove(g)

                c['datos_ok'] = True
            else:
                c['datos_error'] = True

        #--- cambiar password ---
        elif request.POST['action'] == 'password':
            change_form = PasswordChangeForm(request.user, request.POST)
            if change_form.is_valid():
                change_form.save()
                c['change_ok'] = True
            else:
                c['change_error'] = True
        
        #--- cambiar username ---
        elif request.POST['action'] == 'username':
            username_change_form = UsernameChangeForm(request.POST)
            if username_change_form.is_valid():
                user.username = username_change_form.cleaned_data['username']
                user.save()
                c['username_change_ok'] = True
            else:
                c['username_change_error'] = True

    #------ Formulario de gustos --------
    lista_gustos = [t for t in datos.gustos.all()]
    c['gustos'] = ''

    for j in jerarquias:

        c['gustos'] += '<div class="jerarquias %(slug)s"><strong>%(nombre)s</strong>' % {'slug': j.slug, 'nombre': j.nombre}
        c['gustos'] += '<ul class="tags">'

        for t in j.get_tags():

            checked = ''
            if t in lista_gustos:
                checked = 'checked="checked"'

            c['gustos'] += '<li><label for="id_gustos_%(id)s"><input id="id_gustos_%(id)s" type="checkbox" value="%(id)s" name="gustos" %(checked)s />%(slug)s</label></li>' % {'id': t.id, 'slug': t.tag, 'checked': checked}

        c['gustos'] += '</ul></div>'
    #------ /Formulario de gustos --------

    c['datos_form'] = datos_form
    c['change_form'] = change_form
    c['username_change_form'] = username_change_form
    t = get_template('user/ajustes.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################
@login_required
def guardar_pesos(request):
    try:
        lista_pesos = simplejson.loads(request.POST.get("lista_pesos", ""))
    except BaseException, e:
        return HttpResponse('<span class="error">Hubo un error al guardar los pesos</span>')

    try:
        for peso in lista_pesos:
            (jerarquia_slug, tipo_slug) = peso.split("_")
            objeto = PesosTipoJerarquia.objects.get(user=request.user, tipo__slug=tipo_slug, jerarquia__slug=jerarquia_slug)
            objeto.peso = float(lista_pesos[peso]) / 100.0
            objeto.save()
    except BaseException, e:
        return HttpResponse('<span class="error">Hubo un error al guardar los pesos</span>')

    return HttpResponse('<span class="ok">Pesos guardados correctamente</span>')

################################################
@login_required
def ayuda_usuario(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    user = DatosUsuario.objects.get(user=request.user)
    c = {'title': _(u'Ayuda de usuario'),
        'user': request.user,
        'datos': user,
        'ciudad': ciudad,
        }

    t = get_template('user/ayuda.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def prensa(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Sala de prensa'),
        'user': request.user,
        'ciudad': ciudad,
        'lista_ciudades': LISTA_CIUDADES_SLUG,
        }

    t = get_template('base_prensa.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def publicidad(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Anuncia tu negocio'),
        'user': request.user,
        'ciudad': ciudad,
    }

    if request.method == 'POST':
        form = PublicidadForm(request.POST)
        if form.is_valid():
            print "Formulario válido"
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']

            sitio = form.cleaned_data['sitio']
            ciudad = form.cleaned_data['ciudad']
            zona = form.cleaned_data['zona']
            direccion = form.cleaned_data['direccion']
            lat, lng = form.cleaned_data['location']
            telefono = form.cleaned_data['telefono']
            web = form.cleaned_data['web']
            lista_tipos = form.cleaned_data['tipo']
            tipos = []
            for t in lista_tipos:
                tipos.append(t.slug)
            tarifa = form.cleaned_data['tarifa']
            tiempo = form.cleaned_data['tiempo']

            fecha = datetime.datetime.now()
            ip = request.META['REMOTE_ADDR']

            try:
                subject = u'[andaluciapeople] Contacto publicitario de %s' % nombre

                body_aux = u" Nombre: %(nombre)s\n\r Email: %(email)s\n\r Mensaje: %(mensaje)s\n\r"+\
                u" Sitio: %(sitio)s\n\r Ciudad: %(ciudad)s\n\r Zona: %(zona)s\n\r"+\
                u" Dirección: %(direccion)s\n\r Lat: %(lat)s\n\r Lng: %(lng)s\n\r"+\
                u" Teléfono: %(telefono)s\n\r Web: %(web)s\n\r Tipos: %(tipos)s\n\r"+\
                u" Tarifa: %(tarifa)s\r\n Tiempo: %(tiempo)s\r\n"+\
                u" Fecha: %(fecha)s\r\n IP: %(ip)s\r\n"

                body_array = {'nombre': unicode(nombre),
                'email': unicode(email), 'mensaje': unicode(mensaje), 'sitio': unicode(sitio), 'ciudad': unicode(ciudad),
                'zona': unicode(zona), 'direccion': unicode(direccion), 'lat': unicode(lat), 'lng': unicode(lng),
                'telefono': unicode(telefono), 'web': unicode(web), 'tipos': unicode(tipos),
                'tarifa': unicode(tarifa), 'tiempo': unicode(tiempo), 'fecha': unicode(fecha), 'ip': unicode(ip)}

                body = body_aux % body_array

                from_email = email
                to_email = [settings.EMAIL]

                email_message = EmailMessage(subject, body, from_email, to_email)
                email_message.send()
                c['enviado'] = True
            except BaseException, e:
                if settings.DEBUG:
                    print "[DEBUG] [ERROR] " + str(e)
                c['enviado'] = False
                c['error'] = True

        else:
            c['form'] = form
    else:
        c['form'] = PublicidadForm()

    t = get_template('base_publicidad.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def informar_error(request):
    #TODO Usar un formulario de forms.py
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        email = request.POST.get('email', '')
        mensaje = request.POST.get('mensaje', '')
        sitio_id = int(request.POST.get('sitio_id', ''))
        causa = request.POST.get('causa', '')

        if nombre and email and mensaje and sitio_id:
            try:
                sitio = Sitio.objects.get(id=sitio_id)
                mensaje += '\n\rSitio: http://andaluciapeople.com' + sitio.get_absolute_url()
                mensaje += '\n\rNombre: ' + nombre
                mensaje += '\n\rEmail: ' + email
                send_mail('Informe de error para ' + sitio.nombre, mensaje, email, [settings.EMAIL])

                if causa == 'cerrado':
                    sitio.cerrado = True
                elif causa == 'traslado':
                    sitio.traslado = True
                elif causa == 'cambio_nombre':
                    sitio.cambio_nombre = True
                elif causa == 'incorrecto' or causa == '':
                    sitio.incorrecto = True
                sitio.save()
                
            except BaseException, e:
                return HttpResponse("Hubo un error al enviar el mensaje, inténtelo de nuevo. Error: " + str(e), mimetype="text/plain")

            return HttpResponse("Informe de errores enviado correctamente.", mimetype="text/plain")
        else:
            return HttpResponse("Todos los campos son obligatorios.", mimetype="text/plain")
    else:
        return HttpResponse("Método de envío incorrecto (usar POST).", mimetype="text/plain")

################################################

def informar_abuso(request):
    #TODO Usar un formulario de forms.py
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        email = request.POST.get('email', '')
        mensaje = request.POST.get('mensaje', '')
        comment_id = int(request.POST.get('comment_id', ''))

        if nombre and email and mensaje and comment_id:
            try:
                comentario = Comentario.objects.get(id=comment_id)
                mensaje += '\n\rComentario: http://andaluciapeople.com' + comentario.get_absolute_url()
                mensaje += '\n\rNombre: ' + nombre
                mensaje += '\n\rEmail: ' + email
                send_mail('Informe de abuso para un comentario en ' + comentario.sitio.nombre, mensaje, email, [settings.EMAIL,])
            except BaseException, e:
                return HttpResponse("Hubo un error al enviar el mensaje, inténtelo de nuevo. Error: " + str(e), mimetype="text/plain")

            return HttpResponse("Informe de abuso enviado correctamente.", mimetype="text/plain")
        else:
            return HttpResponse("Todos los campos son obligatorios.", mimetype="text/plain")
    else:
        return HttpResponse("Método de envío incorrecto (usar POST).", mimetype="text/plain")

################################################

def blog(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Blog'),
        'user': request.user,
        'ciudad': ciudad,
        }

    t = get_template('base_blog.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def contacto(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Contacto'),
        'user': request.user,
        'ciudad': ciudad,
    }

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']
            try:
                send_mail('Contacto de %s' % nombre, "Email: %s\n\r %s" % (email, mensaje), email, [settings.EMAIL,])
                c['enviado'] = True
            except:
                c['enviado'] = False
                
        else:
            c['form'] = form
    else:
        c['form'] = ContactForm()

    t = get_template('base_contacto.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def acerca_de(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Acerca de AndalucíaPeople'),
        'user': request.user,
        'ciudad': ciudad,
        }

    t = get_template('base_about.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def legal(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Información legal / Condiciones de uso'),
        'user': request.user,
        'ciudad': ciudad,
        }

    t = get_template('base_legal.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def licencias(request):

    try:
        ciudad = request.session['ciudad']
    except:
        ciudad = 'granada'

    c = {'title': _(u'Licencias'),
        'user': request.user,
        'ciudad': ciudad,
        }

    t = get_template('base_licencias.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def invitacion(request):
    c = {'title': _(u'Invitación'),}

    try:
        email = request.POST.get('email', '')
        random.seed()
        codigo = "".join([random.choice(string.letters + string.digits) for x in range(8)])
        i = Invitacion(email=email, enviada=False, codigo=codigo, aceptada=False)
        i.save()
    except:
        c['error'] = True

    t = get_template('registration/invitacion.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def aceptar_invitacion(request, codigo):
    c = {'title': _(u'Invitación aceptada'),}

    try:
        inv = Invitacion.objects.get(codigo=codigo)
        if inv.enviada:
            inv.aceptada = True
            inv.save()
            return register(request)
        else:
            c['error'] = True
    except BaseException, e:
        c['error'] = True
        c['mensaje'] = str(e)

    t = get_template('registration/invitacion.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################
@login_required
def enviar_invitaciones(request, num):
    c = {'title': _(u'Envío de invitaciones'),}

    try:
        invitaciones = Invitacion.objects.filter(enviada=False)[:num]
        for inv in invitaciones:
            try:
                url = u'http://andaluciapeople.com/invitacion/aceptar/' + inv.codigo + '/'

                asunto = u'Invitación para andaluciapeople.com'

                mensaje = u'''
						  <div align="right"><img src="http://andaluciapeople.com/media/img/letras_andaluciapeople.jpg" alt="" /></div>
						  <p>
						  <b><a href="http://andaluciapeople.com">andalucíaPeople</a></b> es un proyecto 
						  en pleno desarrollo que surge ante la petición social de ampliar la página 
						  de <a href="http://granadapeople.com">granadaPeople.com</a> a todas las 
						  provincias de Andalucía. Esta web no sólo se limita a servir de directorio 
						  de bares, restaurantes, discotecas, pubs, etc. de Andalucía, si no que además 
						  introduce un factor innovador como es el de un <i>sistema de recomendación inteligente</i>.
						  </p>
						  <p>
						  Para <b>crear tu cuenta de usuario</b> entra en <a href="%s">%s</a> y usa el formulario de registro.
						  </p>
						  <p>
						  Recuerda que la web está en fase <i>beta</i>, es decir, habrá cosas que estén sin terminar y otras que no funcionen.
						  Esperamos recibir tus comentarios y sugerencias a través de los distintos formularios, así como que 
						  participes activamente en la web enviando y valorando sitios. ¡Gracias!
						  </p>
						  ''' % (url, url)

                email = EmailMessage(asunto, mensaje, settings.EMAIL, [inv.email],
                                     headers={'From': settings.EMAIL, 'Content-Type': 'text/html'})

                email.content_subtype = "html"

                email.send()

                inv.enviada = True
                inv.save()

            except BaseException, e:
                c['error'] = True
                c['mensaje'] = u'Error enviando la invitación:' + str(e)

    except BaseException, e:
        c['error'] = True
        c['mensaje'] = str(e)

    t = get_template('registration/invitacion.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

def especial_nochevieja(request, ciudad):
    cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad) + 1
    nombre_ciudad = LISTA_CIUDADES[cod_ciudad-1]

    lista = SitioNochevieja.objects.filter(sitio__ciudad=cod_ciudad).order_by('sitio__nombre')

    c = {'title': _(u'Especial nochevieja 2010/2011. Conoce los precios de los pubs, discotecas y cotillones en %(nombre_ciudad)s') % {'nombre_ciudad': nombre_ciudad},
        'sitios': lista,
        'ciudad': ciudad,
        'nombre_ciudad': nombre_ciudad
    }

    t = get_template('base_nochevieja.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

################################################

@cache_page(60 * 30)
def eventos_kedin(request, ciudad):
    c = {'url': "http://%s.kedin.es/feed/events/upcoming/atom" % ciudad,
         'template': 'rss_widget.html'}
    t = get_template('sitios/kedin_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

@cache_page(60 * 30)
def eventos_nvivo(request, ciudad):
    url = "http://www.nvivo.es/api/request.php?api_key=%s&method=city.getEvents&city=%s&format=json" % (settings.NVIVO_KEY, ciudad)
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    result = simplejson.load(f)
    if result and result['status']=='success':
        c = {'eventos': result['response']['gigs']}
    else:
        c = {'eventos': []}
    t = get_template('sitios/nvivo_list.html')
    html = t.render(RequestContext(request, c))
    return HttpResponse(html)

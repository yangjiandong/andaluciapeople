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

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User
from andaluciapeople.sitios.models import *
from andaluciapeople.sitios.forms import *
import datetime
import re
import slughifi
import MySQLdb
import random
import string

username_regex = re.compile('^\w+$')
web_regex = re.compile('^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$')


random.seed()
def random_alphanumeric(size=16):
	return "".join([random.choice(string.letters + string.digits) for x in range(size)])

def sanizar_user(username):
	username = username.replace(' ', '_')
	username = username.replace('-', '')
	username = username.replace('.', '')
	username = username.replace('$', '')
	username = username.replace('@', '')
	username = username.replace('á', 'a')
	username = username.replace('é', 'e')
	username = username.replace('í', 'i')
	username = username.replace('ó', 'o')
	username = username.replace('ú', 'u')
	return username
	
def conectar():
	db=MySQLdb.connect(host='localhost', user='draxus_andpeople', passwd='t4p3And0', db='draxus_andpeople')
	return db.cursor()

def migrar_usuarios(request):
	
	cursor = conectar()
	cursor.execute("SELECT * FROM usuarios")
	
	transformados = [] #nicks que se han tenido que transformar a alfanuméricos

	
	row = cursor.fetchone()
	while row is not None:
		#print row
		if row[0]=='admin':
			user = User.objects.get(username='admin')
		else:
			#Comprobamos que el nombre de usuario es alfanumérico
			username = row[0]
			if username_regex.search(username)==None:
				old_username = username
				username = sanizar_user(username)
				transformados.append(old_username+" -> "+username)
			password = random_alphanumeric(size=10)
			user = User.objects.create_user(username=username,
											password=password, #TODO Enviarlos por correo
											email=row[2]
											)
			user.is_active = True
			user.save()
		
		
		web = row[3]
		if web_regex.search(web)==None:
			web = ''
		
		datos_user = DatosUsuario(user=user,
		      					 web=web,
		      					 imagen='miembros/'+row[4],
		      					 boletin=True,
		      					 sexo=row[7],
		      					 nacimiento=row[8],
		      					 notificaciones=True,
		      					 idioma=row[10])
		datos_user.save()
		row = cursor.fetchone()

	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_usuarios',
		'transformados': transformados,
		}))
	return HttpResponse(html)

def migrar_amigos(request):
	
	cursor = conectar()
	
	cursor.execute("SELECT * FROM amigos")
	for row in cursor.fetchall():
		#print row
		username1 = sanizar_user(row[0])
		username2 = sanizar_user(row[1])
		amigos = Amigo(user=User.objects.get(username=username1),
		      		   friend=User.objects.get(username=username2)
					  )
		amigos.save()

	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_amigos',
		}))
	return HttpResponse(html)

def migrar_sitios(request):
	cursor = conectar()
	cursor.execute("SELECT * FROM sitios")
	for row in cursor.fetchall():
		username = sanizar_user(row[13])
		s = Sitio(id=row[0],
				  nombre=row[1],
				  slug=row[2],
				  direccion=row[3],
				  zona=row[4],
				  ciudad=4,
				  lat=row[6],
				  lng=row[7],
				  web=row[5],
				  rank=row[8],
				  num_votos=row[11],
				  user=User.objects.get(username=username),
				  fecha=datetime.datetime.now(),
				  ip='127.0.0.1'
				  )
		s.save()
		row_tipo = row[12]
		if row_tipo == 'Tapas':
			row_tipo = 'Bar'
		tipo, created = Tipo.objects.get_or_create(tipo=row_tipo, slug=slughifi.slughifi(row_tipo))
		s.tipo.add(tipo)

	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_sitios',
		}))
	return HttpResponse(html)

def migrar_comentarios(request):
	cursor = conectar()
	cursor.execute("SELECT * FROM comentarios")
	for row in cursor.fetchall():
		#print row
		try:
			username = sanizar_user(row[1])
			c = Comentario(id=row[0],
					  	   user=User.objects.get(username=username),
					  	   mensaje=row[2],
					  	   fecha=row[3],
					  	   ip=row[4],
					  	   sitio=Sitio.objects.get(id=row[5])
					  	  )
			c.save()
		except BaseException, e:
			print e
	
	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_comentarios',
		}))
	return HttpResponse(html)

def migrar_votos(request):
	cursor = conectar()
	cursor.execute("SELECT * FROM votos")
	for row in cursor.fetchall():
		#print row
		try:
			username = sanizar_user(row[1])
			v = Voto(id=row[0],
					 user=User.objects.get(username=username),
					 valoracion=row[2],
					 fecha=row[3],
					 ip=row[4],
					 sitio=Sitio.objects.get(id=row[5])
					)
			v.save()
		except BaseException, e:
			print e
	
	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_votos',
		}))
	return HttpResponse(html)

def migrar_fotos(request):
	cursor = conectar()
	cursor.execute("SELECT * FROM fotos")
	flickr_regex = re.compile('^http')
	for row in cursor.fetchall():
		#print row
		try:
			username = sanizar_user(row[1])
			f = Foto(id=row[0],
					 user=User.objects.get(username=username),
					 foto=row[2],
					 fecha=row[3],
					 ip=row[4],
					 sitio=Sitio.objects.get(id=row[5]),
					 flickr=(flickr_regex.search(row[2])!=None)
					)
			f.save()
		except BaseException, e:
			print e
	
	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_fotos',
		}))
	return HttpResponse(html)

def migrar_tags(request):
	cursor = conectar()
	cursor.execute("SELECT * FROM freetags")
	for row in cursor.fetchall():
		print row
		try:
			t = Etiqueta(id=row[0],
						 tag=slughifi.slughifi(row[1])
						)
			t.save()
		except BaseException, e:
			print e
	
	cursor.execute("SELECT * FROM freetagged_objects")
	for row in cursor.fetchall():
		#print row
		try:
			username = sanizar_user(row[1])
			t = ObjetoEtiquetado(tag=Etiqueta.objects.get(id=row[0]),
						 		 user=User.objects.get(username=username),
						 		 sitio=Sitio.objects.get(id=row[2]),
						 		 fecha=row[3],
						 		 ip='127.0.0.1'
								)
			t.save()
		except BaseException, e:
			print e
	
	#eliminamos errores
	cursor.execute("DELETE FROM sitios_objetoetiquetado WHERE tag_id NOT IN (SELECT id FROM sitios_etiqueta)");
	
	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_tags',
		}))
	return HttpResponse(html)

def migrar_eventos(request):
	cursor = conectar()
	cursor.execute("SELECT * FROM eventos_lastfm")
	for row in cursor.fetchall():
		print row
		try:
			s = Sitio.objects.get(id=row[0])
			s.lastfm = row[1];
			s.save()
		except BaseException, e:
			print e
		
	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_eventos',
		}))
	return HttpResponse(html)

def crear_jerarquias(request):
	from os import path
	jerarquia_regex = re.compile('^  \* (?P<jerarquia>\w+)$', re.U)
	etiqueta_regex = re.compile('^    \* (?P<etiqueta>[a-z\ ]+)$', re.U)
	
	f = open(path.join(settings.BASEDIR, 'sitios/categorias_tags.txt'))
	try:
		for line in f:
			res = jerarquia_regex.match(line)
			if res!=None:
				print res.group('jerarquia')
				print "--------------------"
				j,creado = Jerarquia.objects.get_or_create(nombre=res.group('jerarquia'))
				j.save()
			else:
				res = etiqueta_regex.match(line)
				if res!=None:
					tag = res.group('etiqueta').replace(' ', '-')
					print "- "+tag
					e,creado = Etiqueta.objects.get_or_create(tag=tag)
					e.padre = j
					e.save()
	finally:
		f.close()
		
	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN crear_jerarquias',
		}))
	return HttpResponse(html)

def migrar_puntos(request):
	'''
	Los puntos son una nueva feature de andaluciaPeople y se asignan según este baremo:
	* Nuevo sitio = 10 puntos
	* Nuevo amigo = 5 puntos
	* Nuevo comentario = 1 punto
	* Nueva foto = 1 punto
	* Nuevo favorito = 1 punto
	'''
	cursor = conectar()
	
	# ------ SITIOS ------
	cursor.execute("SELECT nick, COUNT(*) FROM sitios GROUP BY nick")
	for row in cursor.fetchall():
		try:
			username = sanizar_user(row[0])
			numsitios = int(row[1])
			puntos = 10*numsitios
			user = DatosUsuario.objects.get(user=User.objects.get(username=username))
			user.puntos += puntos
			user.save()
		except BaseException, e:
			print e
	
	# ------ AMIGOS ------
	cursor.execute("SELECT nick, COUNT(*) FROM amigos GROUP BY nick")
	for row in cursor.fetchall():
		try:
			username = sanizar_user(row[0])
			numamigos = int(row[1])
			puntos = 5*numamigos
			user = DatosUsuario.objects.get(user=User.objects.get(username=username))
			user.puntos += puntos
			user.save()
		except BaseException, e:
			print e

	# ------ COMENTARIOS ------
	cursor.execute("SELECT nick, COUNT(*) FROM comentarios GROUP BY nick")
	for row in cursor.fetchall():
		try:
			username = sanizar_user(row[0])
			numcomentarios = int(row[1])
			puntos = 1*numcomentarios
			user = DatosUsuario.objects.get(user=User.objects.get(username=username))
			user.puntos += puntos
			user.save()
		except BaseException, e:
			print e


	# ------ FOTOS ------
	cursor.execute("SELECT nick, COUNT(*) FROM fotos GROUP BY nick")
	for row in cursor.fetchall():
		try:
			username = sanizar_user(row[0])
			numfotos = int(row[1])
			puntos = 1*numfotos
			user = DatosUsuario.objects.get(user=User.objects.get(username=username))
			user.puntos += puntos
			user.save()
		except BaseException, e:
			print e

	t = get_template('migrar.html')
	html = t.render(Context({
		'fin': 'FIN migrar_puntos',
		}))
	return HttpResponse(html)

# -*- coding: utf-8 -*-
import operator
from math import sqrt
from andaluciapeople.sitios.models import *
from django.db import connection
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

LISTA_CIUDADES_SLUG = [ 'almeria',
						'cadiz',
						'cordoba',
						'granada',
						'huelva',
						'jaen',
						'malaga',
						'sevilla'
					  ]



'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
recommender.generar_usuario('prueba', ['tapas', 'rock', 'terraza', 'servicio-a-domicilio', 'chino'])
'''
def generar_usuario(nick, gustos):
	from andaluciapeople.sitios.models import User, DatosUsuario, Etiqueta
	try:
		user = User(username=nick, email="%s@andaluciapeople.com" % (nick))
		user.set_password("test")
		user.save()
		print "Usuario %s creado correctamente" % (nick)
		
	except BaseException, e:
		print "ERROR creando al usuario %s: %s" % (nick, str(e))
		user = User.objects.get(username=nick)

	try:
		datos_user = DatosUsuario(user=user, boletin=False, notificaciones=False, imagen='miembros/default.png')
		datos_user.save()
		
		for tag in gustos:
			tag_obj = Etiqueta.objects.get(tag=tag)
			datos_user.gustos.add(tag_obj)
		print "DatosUsuario %s creado correctamente" % (nick)
		
	except BaseException, e:
		print "ERROR creando los datos del usuario %s: %s" % (nick, str(e))

'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
recommender.generar_pesos_todos()
'''
def generar_pesos_todos():
	from andaluciapeople.sitios.models import User
	
	print "Generando pesos..."
	users = User.objects.all()
	for user in users:
		try:
		   generar_pesos_usuario(user)
		except BaseException, e:
			print "Error: " + str(e)
	
	print "FIN"
	
def generar_pesos_usuario(user):
	from andaluciapeople.sitios.models import Tipo, Jerarquia, PesosTipoJerarquia
	from recommender_pesos import PESOS_TIPO
	
	tipos = Tipo.objects.all()
	jerarquias = Jerarquia.objects.all()
	
	for tipo in tipos:
		for jerarquia in jerarquias:
			peso = PESOS_TIPO[tipo.slug][jerarquia.slug]
			PesosTipoJerarquia(user=user, tipo=tipo, jerarquia=jerarquia, peso=peso).save()



def generar_votos(nick, num_votos):
	from andaluciapeople.sitios.models import User, Sitio, Voto
	from datetime import datetime
	import random
	try:
		user = User.objects.get(username=nick)
		#nodo_user = NodoPerfilUsuario(user)
	except BaseException, e:
		print "ERROR El usuario %s no existe: %s" % (nick, str(e))
	
	'''
	Cogemos *num_votos* sitios aleatorios y asignamos valoración según los gustos del usuario
	'''
	sitios = Sitio.objects.all().order_by('?')[:num_votos]
	for sitio in sitios:
		probabilidad = probabilidades_para_un_sitio(sitio, user)
		#si no ha encontrado ninguna similaridad, le asignamos un valor aleatorio entre 1 y 5
		if probabilidad[6]<1:
			valoracion = int(round(random.randint(1,4)+random.random()))
		else:
			valoracion = int(round(probabilidad[6]))
		print valoracion
		#voto = Voto(user=user, sitio=sitio, valoracion=probabilidad[6], fecha=datetime.now(), ip='127.0.0.1')



'''
from sitios.models import *; recommender.mae_cobertura_medias('voto_medio', 20)
from sitios.models import *; recommender.mae_cobertura_medias('coseno', 20)
from sitios.models import *; recommender.mae_cobertura_medias('contenido', 20)
from sitios.models import *; recommender.mae_cobertura_medias('colaborativo', 20)
'''
def mae_cobertura_medias(metodo, num):
	from numpy import average,std
	maes = []
	coberturas = []
	
	if metodo=='voto_medio':
	  for i in range(0, num):
	     r = MAE_voto_medio()
	     maes.append(r['mae'])
	     coberturas.append(r['cobertura'])
	
	elif metodo=='coseno':
	  for i in range(0, num):
	     r = MAE_coseno()
	     maes.append(r['mae'])
	     coberturas.append(r['cobertura'])
	     
	elif metodo=='contenido':
	  for i in range(0, num):
	     r = MAE_contenido()
	     maes.append(r['mae'])
	     coberturas.append(r['cobertura'])
	     
	elif metodo=='colaborativo':
	  for i in range(0, num):
	     r = MAE_colaborativo()
	     maes.append(r['mae'])
	     coberturas.append(r['cobertura'])
	    
	mae_media = average(maes)
	mae_std = std(maes)
	cobertura_media = average(coberturas)
	cobertura_std = std(coberturas)
	
	print mae_media, " ", mae_std, " ", cobertura_media, " ", cobertura_std
	


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
user = User.objects.get(username='draxus')
recommender.voto_medio(user)
'''
def voto_medio(user):
	
	cursor = connection.cursor()
	cursor.execute("SELECT AVG(valoracion) FROM sitios_voto WHERE user_id = %s", [user.id])
	row = cursor.fetchone()
	
	return row[0]


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_voto_medio();
'''
def MAE_voto_medio():
	from math import sqrt
	
	res = {}
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()
		
	#buscamos aquellos usuarios que tienen más de x votos
	cursor = connection.cursor()
	cursor.execute("SELECT user_id FROM sitios_voto GROUP BY user_id HAVING COUNT(*)>5")
	
	usuarios = cursor.fetchall()
	
	users_id = repr(tuple([int(u[0]) for u in usuarios]))
	
	votos_total = votos_total.extra(where=['user_id IN '+ users_id])
	
	num_votos_total = votos_total.count()
	
	#Obtenemos un conjunto de votos para test (20% del total)
	num_votos_test = 20*num_votos_total/100
	votos_test = votos_total.order_by('?')[:num_votos_test]
	
	copia_test = votos_test
	
	#Borramos los votos de la base de datos
	for voto in copia_test:
		voto.delete()
	
	try:
	
		cursor.execute("SELECT user_id FROM sitios_voto GROUP BY user_id HAVING COUNT(*)>1")
		usuarios = cursor.fetchall()
		
		users_id = [int(u[0]) for u in usuarios]
				
		votos_test2 = []
		for v in votos_test:
			if int(v.user.id) in users_id:
			  votos_test2.append(v)
			else:
			  v.save()
		
		votos_test = votos_test2
		num_votos_test = len(votos_test)
		
		try:
			#Calculamos la predicción para cada sitio y su diferencia con el real
			mae = 0
			num_sitios_predichos = 0
			
			for voto in votos_test:
				p = voto_medio(voto.user)
				
				if p>0:
					mae += abs(voto.valoracion - p)
					#mae += sqrt(abs(voto.valoracion*voto.valoracion - p*p))
					num_sitios_predichos += 1
					#print voto.valoracion, "\t", p
			
			if num_sitios_predichos>0:
				mae /= num_sitios_predichos
			
			#Calculamos el porcentaje de votos que se ha podido predecir
			coverage = num_sitios_predichos*100/num_votos_test
			
			res = {'entrenamiento': (num_votos_total-num_votos_test),
			        'prueba': num_votos_test,
			        'mae': mae,
			        'cobertura': coverage
			       }
			#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
			#print "MAE = ", mae, " Cobertura = ", coverage, "%"
		
		except BaseException,e:
			print "Error: " + str(e)
	
	except BaseException,e:
		print "Error: " + str(e)
		
	#Volvemos a guardar los votos en la BD
	for voto in votos_test:
		voto.save()

	return res


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_voto_medio2()
'''
def MAE_voto_medio2():
	from math import pow
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()
	num_votos_total = votos_total.count()
	
	try:
		#Calculamos la predicción para cada sitio y su diferencia con el real
		mae = 0
		mse = 0
		num_sitios_predichos = 0
		
		for voto in votos_total:
			
			voto.delete()
			
			p = voto_medio(voto.user)
			
			if p>0:
				mae += abs(voto.valoracion - p)
				mse += pow(abs(voto.valoracion - p), 2)
				num_sitios_predichos += 1
			
			voto.save()
		
		if num_sitios_predichos>0:
			mae /= num_sitios_predichos
			mse /= num_sitios_predichos
						
		#Calculamos el porcentaje de votos que se ha podido predecir
		try:
			coverage = num_sitios_predichos*100/num_votos_total
		except:
			coverage = 0
		
		res = { 'num_votos_total': num_votos_total,
		        'mae': mae,
		        'mse': mse,
		        'cobertura': coverage,
		        'num_sitios_predichos': num_sitios_predichos,
		       }
		#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
		#print "MAE = ", mae, " Cobertura = ", coverage, "%"
	
	except BaseException,e:
		print "Error: " + str(e)


	return res



'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
user = User.objects.get(username='draxus')
evidence = Sitio.objects.get(slug='kirin')
recommender.medida_coseno(evidence, user)
'''
def medida_coseno(evidence, user):
	
	coseno = 0
	
	#Obtenemos las etiquetas que le gustan al usuario
	tags_user = set(DatosUsuario.objects.get(user=user).gustos.all())
	
	#Obtenemos las etiquetas que describen al sitio
	objtags_evidence = ObjetoEtiquetado.objects.filter(sitio=evidence)
	tags_evidence = set()
	for objtag in objtags_evidence:
		tags_evidence.add(objtag.tag)
	
	#Obtenemos las etiquetas que tienen en común		
	tags_comunes = tags_user.intersection(tags_evidence)
	
	#debería ser len(tags_user) pero como pueden ser muchas, pongo sólo las comunes
	producto_raices = (sqrt(len(tags_comunes)) * sqrt(len(tags_evidence)))
	
	if producto_raices>0:
		coseno = len(tags_comunes) / producto_raices
	
	return coseno


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
recommender.MAE_coseno()
'''
def MAE_coseno():
	from math import sqrt
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()

	#Buscamos aquellos usuarios que han rellenado sus gustos
	cursor = connection.cursor()
	cursor.execute("SELECT datosusuario_id FROM sitios_datosusuario_gustos GROUP BY datosusuario_id HAVING COUNT(*)>0")
		
	usuarios = cursor.fetchall()
	
	users_id = repr(tuple([int(u[0]) for u in usuarios]))
	
	votos_total = votos_total.extra(where=['user_id IN '+ users_id])
	num_votos_total = votos_total.count()
	
	#Obtenemos un conjunto de votos para test (20% del total)
	num_votos_test = 20*num_votos_total/100
	votos_test = votos_total.order_by('?')[:num_votos_test]
	copia_test = votos_test
	
	#Borramos los votos de la base de datos
	for voto in copia_test:
		voto.delete()
	
	try:
		#Calculamos la predicción para cada sitio y su diferencia con el real
		mae = 0
		num_sitios_predichos = 0
		
		for voto in votos_test:
			p = 5*medida_coseno(voto.sitio, voto.user) #multiplico por 5 porque es el voto asignado al perfil de usuario
			
			if p>0:
				mae += abs(voto.valoracion - p)
				#mae += sqrt(abs(voto.valoracion*voto.valoracion - p*p))
				num_sitios_predichos += 1
				#print voto.valoracion, "\t", p
		
		if num_sitios_predichos>0:
			mae /= num_sitios_predichos
		
		#Calculamos el porcentaje de votos que se ha podido predecir
		coverage = num_sitios_predichos*100/num_votos_test
		
		res = {'entrenamiento': (num_votos_total-num_votos_test),
		        'prueba': num_votos_test,
		        'mae': mae,
		        'cobertura': coverage
		       }
		#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
		#print "MAE = ", mae, " Cobertura = ", coverage, "%"
	
	except BaseException,e:
		print "Error: " + str(e)
	
	#Volvemos a guardar los votos en la BD
	for voto in votos_test:
		voto.save()

	return res


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_coseno2()
'''
def MAE_coseno2():
	from math import pow
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()
	num_votos_total = votos_total.count()
	
	try:
		#Calculamos la predicción para cada sitio y su diferencia con el real
		mae = 0
		mse = 0
		num_sitios_predichos = 0
		
		for voto in votos_total:
			
			voto.delete()
			
			p = 5*medida_coseno(voto.sitio, voto.user)
			
			if p>0:
				mae += abs(voto.valoracion - p)
				mse += pow(abs(voto.valoracion - p), 2)
				num_sitios_predichos += 1
			
			voto.save()
		
		if num_sitios_predichos>0:
			mae /= num_sitios_predichos
			mse /= num_sitios_predichos
						
		#Calculamos el porcentaje de votos que se ha podido predecir
		try:
			coverage = num_sitios_predichos*100/num_votos_total
		except:
			coverage = 0
		
		res = { 'num_votos_total': num_votos_total,
		        'mae': mae,
		        'mse': mse,
		        'cobertura': coverage,
		        'num_sitios_predichos': num_sitios_predichos,
		       }
		#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
		#print "MAE = ", mae, " Cobertura = ", coverage, "%"
	
	except BaseException,e:
		print "Error: " + str(e)


	return res



'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_contenido()
'''
def MAE_contenido():
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()

	#buscamos aquellos usuarios que tienen más de cinco votos
	cursor = connection.cursor()
	cursor.execute("SELECT user_id FROM sitios_voto GROUP BY user_id HAVING COUNT(*)>10")
	
	usuarios = cursor.fetchall()
	
	if len(usuarios)>1:
		users_id = repr(tuple([int(u[0]) for u in usuarios]))	
		votos_total = votos_total.extra(where=['user_id IN '+ users_id])
	else:
		user_id = str(usuarios[0][0])
		votos_total = votos_total.extra(where=['user_id = '+ user_id])

	num_votos_total = votos_total.count()
	
	#Obtenemos un conjunto de votos para test (20% del total)
	num_votos_test = 20*num_votos_total/100
	votos_test = votos_total.order_by('?')[:num_votos_test]
	copia_test = votos_test
	
	#Borramos los votos de la base de datos
	for voto in copia_test:
		voto.delete()


	try:
	
		cursor.execute("SELECT user_id FROM sitios_voto GROUP BY user_id HAVING COUNT(*)>=10")
		usuarios = cursor.fetchall()
		
		users_id = [int(u[0]) for u in usuarios]
				
		votos_test2 = []
		for v in votos_test:
			if int(v.user.id) in users_id:
			  votos_test2.append(v)
			else:
			  v.save()
		
		votos_test = votos_test2
		num_votos_test = len(votos_test)
		
		try:
			#Calculamos la predicción para cada sitio y su diferencia con el real
			mae = 0
			num_sitios_predichos = 0
			
			for voto in votos_test:
				p = probabilidades_para_un_sitio(voto.sitio, voto.user)
				
				if p['media']>0:
					mae += abs(voto.valoracion - p['media'])
					num_sitios_predichos += 1
					#print voto.valoracion, "\t", p['media']
			
			if num_sitios_predichos>0:
				mae /= num_sitios_predichos
							
			#Calculamos el porcentaje de votos que se ha podido predecir
			try:
				coverage = num_sitios_predichos*100/num_votos_test
			except:
				coverage = 0
			
			res = {'entrenamiento': (num_votos_total-num_votos_test),
			        'prueba': num_votos_test,
			        'mae': mae,
			        'cobertura': coverage
			       }
			#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
			#print "MAE = ", mae, " Cobertura = ", coverage, "%"
		
		except BaseException,e:
			print "Error: " + str(e)
	
	except BaseException,e:
		print "Error: " + str(e)
		
	#Volvemos a guardar los votos en la BD
	for voto in votos_test:
		voto.save()

	return res



'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_contenido2()
'''
def MAE_contenido2():
	from math import pow
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()
	num_votos_total = votos_total.count()
	
	try:
		#Calculamos la predicción para cada sitio y su diferencia con el real
		mae = 0
		mse = 0
		num_sitios_predichos = 0
		
		for voto in votos_total:
			
			voto.delete()
			
			p = probabilidades_para_un_sitio(voto.sitio, voto.user)
			
			if p['media']>0:
				mae += abs(voto.valoracion - p['media'])
				mse += pow(abs(voto.valoracion - p['media']), 2)
				num_sitios_predichos += 1
				#print voto.valoracion, "\t", p['media']
			
			voto.save()
		
		if num_sitios_predichos>0:
			mae /= num_sitios_predichos
			mse /= num_sitios_predichos
						
		#Calculamos el porcentaje de votos que se ha podido predecir
		try:
			coverage = num_sitios_predichos*100/num_votos_total
		except:
			coverage = 0
		
		res = { 'num_votos_total': num_votos_total,
		        'mae': mae,
		        'mse': mse,
		        'cobertura': coverage,
		        'num_sitios_predichos': num_sitios_predichos,
		       }
		#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
		#print "MAE = ", mae, " Cobertura = ", coverage, "%"
	
	except BaseException,e:
		print "Error: " + str(e)


	return res
			


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.porcentaje_aciertos()
'''
def porcentaje_aciertos():
	from math import pow
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()
	num_votos_total = votos_total.count()
	
	try:
		#Calculamos la predicción para cada sitio y su diferencia con el real
		aciertos = 0
		num_sitios_predichos = 0
		porcentaje = 0
		
		for voto in votos_total:
			
			voto.delete()
			
			p = probabilidades_para_un_sitio(voto.sitio, voto.user)
			
			if p['media']>0:
				if abs(voto.valoracion - p['media']) <= 0.5:
					aciertos += 1
				num_sitios_predichos += 1
			
			voto.save()
		
		if num_sitios_predichos>0:
			porcentaje = aciertos*100/num_sitios_predichos
		
		res = { 'num_votos_total': num_votos_total,
		        'aciertos': aciertos,
		        'porcentaje': porcentaje,
		        'num_sitios_predichos': num_sitios_predichos,
		       }
		#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
		#print "MAE = ", mae, " Cobertura = ", coverage, "%"
	
	except BaseException,e:
		print "Error: " + str(e)


	return res
	
'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.estadisticas_votos()
'''
def estadisticas_votos():

	valoraciones = {'0.5': 0,
					'1.0': 0,
					'1.5': 0,
					'2.0': 0,
					'2.5': 0,
					'3.0': 0,
					'3.5': 0,
					'4.0': 0,
					'4.5': 0,
					'5.0': 0,
					}
					
	votos = Voto.objects.all()
	num_votos = votos.count()
	
	for v in votos:
		valoraciones[str(v.valoracion)] += 1
	
	for key in valoraciones:
		print "[" + str(key) + "] = " + str(valoraciones[str(key)])


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.estadisticas_votos_medios()
'''
def estadisticas_votos_medios():

	from numpy import average
	
	valoraciones = {'0.5': 0,
					'1.0': 0,
					'1.5': 0,
					'2.0': 0,
					'2.5': 0,
					'3.0': 0,
					'3.5': 0,
					'4.0': 0,
					'4.5': 0,
					'5.0': 0,
					}
	
	usuarios = User.objects.all()
	num_usuarios = usuarios.count()
	
	votos = Voto.objects.all()
	num_votos = votos.count()
	
	for user in usuarios:
		try:
			votos_user = votos.filter(user=user)
			voto_medio = round(average([v.valoracion for v in votos_user])*2)/2
			valoraciones[str(voto_medio)] += 1
		except:
			pass
	
	for key in valoraciones:
		print "[" + str(key) + "] = " + str(valoraciones[str(key)])


'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
user = User.objects.get(username='draxus')
evidence = Sitio.objects.get(slug='kirin')
recommender.probabilidades_para_un_sitio(evidence, user)
'''
def probabilidades_para_un_sitio(evidence, user):
	from andaluciapeople.sitios.models import Voto, DatosUsuario, PesosTipoJerarquia
	from andaluciapeople.sitios.recommender_models import NodoSitio, NodoPerfilUsuario
	from django.core.cache import cache

	'''
	   1º Obtenemos el/los tipo/s del sitio a predecir su voto
	   2º Buscamos los sitios de ese tipo que el usuario haya votado
	   3º Calculamos las probabilidades de los sitios con respecto al evidence
	   4º Calculamos las probabilidades del perfil de usuario con respecto al evidence
	   5º Normalizamos los valores de la matriz
	'''
	capa_sitios = set()
	tipos_evidence = set(evidence.tipo.all())
	
	#print "Obteniendo votos de usuario"
	votos = Voto.objects.filter(user=user)
	
	pesos = cache.get('pesos_'+user.username)
	if pesos is None:
		#print "Obteniendo pesos de usuario"
		pesos = PesosTipoJerarquia.objects.filter(user=user)
		cache.set('pesos_'+user.username, pesos, 60*60)
	
	# Matriz con las probabilidades por voto
	#       voto -> 0 0.5 1 1.5 2 2.5 3 3.5 4 4.5 5 Media
	#               ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^
	#               |  |  |  |  |  |  |  |  |  |  |  |
	#probabilidad = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	probabilidad = {'0': 0,
					'0.5': 0,
					'1.0': 0,
					'1.5': 0,
					'2.0': 0,
					'2.5': 0,
					'3.0': 0,
					'3.5': 0,
					'4.0': 0,
					'4.5': 0,
					'5.0': 0,
					'media': 0,
					}
	
	for voto in votos:
		tipos_sitio = set(voto.sitio.tipo.all())
		# Si es del mismo tipo o bien tiene tipos en común
		tipos_comun = tipos_sitio.intersection(tipos_evidence)
		if len(tipos_comun)>0:
			#print "\tCreando nodo sitio ", voto.sitio.slug
			nodo_sitio = NodoSitio(voto.sitio, voto.valoracion)
			capa_sitios.add(nodo_sitio)
			#print "\tCalculando probabilidad de ", voto.sitio.slug, "con ", evidence.slug
			p = nodo_sitio.calcular_probabilidad(evidence, tipos_comun, pesos)
			probabilidad[str(nodo_sitio.voto)] += p
			probabilidad['0'] += 1-p
	
	#for s in capa_sitios:
	#	print s.sitio.nombre
	#	txt_tags = ''
	#	for tag in s.sitio.get_tags():
	#		txt_tags += tag.tag.tag + " " 
	#	print txt_tags + "\n"
	
	#print "Creando nodo perfil de usuario"
	perfil_usuario = NodoPerfilUsuario(user)
	#print "Calculando probabilidad del usuario con ", evidence.slug
	p = perfil_usuario.calcular_probabilidad(evidence, pesos)
	probabilidad['5.0'] += p   # Estamos suponiendo que el perfil de usuario tiene el voto máximo
	probabilidad['0'] += 1-p
	
	# Normalizamos para que la suma de la matriz sea igual a 1
	#print "Normalizamos"
	#suma_p = sum(probabilidad)
	suma_p = 0.0
	for key,val in probabilidad.iteritems():
		suma_p += val
	
	
	for key in probabilidad:
		if key!= 'media':
		  probabilidad[key] /= suma_p
	
	# Normalizamos para que la suma de los votos sea igual a 1 (Paper página 20)
	# Se necesita para obtener el voto medio
	if probabilidad['0']<1:
	  for key in probabilidad:
		  if key!='0' and key!='media':
		    probabilidad[key] /= 1-probabilidad['0']
		    #Calculamos el voto promedio
		    probabilidad['media'] += float(key)*probabilidad[key]
	
	#Calculamos el voto máximo
	#max_probabilidad = 0.0
	#for key in probabilidad:
	#  if key!='0' and key!='media':
	#    if probabilidad[key]>max_probabilidad:
	#       max_probabilidad = probabilidad[key]
	#       probabilidad['media'] = float(key)
	
	#Calculamos el voto mediano
	#sum_probabilidad = 0.0
	#for key in probabilidad:
	#  if key!='0' and key!='media':
	#    if sum_probabilidad<=0.5:
	#       sum_probabilidad += probabilidad[key]
	#       if sum_probabilidad>=0.5:
	#         probabilidad['media'] = float(key)
	#         break

	# Damos más o menos prioridad si el sitio es gay o no	
	#is_gay = False
	#for tag in evidence.get_tags():
	#	if tag.tag.tag == 'gay':
	#		is_gay = True
	#
	# user_gay = ???
		         
	return probabilidad




'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
user = User.objects.get(username='draxus')
recommender.recomendar_sitios_tipo_con_valoracion('restaurante', 4, 'Granada', user)
'''
def recomendar_sitios_tipo_con_valoracion(slug_tipo, ciudad, zona, user):
	from andaluciapeople.sitios.models import Sitio,Tipo,Voto
	from django.core.cache import cache
	
	'''
	   1º Obtener los sitios filtrados por tipo
	   2º Quitamos aquellos sitios que el usuario ya ha votado
	   3º Obtener la matriz de probabilidades de cada uno de ellos
	   4º Ordenar por la probabilidad del 0 y devolver los 10 mejores
	'''
	#cod_ciudad = LISTA_CIUDADES_SLUG.index(ciudad)+1
	#print "Entrando a recomendar_sitios_tipo_con_valoracion"
	cod_ciudad = ciudad
	#print "Obteniendo tipos"
	tipo = Tipo.objects.get(slug=slug_tipo)
	#print "Obteniendo sitios"
	if zona != "":
	  sitios = set(Sitio.objects.filter(tipo=tipo, ciudad=cod_ciudad, zona=zona))
	else:
	  sitios = set(Sitio.objects.filter(tipo=tipo, ciudad=cod_ciudad))
	
	#print "Obteniendo sitios votados por el usuario"
	votos = Voto.objects.filter(user=user)
	sitios_votados = set([v.sitio for v in votos])
	
	#print "Haciendo diferencia de sitios"
	sitios = sitios.difference(sitios_votados)
	
	#print "Obteniendo probabilidades de %i sitios" % (len(sitios))
	probabilidades = []
	for sitio in sitios:
		#print "\t Obteniendo sitio similar a ", sitio.slug
		p = probabilidades_para_un_sitio(sitio, user)
		if p['0']<1 and p['media']>2.5: #quitamos los que no aportan nada
		  #probabilidades.append((sitio.slug, p, p[0]))
		  probabilidades.append({
			'nombre': sitio.nombre, 
			'slug': sitio.slug, 
			'ciudad': str(LISTA_CIUDADES_SLUG[sitio.ciudad-1]), 
			'rank': str(sitio.rank), 
			'prediccion': str(round(p['media']*2)/2), 
			'precision': str(p['0']),
			'tags' : [x.tag.tag for x in sitio.get_tags()]
		  })
		#print "\t\t Listo!"
	
	#print "Ordenando probabilidades"
	#probabilidades.sort(key=operator.itemgetter(2), reverse=False)
	probabilidades.sort(key=operator.itemgetter('precision'), reverse=False)
	probabilidades = probabilidades[0:10]
	#for p in probabilidades:
		#p_votos = "["
		#for v in p[1]:
		#	p_votos += str(v)[0:4] + ", "
		#p_votos += "]"
		#print str(p[0]) + " = " + p_votos
		#print repr(p)
		
		

	#print "Saliendo..."
	return probabilidades

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------


#Sólo por etiquetas en común
def sitios_similares(sitio):
	from models import Sitio, ObjetoEtiquetado
	from django.db import connection
	
	cursor = connection.cursor()
	umbral = 1
	max_sitios = 5

	resultados = []
	try:
		etiquetas = ObjetoEtiquetado.objects.filter(sitio=sitio)
		etiquetas_tags = [str(e.tag) for e in etiquetas]
		#TODO Obtener el nombre de la tabla de algún sitio
		sql = "SELECT matches.sitio_id, COUNT( matches.sitio_id ) AS num_common_tags\
		FROM (sitios_objetoetiquetado as matches\
		INNER JOIN sitios_etiqueta as tags ON ( tags.id = matches.tag_id ))\
		INNER JOIN sitios_sitio as sitio ON ( sitio.id = matches.sitio_id)\
		WHERE sitio.ciudad=" + str(sitio.ciudad) + " AND matches.sitio_id!=" + str(sitio.id) + " AND tags.tag IN " + repr(etiquetas_tags).replace('[', '(').replace(']', ')') + "\
		GROUP BY matches.sitio_id\
		HAVING num_common_tags >= " + str(umbral) + "\
		ORDER BY num_common_tags DESC\
		LIMIT 0, " + str(max_sitios)
		#print sql
		cursor.execute(sql)
		sitios_ids = [item[0] for item in cursor.fetchall()]
		resultados = Sitio.objects.filter(id__in = sitios_ids)
	except BaseException, e:
		print e
	
	return resultados

'''
def sitios_similares2(self):
	cursor = connection.cursor()
	umbral = 1
	max_sitios = 5

	etiquetas = ObjetoEtiquetado.objects.filter(sitio=self)
	etiquetas_tags = [str(e.tag) for e in etiquetas]

	
	
	sitios_ids = [item[0] for item in cursor.fetchall()]
	return Sitio.objects.filter(id__in = sitios_ids)
'''	



'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_colaborativo()
'''
def MAE_colaborativo():
	
	from math import sqrt
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()

	#buscamos aquellos usuarios que tienen más de cinco votos
	cursor = connection.cursor()
	cursor.execute("SELECT user_id FROM sitios_voto GROUP BY user_id HAVING COUNT(*)>1")
	
	usuarios = cursor.fetchall()
	
	users_id = repr(tuple([int(u[0]) for u in usuarios]))
	
	votos_total = votos_total.extra(where=['user_id IN '+ users_id])
	num_votos_total = votos_total.count()
	
	#Obtenemos un conjunto de votos para test (20% del total)
	num_votos_test = 20*num_votos_total/100
	votos_test = votos_total.order_by('?')[:num_votos_test]
	copia_test = votos_test
	
	#Borramos los votos de la base de datos
	for voto in copia_test:
		voto.delete()


	try:
	
		cursor.execute("SELECT user_id FROM sitios_voto GROUP BY user_id HAVING COUNT(*)>=1")
		usuarios = cursor.fetchall()
		
		users_id = [int(u[0]) for u in usuarios]
				
		votos_test2 = []
		for v in votos_test:
			if int(v.user.id) in users_id:
			  votos_test2.append(v)
			else:
			  v.save()
		
		votos_test = votos_test2
		num_votos_test = len(votos_test)
		
		try:
			#Calculamos la predicción para cada sitio y su diferencia con el real
			mae = 0
			num_sitios_predichos = 0
			
			for voto in votos_test:
				p = prediction(voto.sitio, voto.user)
				
				if p>0:
					mae += abs(voto.valoracion - p)
					#mae += sqrt(voto.valoracion*voto.valoracion - p*p)
					num_sitios_predichos += 1
					#print voto.valoracion, "\t", p['media']
			
			if num_sitios_predichos>0:
				mae /= num_sitios_predichos
							
			#Calculamos el porcentaje de votos que se ha podido predecir
			coverage = num_sitios_predichos*100/num_votos_test
			
			res = {'entrenamiento': (num_votos_total-num_votos_test),
			        'prueba': num_votos_test,
			        'mae': mae,
			        'cobertura': coverage
			       }
			#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
			#print "MAE = ", mae, " Cobertura = ", coverage, "%"
		
		except BaseException,e:
			print "Error: " + str(e)
	
	except BaseException,e:
		print "Error: " + str(e)
		
	#Volvemos a guardar los votos en la BD
	for voto in votos_test:
		voto.save()

	return res



'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *; recommender.MAE_colaborativo2()
'''
def MAE_colaborativo2():
	from math import pow
	
	#Obtenemos todos los votos
	votos_total = Voto.objects.all()
	num_votos_total = votos_total.count()
	
	try:
		#Calculamos la predicción para cada sitio y su diferencia con el real
		mae = 0
		mse = 0
		num_sitios_predichos = 0
		
		for voto in votos_total:
			
			voto.delete()
			
			p = prediction(voto.sitio, voto.user)
			
			if p>0:
				mae += abs(voto.valoracion - p)
				mse += pow(abs(voto.valoracion - p), 2)
				num_sitios_predichos += 1
				#print voto.valoracion, "\t", p['media']
			
			voto.save()
		
		if num_sitios_predichos>0:
			mae /= num_sitios_predichos
			mse /= num_sitios_predichos
						
		#Calculamos el porcentaje de votos que se ha podido predecir
		try:
			coverage = num_sitios_predichos*100/num_votos_total
		except:
			coverage = 0
		
		res = { 'num_votos_total': num_votos_total,
		        'mae': mae,
		        'mse': mse,
		        'cobertura': coverage,
		        'num_sitios_predichos': num_sitios_predichos,
		       }
		#print "entrenamiento = ", (num_votos_total-num_votos_test), " prueba = ", num_votos_test
		#print "MAE = ", mae, " Cobertura = ", coverage, "%"
	
	except BaseException,e:
		print "Error: " + str(e)


	return res
	



def prediction(sitio, user):
	from models import Voto
	from math import sqrt

	def media(v):
		sum = 0
		for i in v:
			sum += i.valoracion
		return sum/len(v)

	def co_rated_items(v1, v2):
		co_rated_1 = []
		co_rated_2 = []
		for i in v1:
			for j in v2:
				if i.sitio == j.sitio:
					co_rated_1.append(i)
					co_rated_2.append(j)
		return co_rated_1, co_rated_2
	
	datos_user = DatosUsuario.objects.get(user=user)
	
	# coger los votos del usuario
	mis_votos = Voto.objects.filter(user=user)
	
	# coger usuarios que han votado
	otros_votos = Voto.objects.exclude(user=user)
	otros_usuarios = otros_votos.values('user').distinct()

	# comparar similaridad
	numerador = 0
	denominador = 0
	for otro in otros_usuarios:
		otro_votos = otros_votos.filter(user=otro['user'])
		try:
			rating_self = otro_votos.get(sitio=sitio)
			sim_1_2, num_comunes = datos_user.similitud(otro['user'], mis_votos, otro_votos)
			if sim_1_2>0:
				numerador += sim_1_2 * (rating_self.valoracion - media(otro_votos))
				#numerador += sim_1_2 * rating_self.valoracion
				denominador += sim_1_2
		except BaseException, e:
			#print str(e)
			pass
	
	try:
		pred = media(mis_votos) + (numerador/denominador)
	except:
		pred = 0
	return pred




def similitud(user, user_2, user_votos=None, user_2_votos=None):
	from math import sqrt
	
	def media(v):
		sum = 0
		for i in v:
			sum += i.valoracion
		return sum/len(v)

	def co_rated_items(v1, v2):
		co_rated_1 = []
		co_rated_2 = []
		for i in v1:
			for j in v2:
				if i.sitio == j.sitio:
					co_rated_1.append(i)
					co_rated_2.append(j)
		return co_rated_1, co_rated_2
	
	if user_votos is None:
		user_votos = Voto.objects.filter(user=user)
	if user_2_votos is None:
		user_2_votos = Voto.objects.filter(user=user_2)
	
	#obetener los vectores con los elementos comunes
	co_rated_1, co_rated_2 = co_rated_items(user_votos, user_2_votos)
	num_comunes = len(co_rated_1)
	
	if num_comunes>0:
		#media_1 = media(co_rated_1) #necesario para COR
		#media_2 = media(co_rated_2) #necesario para COR
		
		numerador = 0
		for i in range(num_comunes):
			#numerador += (co_rated_1[i].valoracion - media_1)*(co_rated_2[i].valoracion - media_2) #COR
			#numerador += co_rated_1[i].valoracion * co_rated_2[i].valoracion						#COS
			numerador += (co_rated_1[i].valoracion - 3)*(co_rated_2[i].valoracion - 3)				#CPC
		
		denominador_1 = 0
		for i in co_rated_1:
			#denominador_1 += (i.valoracion - media_1)*(i.valoracion - media_1) #COR
			#denominador_1 += i.valoracion * i.valoracion						#COS
			denominador_1 += (i.valoracion - 3)*(i.valoracion - 3)				#CPC
		denominador_1 = sqrt(denominador_1)
		
		denominador_2 = 0
		for i in co_rated_2:
			#denominador_2 += (i.valoracion - media_2)*(i.valoracion - media_2) #COR
			#denominador_2 += i.valoracion * i.valoracion						#COS
			denominador_2 += (i.valoracion - 3)*(i.valoracion - 3)				#CPC
		denominador_2 = sqrt(denominador_2)
		
		try:
			sim_1_2 = numerador/(denominador_1*denominador_2)
		except:
			sim_1_2 = 0
		
		return sim_1_2, num_comunes
	
	return 0, 0



'''
from sitios.models import *
user = User.objects.get(username='draxus')
recommender.usuarios_similares(user)
'''
def usuarios_similares(user):		
	def cmp(x, y):
		sim1 = x['sim']
		sim2 = y['sim']
		if sim1<sim2:
			return -1
		if sim1>sim2:
			return 1
		else:
			return 0
					
	# coger los votos del usuario
	mis_votos = Voto.objects.filter(user=user)
	
	# coger usuarios que han votado
	otros_votos = Voto.objects.exclude(user=user)
	otros_usuarios = otros_votos.values('user').distinct()

	datos_user = DatosUsuario.objects.get(user=user)
	
	# comparar similaridad
	sim = []
	for otro in otros_usuarios:
		otro_votos = otros_votos.filter(user=otro['user'])
		
		sim_1_2, num_comunes = datos_user.similitud(otro['user'], mis_votos, otro_votos)
		if sim_1_2>0:
			#sim.append({ 'user': User.objects.get(id=otro['user']), 'sim': sim_1_2, 'comunes': num_comunes })
			sim.append({ 'user': User.objects.get(id=otro['user']), 'sim': sim_1_2*num_comunes, 'comunes': num_comunes })
			

	#ordenamos por similaridad
	sim.sort(cmp=cmp, reverse=True)
	# devolver los mejores
	return sim




'''
Para pruebas:
$ python manage.py shell --settings=andaluciapeople.settings
from sitios.models import *
user = DatosUsuario.objects.get(user__username='draxus')
recommender.sitios_recomendados_colaborativo(user, 5)
'''
def sitios_recomendados_colaborativo(user, num):

	#cogemos los 3 usuarios que más se le parecen
	usuarios = usuarios_similares(user)[:3]
	usuarios_ids = repr(tuple([int(u['user'].id) for u in usuarios]))
	
	#obtenemos los sitios que el usuario ya ha votado
	sitios_ids = repr(tuple([int(v.sitio.id) for v in Voto.objects.filter(user=user.user)]))
	
	#obtenemos aquellos sitios que han votado los usuarios parecidos y que el actual no
	votos_usuarios = Voto.objects.extra(where=['user_id IN %s' % (usuarios_ids)]).extra(where=['sitio_id NOT IN %s' % (sitios_ids)]).filter(valoracion__gt = 3.5).values("sitio_id").distinct()
	
	sitios_ids = repr(tuple([int(v['sitio_id']) for v in votos_usuarios]))
	
	sitios = Sitio.objects.extra(where=['id IN %s' % (sitios_ids)]).order_by('?')[:num]
	
	for s in sitios:
		print s
	
	


'''
def sitios_recomendados(user):
	def cmp(x, y):
		sim1 = x['pred']
		sim2 = y['pred']
		if sim1<sim2:
			return -1
		if sim1>sim2:
			return 1
		else:
			return 0
	
	sitios = Sitio.objects.all()[:20]
	
	lista = []
	for s in sitios:
		pred = s.prediction(user)
		if pred>1:
			lista.append({ 'sitio': s, 'pred': pred })
	
	lista.sort(cmp=cmp, reverse=True)
	return lista
'''





"""
No nos hace falta, los cogemos directamente de la BD ya que he dividido la tabla en sitios_voto y en sitios_voto_test
def generar_base_test():
	from andaluciapeople.sitios.models import Voto
	from math import ceil
	from random import sample
	'''
	El 20% de los votos de forma aleatoria
	'''
	numvotos = Voto.objects.count()
	numtest = int(ceil(20*numvotos/100))
	
	i_todos = set(xrange(numvotos))
	i_test = set(sample(xrange(numvotos), numtest))
	i_base = i_todos.difference(i_test)
	
	votos = Voto.objects.all()
	
	#Creamos el conjunto de test
	test = set()
	for i in i_test:
		test.add(votos[i])
	
	#Creamos el conjunto base
	base = set()
	for i in i_base:
		base.add(votos[i])
	
	return (base,test)
"""

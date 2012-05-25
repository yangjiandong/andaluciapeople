# -*- coding: utf-8 -*-

from math import log
from sitios.models import *
from recommender_pesos import *
from django.core.cache import cache

"""
1º Instanciar el sitio a predecir
2º Instanciar sus etiquetas con la probabilidad que les corresponda
3º Instanciar aquellos sitios que tiene algunas de las etiquetas anteriores, calculando la probabilidad para cada uno
4º Calcular la distribución de probabilidades para el usuario activo
"""

CapaEtiquetas = dict()
CapaSitios = dict()
NUM_SITIOS = Sitio.objects.all().count()

class NodoEtiqueta:
	''' NodoEtiqueta
	    Cada etiqueta está descrita por un nodo de esta clase:
	    * tag
	    * ocurrencias
	    * get_probabilidad
	'''
	def __init__(self, tag):
		self.tag = tag
		self.ocurrencias = ObjetoEtiquetado.objects.filter(tag=tag).count()
	
	def get_probabilidad(self):
		try:
			return self.probabilidad
		except:
			pass
		
		self.probabilidad = (self.ocurrencias+0.5)/(NUM_SITIOS+1)
		return self.probabilidad
	
class NodoSitio:
	''' NodoSitio
	    Cada sitio está representado por un nodo de esta clase:
	    * sitio
	    * valoracion
	'''
	def __init__(self, sitio, valoracion):
		self.sitio = sitio
		self.valoracion = valoracion
		self.num_sitios = Sitio.objects.all().count()
		self.ptr = dict()
	
	def get_descriptores(self):
		try:
			return self.descriptores
		except:
			pass
		
		self.descriptores = [x.tag for x in ObjetoEtiquetado.objects.filter(sitio=self.sitio)]
		
		aux = dict()
		for tag in self.descriptores:
			if not CapaEtiquetas.has_key(tag.id):
				CapaEtiquetas[tag.id] = NodoEtiqueta(tag)
			
			aux[tag.id] = log(self.num_sitios/CapaEtiquetas[tag.id].ocurrencias + 1) #log en base e
		sum_aux = sum(aux)
		
		self.pesos = dict()	
		for tag in self.descriptores:
			self.pesos[tag.id] = aux[tag.id]/sum_aux
		
		#TODO Darle más o menos peso según la jerarquía a la que pertenece la etiqueta
		return self.descriptores
		
	def get_probabilidad_item_relevante(self):
		try:
			return self.pir
		except:
			pass
		
		self.pir = 0
		for tag in self.descriptores:
			self.pir += self.pesos[tag.id] * CapaEtiquetas[tag.id].get_probabilidad()
		
		return self.pir
	
	def get_probabilidad_tag_relevante(self, tag):
		try:
			return self.ptr[tag.id]
		except:
			pass
		
		self.ptr[tag.id] = CapaEtiquetas[tag.id].get_probabilidad()
		if tag in self.descriptores:
			self.ptr[tag.id] += (self.pesos[tag.id]*self.ptr[tag.id]*(1-self.ptr[tag.id]))/self.get_probabilidad_item_relevante()
			
		return self.ptr[tag.id]
	
	def get_probabilidad(self):
		try:
			return self.probabilidad
		except:
			pass
		
		self.probabilidad = 0
		for tag in self.get_descriptores():
			self.probabilidad += self.pesos[tag.id]*self.get_probabilidad_tag_relevante(tag)
		
		return self.probabilidad

class NodoUsuarioActivo:
	
	def __init__(self, user):
		self.user = user
		consulta = Voto.objects.filter(user=user)
		self.num_votos = consulta.count()
		for x in consulta:
			CapaSitios[x.sitio.id] = NodoSitio(x.sitio, x.valoracion)
	
	def __str__(self):
		return u"Usuario activo: %s\nNumero de votos: %d" % (self.user, self.num_votos)
		
	def predecir_voto(self, sitio):
		instancia = NodoSitio(sitio, 0)
		#if instancia in CapaSitios.values(): #no es necesaria, se hace en la vista
		#	print u"Este sitio ya lo votó el usuario"
		#	return False
		
		CapaSitios[sitio.id] = instancia
		CapaSitios[sitio.id].probabilidad = 1
		
		for tag in CapaSitios[sitio.id].get_descriptores():
			CapaSitios[sitio.id].get_probabilidad_tag_relevante(tag)
		
		self.pesos= [0, 0, 0, 0, 0, 0]
		for nodo in CapaSitios.values():
			if nodo!=instancia:
				pr = nodo.get_probabilidad()
				#print u"Sitio: %s ; Valoracion: %d; Probabilidad: %.3f" % (nodo.sitio.slug, nodo.valoracion, pr)
				if pr>0.5: #TODO Definir a partir de qué probabilidad es un ítem relevante
					self.pesos[nodo.valoracion] += 1/self.num_votos
				else:
					self.pesos[0] += 1/self.num_votos
				
		print repr(self.pesos)
		
		return self.pesos.index(max(self.pesos))
		
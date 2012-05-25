# -*- coding: utf-8 -*-

from math import log
from sitios.models import *
from recommender_pesos import *
from django.core.cache import cache

class NodoPerfilUsuario:
	def __init__(self, user):
		self.user = user
		self.gustos = set(DatosUsuario.objects.get(user=user).gustos.all())
				
	def calcular_probabilidad(self, evidence, pesos):
		'''
		   1º Obtenemos las etiquetas en común del perfil de usuario y del evidence.
		   2º Calculamos las probabilidades una a una junto con la matriz de pesos asociada al tipo de sitio.
		   3º Devolvemos la suma de las probabilidades.
		   
		   Nota: estamos suponiendo que todas las etiquetas dentro de una jerarquía van a tener el mismo peso.
		'''	
		probabilidad = cache.get('probabilidad_'+str(self.user.username)+'_'+str(evidence.id))
		
		if probabilidad is None:
			
			tags_evidence = cache.get('tags_'+str(evidence.id))
			
			if tags_evidence is None:
				objtags_evidence = ObjetoEtiquetado.objects.filter(sitio=evidence)
				tags_evidence = set()
				for objtag in objtags_evidence:
					tags_evidence.add(objtag.tag)
				cache.add('tags_'+str(evidence.id), tags_evidence, 24*60*60)
				
			tags_comunes = self.gustos.intersection(tags_evidence)
				
			probabilidad = 0.0
			
			if len(tags_comunes)>0:
				tipos_evidence = evidence.tipo.all()
				num_tipos = len(tipos_evidence)
				
				for tag in tags_comunes:
					# OJO! Un sitio puede tener varios tipos!!!
					# Solución: haremos la media aritmética si tiene más de uno.
					
					probabilidad_temp = 0
					for tipo in tipos_evidence:
						if tag.padre!=None:
							probabilidad_temp += pesos.get(tipo=tipo, jerarquia=tag.padre).peso
							#print "PERFIL " + str(tag.tag) + " (" + str(tag.padre.slug) + ")"
							
					probabilidad_temp /= num_tipos
					probabilidad += probabilidad_temp
		
			cache.add('probabilidad_'+str(self.user.username)+'_'+str(evidence.id), probabilidad, 24*60*60)
		
		return probabilidad
		
class NodoSitio:
	# evidence -> sitio para predecir su voto
	def __init__(self, sitio, voto):
		self.sitio = sitio
		self.voto = voto
	
	def calcular_probabilidad(self, evidence, tipos_comun, pesos):
		'''
		    1º Obtenemos las etiquetas que tienen en común el sitio actual con el sitio a predecir.
		    2º Calculamos las probabilidades una a una junto con la matriz de pesos asociada al tipo de sitio.
		    3º Devolvemos la suma de las probabilidades.
		    
		    Nota: estamos suponiendo que todas las etiquetas dentro de una jerarquía van a tener el mismo peso.
		'''
		probabilidad = cache.get('probabilidad_'+str(self.sitio.id)+'_'+str(evidence.id))
		if probabilidad is None:
			# Usamos conjuntos para poder intersecarlos fácilmente
			#print "Obteniendo probabilidad entre sitios:", 'probabilidad_'+str(self.sitio.id)+'_'+str(evidence.id)
			tags_sitio = cache.get('tags_'+str(self.sitio.id))
			if tags_sitio is None:
				objtags_sitio = ObjetoEtiquetado.objects.filter(sitio=self.sitio)
				tags_sitio = set()
				for objtag in objtags_sitio:
					tags_sitio.add(objtag.tag)
				cache.add('tags_'+str(self.sitio.id), tags_sitio, 24*60*60)
				
			tags_evidence = cache.get('tags_'+str(evidence.id))
			if tags_evidence is None:
				objtags_evidence = ObjetoEtiquetado.objects.filter(sitio=evidence)
				tags_evidence = set()
				for objtag in objtags_evidence:
					tags_evidence.add(objtag.tag)
				cache.add('tags_'+str(evidence.id), tags_evidence, 24*60*60)
				
			tags_comunes = tags_sitio.intersection(tags_evidence)
			
			probabilidad = 0.0
			
			if len(tags_comunes)>0:
				num_tipos = len(tipos_comun)
				
				for tag in tags_comunes:
					# OJO! Un sitio puede tener varios tipos!!!
					# Solución: sólo cogeremos aquellos que tiene en común con el evidence y
					#           haremos la media aritmética si tiene más de uno.
					
					probabilidad_temp = 0
					for tipo in tipos_comun:
						if tag.padre!=None:
							probabilidad_temp += pesos.get(tipo=tipo, jerarquia=tag.padre).peso
							#probabilidad_temp += PESOS_TIPO[tipo.slug][tag.padre.slug]
							#print "SITIO " + str(tag.tag) + " (" + str(tag.padre.slug) + ")"
							
					probabilidad_temp /= num_tipos
					probabilidad += probabilidad_temp
			
			cache.add('probabilidad_'+str(self.sitio.id)+'_'+str(evidence.id), probabilidad, 24*60*60)
		
		return probabilidad

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
"""

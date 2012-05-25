# -*- coding: utf-8 -*-
from django import forms
from andaluciapeople.piston.handler import BaseHandler
from andaluciapeople.sitios.models import Sitio

class SitioForm(forms.ModelForm):
    class Meta:
        model = Sitio

class SitioHandler(BaseHandler):
    allowed_methods = ('GET', )
    fields = ('id', 'nombre', 'slug', 'direccion', 'zona', 'ciudad', 'tipo',
        'lat', 'lng', 'telefono', 'web', 'rank', 'num_votos',
        'cerrado', 'traslado', 'cambio_nombre', 'incorrecto')
    model = Sitio

    def read(self, request):
        id = int(request.GET.get('id', -1))
        if id<0:
            raise
        else:
            sitio = Sitio.objects.get(id=id)
            return sitio

    def create(self, request):
        if request.content_type:
            data = request.data

            sitio = self.model(nombre=data['nombre'],
                               slug=slughifi(data['nombre']),
                               direccion=data['direccion'],
                               zona=data['zona'],
                               ciudad=data['ciudad'],
                               tipo=data['tipo'],
                               lat=data['lat'],
                               lng=data['lng'],
                               telefono=data['telefono'],
                               web=data['web'],
                               fecha=datetime.datetime.now(),
                               ip=request.META['REMOTE_ADDR'])
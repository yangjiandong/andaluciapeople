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
from oauth_access.callback import AuthenticationCallback
from sitios.views import create_user_profile
from slughifi import slughifi
from datetime import datetime

class DjangoCallback(AuthenticationCallback):

    def redirect_url(self, request):
        return "/"


class FacebookCallback(DjangoCallback):

    def handle_no_user(self, request, access, token, user_data):
        return self.create_user(request, access, token, user_data)
    
    def create_user(self, request, access, token, user_data):
        try:
            name = user_data['name']
            slug_name = slughifi(name)
            try:
                user = User.objects.get(username=slug_name) #@UnusedVariable
            except:
                pass # si no existe, no pasa nada
            else:
                raise #si existe, lanzamos una excepciónpara que escoja otro nombre de usuario
        except:
            slug_name = self.identifier_from_data(user_data)
        try:
            email = user_data['email']
        except:
            email = '%s@facebook.com' % slug_name #TODO
        try:
            website = user_data['website']
        except:
            website = user_data['link']
        try:
            gender = user_data['gender']
            if gender=='hombre' or gender=='man':
                gender = 'H'
            elif gender=='mujer' or gender=='woman':
                gender = 'M'
            else:
                gender = 'I'
        except:
            gender = 'I'
        try:
            locale = user_data['locale'][0:2]
        except:
            locale = 'es'
        try:
            birthday = datetime.strptime(user_data['birthday'], '%m/%d/%Y')
        except:
            birthday = None
        user = User(username=slug_name, email=email)
        user.set_unusable_password()
        user.save()
        
        user_profile = create_user_profile(user, user.username, servicio='Facebook')
        user_profile.web = website
        user_profile.sexo = gender
        user_profile.idioma = locale
        user_profile.nacimiento = birthday
        user_profile.save()
        
        self.login_user(request, user)
        return user
    
    def fetch_user_data(self, request, access, token):
        url = "https://graph.facebook.com/me"
        return access.make_api_call("json", url, token)

    def identifier_from_data(self, data):
        return "fb-%s" % data["id"]
    
class TwitterCallback(DjangoCallback):

    def handle_no_user(self, request, access, token, user_data):
        return self.create_user(request, access, token, user_data)
    
    def create_user(self, request, access, token, user_data):
        try:
            name = user_data['screen_name']
            slug_name = slughifi(name)
            try:
                user = User.objects.get(username=slug_name) #@UnusedVariable
            except:
                pass # si no existe, no pasa nada
            else:
                raise #si existe, lanzamos una excepciónpara que escoja otro nombre de usuario
        except:
            slug_name = self.identifier_from_data(user_data)
        
        email = '%s@twitter.com' % slug_name #TODO
        
        try:
            website = user_data['url']
        except:
            website = 'http://twitter.com/%s' % slug_name
        
        gender = 'I'
        
        try:
            locale = user_data['lang']
        except:
            locale = 'es'
        
        birthday = None
        
        user = User(username=slug_name, email=email)
        user.set_unusable_password()
        user.save()
        
        user_profile = create_user_profile(user, user.username, servicio='Twitter')
        user_profile.web = website
        user_profile.sexo = gender
        user_profile.idioma = locale
        user_profile.nacimiento = birthday
        user_profile.save()
        
        self.login_user(request, user)
        return user
    
    def fetch_user_data(self, request, access, token):
        url = "http://api.twitter.com/1/account/verify_credentials.json"#?user_id=12345 or screen_name=username
        return access.make_api_call("json", url, token)

    def identifier_from_data(self, data):
        return "tw-%s" % data["id"]



class GoogleCallback(DjangoCallback):

    def handle_no_user(self, request, access, token, user_data):
        return self.create_user(request, access, token, user_data)
    
    def create_user(self, request, access, token, user_data):
        print user_data
        raise
        '''
        try:
            name = user_data['screen_name']
            slug_name = slughifi(name)
            try:
                user = User.objects.get(username=slug_name)
            except:
                pass # si no existe, no pasa nada
            else:
                raise #si existe, lanzamos uan excepciónpara que escoja otro nombre de usuario
        except:
            slug_name = self.identifier_from_data(user_data)
        
        email = '%s@twitter.com' % slug_name #TODO
        
        try:
            website = user_data['url']
        except:
            website = 'http://twitter.com/%s' % slug_name
        
        gender = 'I'
        
        try:
            locale = user_data['lang']
        except:
            locale = 'es'
        
        birthday = None
        
        user = User(username=slug_name, email=email)
        user.set_unusable_password()
        user.save()
        
        user_profile = create_user_profile(user)
        user_profile.web = website
        user_profile.sexo = gender
        user_profile.idioma = locale
        user_profile.nacimiento = birthday
        user_profile.save()
        
        self.login_user(request, user)
        return user
        '''
    
    def fetch_user_data(self, request, access, token):
        url = "http://api.twitter.com/1/account/verify_credentials.json"#?user_id=12345 or screen_name=username
        return access.make_api_call("json", url, token)

    def identifier_from_data(self, data):
        return "tw-%s" % data["id"]
    
    
#4sq http://developer.foursquare.com/docs/responses/user.html
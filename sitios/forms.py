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

from captcha.fields import CaptchaField
from sitios.models import Tipo
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.forms.extras import widgets
from django.template import Context
from django.template import loader
from django.utils.translation import ugettext_lazy as _
import locationmap
import random #@UnresolvedImport
import settings
import string #@UnresolvedImport
from datetime import datetime
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from itertools import chain
from django.utils.encoding import force_unicode
from sitios.multifile import FixedMultiFileInput, MultiFileField

class CheckboxSelectMultipleImproved(forms.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        #str_values = set([force_unicode(v) for v in value])
        # FIXED by draxus http://code.djangoproject.com/attachment/ticket/5247/patch.diff
        #str_values = set([force_unicode(v) for v in value])
        str_values = set()
        for v in value:
            if hasattr(v, '_get_pk_val'):
                str_values.add(force_unicode(v._get_pk_val()))
            else:
                str_values.add(force_unicode(v))
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)


CH_RANK = ((float(0.5), _(u'Muy malo')),
           (float(1), _(u'Malo')),
           (float(1.5), _(u'No demasiado malo')),
           (float(2), _(u'Regular')),
           (float(2.5), _(u'Ni bueno ni malo')),
           (float(3), _(u'Casi bueno')),
           (float(3.5), _(u'Bueno')),
           (float(4), _(u'Muy Bueno')),
           (float(4.5), _(u'Excelente')),
           (float(5), _(u'Perfecto')),
           )

CH_RANK_PLUS = (('0', _(u'Todos')),
                ('1', _(u'Malo')),
                ('2', _(u'Regular')),
                ('3', _(u'Aceptable')),
                ('4', _(u'Bueno')),
                ('5', _(u'Excelente')),
                )

CH_SEXO = (('H', _(u'Hombre')),
           ('M', _(u'Mujer')),
           ('I', _(u'Indeterminado')),
           )

CH_IDIOMA = (('es', 'Español'),
             ('en', 'English'),
             )

CH_CIUDAD = (('1', 'Almería'),
             ('2', 'Cádiz'),
             ('3', 'Córdoba'),
             ('4', 'Granada'),
             ('5', 'Huelva'),
             ('6', 'Jaén'),
             ('7', 'Málaga'),
             ('8', 'Sevilla'),
             )

CH_TARIFAS_PUBLICIDAD = (('BS2491P', _(u'Banner Superior 249x90 Exclusivo (1 Provincia) - 39€/mes')),
                         ('BS249TP', _(u'Banner Superior 249x90 Exclusivo (Todas Provincias) - 69€/mes')),
                         ('SPR1P', _(u'Sitio Patrocinado Rotatorio (1 Provincia) - 19€/mes')),
                         ('AP1P', _(u'Alojamiento Premium (1 Provincia) - 19€/mes')),
                         ('DEUAP', _(u'Descuentos Especiales para usuarios - Consultar precio')),
                         ('PODF', _(u'Promoción Ofertas en determinadas fechas - Consultar precio')),
                         ('VP', _(u'Vídeo promocional - Consultar precio')),
                         ('FP', _(u'Fotografías panorámicas - Consultar precio')),
                         ('OT', _(u'Otras consultas'))
                         )
CH_TIEMPO_CONTRATADO = (('12M', _(u'12 Meses')),
                        ('11M', _(u'11 Meses')),
                        ('10M', _(u'10 Meses')),
                        ('9M', _(u'9 Meses')),
                        ('8M', _(u'8 Meses')),
                        ('7M', _(u'7 Meses')),
                        ('6M', _(u'6 Meses')),
                        ('5M', _(u'5 Meses')),
                        ('4M', _(u'4 Meses')),
                        ('3M', _(u'3 Meses')),
                        ('2M', _(u'2 Meses')),
                        ('1M', _(u'1 Mes')),
                        ('OT', _(u'Otro'))
                        )

INVALID_USERNAMES = ['', 'administrador', 'superadmin']

class CommentForm(forms.Form):
    sitio = forms.IntegerField(widget=forms.HiddenInput)
    mensaje = forms.CharField(widget=forms.Textarea)
    action = forms.CharField(widget=forms.HiddenInput, initial='comentario')

class VoteForm(forms.Form):
    sitio = forms.IntegerField(widget=forms.HiddenInput)
    valoracion = forms.ChoiceField(widget=forms.Select, choices=CH_RANK)
    action = forms.CharField(widget=forms.HiddenInput, initial='voto')

class FotoForm(forms.Form):
    sitio = forms.IntegerField(widget=forms.HiddenInput)
    #foto = forms.ImageField()
    fotos = MultiFileField(widget=FixedMultiFileInput, count=3)
    action = forms.CharField(widget=forms.HiddenInput, initial='foto')

class TagForm(forms.Form):
    sitio = forms.IntegerField(widget=forms.HiddenInput)
    tag = forms.CharField()
    action = forms.CharField(widget=forms.HiddenInput, initial='tag')

class BuscaSitiosForm(forms.Form):
    s = forms.CharField()

class BuscaUsuariosForm(forms.Form):
    s = forms.CharField()

class UsernameChangeForm(forms.Form):
    username = forms.CharField(label=_(u'Nombre de usuario'), max_length=30, min_length=2, required=False)
    action = forms.CharField(label='', widget=forms.HiddenInput, initial='username')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username in INVALID_USERNAMES or len(username)<3:
            raise forms.ValidationError(_(u"El nombre de usuario no es válido"))

        user = User.objects.filter(username=username)
        if user:
            raise forms.ValidationError(_(u"Ya existe un usuario con ese nombre"))

        return username

class DatosUsuarioForm(forms.Form):
    web = forms.URLField(label=_(u'Web'), required=False)
    imagen = forms.ImageField(label=_(u'Imagen'),widget=forms.FileInput(attrs={'size':'12'}), required=False, help_text=_(u'Tamaño recomendado: 200x200 px'))
    boletin = forms.BooleanField(label=_(u'Boletín'), required=False)
    sexo = forms.ChoiceField(label=_(u'Sexo'), widget=forms.Select, choices=CH_SEXO, required=False)
    nacimiento = forms.DateField(label=_(u'Fecha de nacimiento'), widget=widgets.SelectDateWidget(years=range(datetime.now().year, 1900, -1)), required=False)
    notificaciones = forms.BooleanField(label=_(u'Notificaciones'), required=False)
    idioma = forms.ChoiceField(label=_(u'Idioma'), widget=forms.Select, choices=CH_IDIOMA, required=False)
    #gustos = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Etiqueta.objects.exclude(padre=None).order_by('padre','tag'), required=False)
    action = forms.CharField(label='', widget=forms.HiddenInput, initial='datos')


class SitioForm(forms.Form):
    nombre = forms.CharField(label=_(u'Nombre *'), max_length=100, help_text=_(u'Ej. La Carihuela'))
    ciudad = forms.ChoiceField(label=_(u'Provincia *'), widget=forms.Select, choices=CH_CIUDAD)
    zona = forms.CharField(label=_(u'Localidad *'), widget=forms.Select)
    direccion = forms.CharField(label=_(u'Dirección *'), max_length=100, help_text=_(u'Ej. Calle Puentezuelas, 2 (o pincha en el mapa)'))
    location = locationmap.LocationField(label=_(u'Mapa *'), help_text=_(u'Arrastra y coloca el punto lo más exactamente posible'))
    telefono = forms.CharField(label=_(u'Teléfono'), max_length=20, required=False, help_text=_(u'Ej. 950123456 (opcional)'))
    web = forms.URLField(label=_(u'Web'), required=False, help_text=_(u'Ej. http://www.miweb.com (opcional)'))
    tipo = forms.ModelMultipleChoiceField(label=_(u'Tipo *'), widget=CheckboxSelectMultipleImproved(attrs={'class':'tipo'}), queryset=Tipo.objects.all(), help_text=_(u'Elige el tipo o tipos que mejor representen al sitio'))

class RecomiendaSitiosForm(forms.Form):
    lista_tipos = ((item.slug, item.tipo) for item in Tipo.objects.all())
    tipo = forms.ChoiceField(label=_(u'Tipo'), widget=forms.Select, choices=lista_tipos)
    ciudad = forms.ChoiceField(label=_(u'Ciudad'), widget=forms.Select, choices=CH_CIUDAD)
    zona = forms.CharField(label=_(u'Localidad'), widget=forms.Select)
    #valoracion = forms.ChoiceField(label=u'Valoración', widget=forms.Select, choices=CH_RANK_PLUS)

class NewUserForm(forms.Form):
    username = forms.RegexField(label='用户名', max_length=30, regex=r'^\w+$',
                                #help_text=_(u'30 caracteres o menos. Sólo caracteres alfanuméricos (letras, dígitos y guión bajo)'),
                                help_text='最长30个字符。只允许英文字母，数字，下划线',
                                error_message='该字段只允许英文字母，数字，下划线')

    email = forms.RegexField(label='邮箱', max_length=75, regex=r'^[A-Za-z0-9](([_\.\-]?[a-zA-Z0-9]+)*)@([A-Za-z0-9]+)(([\.\-]?[a-zA-Z0-9]+)*)\.([A-Za-z]{2,})$',
                             help_text='请输入真实邮箱,我们将通过邮箱发送一些消息',
                             error_message='')

    password = forms.CharField(label='密码', widget=forms.PasswordInput)

    captcha = CaptchaField(label='验证码', help_text='输入以上信息保证你不是机器人')

class NewPassForm(forms.Form):
    email = forms.EmailField(label=_(u"E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that a user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(email__iexact=email)
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_(u"That e-mail address doesn't have an associated user account. Are you sure you've registered?"))

    def save(self):
        """
      Cambia la contraseña y la envia por correo
      """
        current_site = Site.objects.get_current()
        site_name = current_site.name
        domain = current_site.domain

        random.seed()
        t = loader.get_template('registration/password_reset_email.html')

        for user in self.users_cache:
            password = "".join([random.choice(string.letters + string.digits) for x in range(10)]) #@UnusedVariable
            user.set_password(password)
            user.save()
            c = {
                'email': user.email,
                'user': user,
                'password': password,
                'site_name': site_name,
                'domain': domain,
            }
            send_mail(_(u"Password reset on %s") % site_name, t.render(Context(c)), settings.EMAIL, [user.email])

class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(label=_(u"Old password"), widget=forms.PasswordInput)
    action = forms.CharField(label='', widget=forms.HiddenInput, initial='password')

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_(u"Your old password was entered incorrectly. Please enter it again."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2', 'action']

class ContactForm(forms.Form):
    nombre = forms.CharField(label=_(u"Nombre"), max_length=100)
    email = forms.EmailField(label=_(u"Email"))
    mensaje = forms.CharField(label=_(u"Mensaje"), max_length=1000, widget=forms.Textarea)
    captcha = CaptchaField(help_text=_(u"Introduce las siguientes letras para comprobar que no eres un robot."))

class PublicidadForm(forms.Form):
    nombre = forms.CharField(label=_(u"Tu Nombre *"), max_length=100)
    email = forms.EmailField(label=_(u"Tu Email *"), help_text=_(u"Donde te enviaremos la factura"))

    sitio = forms.CharField(label=_(u"Nombre del negocio *"), max_length=100, help_text=_(u'Ej. La Carihuela'))
    ciudad = forms.ChoiceField(label=_(u'Provincia *'), widget=forms.Select, choices=CH_CIUDAD)
    zona = forms.CharField(label=_(u'Localidad *'), widget=forms.Select)
    direccion = forms.CharField(label=_(u'Dirección *'), max_length=100, help_text=_(u'Ej. Calle Puentezuelas, 2 (o pincha en el mapa)'))
    location = locationmap.LocationField(label=_(u'Mapa *'), help_text=_(u'Arrastra y coloca el punto lo más exactamente posible'))
    telefono = forms.CharField(label=_(u'Teléfono'), max_length=20, required=False, help_text=_(u'Ej. 950123456 (opcional)'))
    web = forms.URLField(label=_(u'Web'), required=False, help_text=_(u'Ej. http://www.miweb.com (opcional)'))
    tipo = forms.ModelMultipleChoiceField(label=_(u'Tipo *'), widget=CheckboxSelectMultipleImproved(attrs={'class':'tipo'}), queryset=Tipo.objects.all(), help_text=_(u'Elige el tipo o tipos que mejor representen al sitio'))

    tarifa = forms.ChoiceField(label=_(u'Tarifa publicitaria *'), widget=forms.Select, choices=CH_TARIFAS_PUBLICIDAD)
    tiempo = forms.ChoiceField(label=_(u'Tiempo contratado *'), widget=forms.Select, choices=CH_TIEMPO_CONTRATADO)

    mensaje = forms.CharField(label=_("Mensaje"), help_text=_(u"Indícanos algo más si lo deseas"), max_length=1000, widget=forms.Textarea, required=False)
    captcha = CaptchaField(help_text=_(u"Introduce las siguientes letras para comprobar que no eres un robot."))
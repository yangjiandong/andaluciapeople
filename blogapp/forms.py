from django import forms
from django.utils.translation import ugettext as _

class CommentForm(forms.Form):
    author_name = forms.CharField(label=_('Nombre'), max_length=48)
    author_email = forms.EmailField(label=_('E-mail'))
    author_website = forms.URLField(required=False, label=_('Web'))
    comment = forms.CharField(widget=forms.Textarea, label=_('Comentario'), max_length=2048)

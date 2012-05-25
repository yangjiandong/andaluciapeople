from django import template
import string #@UnresolvedImport

register = template.Library()

@register.filter
def dotify(value):
    if isinstance(value, basestring):
        return string.replace(',', '.')
    elif isinstance(value, float):
        return ('%f' % value).replace(',', '.')
    else:
        return value

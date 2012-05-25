# Code from http://fi.am/entry/plugging-a-rss-feed-into-a-django-template/

from datetime import datetime
import time

from django.core.cache import cache
from django import template

import feedparser

register = template.Library()

@register.filter
def todatetime(value):
    return datetime(*time.localtime(time.mktime(value))[:6])

@register.tag
def rssplug(parser, token):
    try:
        tag_name, address, template = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%s tag requires 2 arguments' % token.split_contents()[0])

    return RssPlugNode(address, template)

class RssPlugNode(template.Node):
    def __init__(self, address, templ):
        self.address = template.Variable(address)
        self.templ = template.Variable(templ)

    def rss(self, addr):
        ckey = 'rssplug_%s' % addr
        data = cache.get(ckey)
        if data:
            return data
        data = feedparser.parse(addr)
        cache.set(ckey, data)
        return data

    def render(self, context):
        address = self.address.resolve(context)
        tmpl = self.templ.resolve(context)
        t = template.loader.get_template(tmpl)
        return ''.join([t.render(template.Context({ 'item': item })) for item in self.rss(address).entries])
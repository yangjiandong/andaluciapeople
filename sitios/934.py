# -*- coding: utf-8 -*-
'''
Admin Image Widget by KpoH
http://www.djangosnippets.org/snippets/934/#c1136
'''

from sorl.thumbnail.main import DjangoThumbnail

def thumbnail(image_path):
    t = DjangoThumbnail(relative_source=image_path, requested_size=(80, 80))
    return u'<img src="%s" alt="%s">' % (t.absolute_url, image_path)

class AdminImageWidget(AdminFileWidget):
    """
    A FileField Widget that displays an image instead of a file path
    if the current file is an image.
    """
    def render(self, name, value, attrs=None):
        output = []
        if value:
            file_path = '%s%s' % (settings.MEDIA_URL, value)
            try:
                output.append('<a target="_blank" href="%s">%s</a><br />' %
                        (file_path, thumbnail(value)))
            except IOError:
                output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' %
                        ('Currently:', file_path, value, 'Change:'))

        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

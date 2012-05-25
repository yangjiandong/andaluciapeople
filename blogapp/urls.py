from django.conf.urls.defaults import *

urlpatterns = patterns('blogapp.views',
    (r'^$', 'homepage'),
    (r'^([a-z0-9-]+)$', 'post_by_name'),
    (r'^page/([a-z0-9-]+)$', 'page_by_name'),
    (r'^tag/([a-z0-9-]+)/$', 'posts_by_tag'),
    (r'^archive/([0-9]{4})/([0-9]{1,2})/$', 'posts_by_date'),
    (r'feed/(rss|atom)/$', 'feed'),
)

urlpatterns += patterns('blogapp.utilities',
    (r'xmlrpc/$', 'django_xmlrpc.handle_xmlrpc'),
    (r'robots.txt$', 'robots_txt'),
)

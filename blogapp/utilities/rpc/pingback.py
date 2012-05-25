from django.utils.html import strip_tags

import re
from urllib2 import urlopen, HTTPError
from datetime import datetime

from blogapp.models import Post, Comment
from blogapp.urls import urlpatterns
from blogapp.utilities import options, escape

def rm_www(link):
    link = link.replace('http://', '').replace('https://', '')
    if link[:4] == 'www.':
        link = link[4:]
    return link

def get_reqid(link):
    base_url = rm_www(options('base_url'))
    return link.replace(base_url, '', 1).strip('/')

def ping(resource, target):

    #basic check agains cheating
    if resource == target:
        return "Error 0: Resource and target cannot be the same."

    #gets a regex for a post from urls file
    r = [pattern.regex for pattern in urlpatterns if pattern.callback.func_name == 'post_by_name'][0]
    reqid = get_reqid(rm_www(target))
    if not r.search(reqid):
        return "Error 0x0021: The specified target URI cannot be used as a target."
    else:
        post_name = r.search(reqid).groups()[0]
        try:
            post_id = Post.objects.get(name=post_name)
        except:
            return "Error 0x0021: The specified target URI cannot be used as a target."

    #opens and checks the resource uri
    try:
        f = urlopen(resource)
    except HTTPError, e:
        return "Error 0: Error while retrieving resource uri (%s)" % e.msg

    #string "html" shouldn't at position 0 anyway
    if f.headers.dict['content-type'].find('html'):
        s = f.read()
    else:
        return "Error 0: Content-type of the resource does not seem to be (x)html."
    f.close()

    #have pinged before?
    if Comment.objects.filter(post=post_id, author_website=resource):
        return "Error 0x0030: The pingback has already been registered."

    #are we linked to?
    link = re.search(r'<a[^>]*href=(\'|")' + re.escape(target) + '(\\1)[^>]*>[^<]+<\/a>', s)
    if not link:
        return "Error 0x0011: The source URI does not contain a link to the target URI, and so cannot be used as a source."
    else:
        mark = link.group()

    #fetch the title
    title = re.search(r'<title>(.+)</title>', s)
    if title:
        title = title.groups()[0]
    else:
        return "Error 0: Title of the resource page could not be found."


    #get an excerpt
    #take text between a tags (usually <p> and </p>)
    p = re.compile(r'([^>]*' + re.escape(mark) + '[^<]*)', re.DOTALL)
    excerpt = strip_tags(p.search(s).group()).strip()

    #semi-perfect length :)
    if len(excerpt) > 80:
        mark_pos = excerpt.find(strip_tags(mark))
        mark_len = len(strip_tags(mark))

        #might need some improvement
        start_diff = mark_pos - 30
        end_diff = len(excerpt) - mark_pos - mark_len - 30

        #might need some improvement as well
        start = (start_diff > 0) and (start_diff) or 0
        if end_diff < 0:
            end = len(excerpt)
        else:
            end = len(excerpt) - end_diff - ((start_diff < 0) and start_diff or 0)

        excerpt = excerpt[start:end]
        excerpt = ' '.join(excerpt.split(' ')[1:-1])

    excerpt = "[...] " + excerpt + " [...]"

    c = Comment(
        author_name=escape(title), 
        author_website=escape(resource),
        content=escape(excerpt),
        date=datetime.now(),
        comment_type='linkback',
        post=post_id)
    c.save()

    return "Pingback registered. Thank you."
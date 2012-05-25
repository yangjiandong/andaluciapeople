from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.forms import ValidationError

from os.path import dirname
from os import stat
from xml.dom import minidom
from time import time
from urllib import urlopen
from datetime import datetime
import pickle

from blogapp.models import *
from blogapp.utilities import friends
from blogapp.utilities.akismet import *

def blog_processor(request):
    context = {
        'options': options(),
        'tags': tag_list(),
        'archives': archive(),
        'friends': friends.get_list(),
        'tracklist': tracklist(),
    }
    return context

def not_found(request, title=_('Error 404'), message=_('Page not found')):
    t = get_template("service/404_message.html")
    c = RequestContext(request, {'err_title': title, 'err_message': message})
    html = t.render(c)
    return HttpResponseNotFound(html)

def options(opt_name=None):
    """
        If name is given, returns the value of an option (empty string if not found).
        Otherwise, returns a dictionary of options.
    """
    if opt_name:
        try:
            return Option.objects.get(name=opt_name).value
        except:
            return ""
    opt_list = [(opt.name, opt.value) for opt in Option.objects.all()]
    options = dict(opt_list)
    return options

def robots_txt(request):
    """
        Returns a content of robots.txt setting in options table.
    """
    content = options('robots.txt')
    return HttpResponse(content, mimetype="text/plain")

def escape(value):
    """
        This function is based on django.utils.html.escape, but doesn't have issues with unicode.
    """
    return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def unpickle_cookies(request):
    for cookie in request.COOKIES:
        try:
            request.COOKIES[cookie] = pickle.loads(request.COOKIES[cookie])
        except:
            request.COOKIES[cookie] = ''

def process_comment(request, post, form):
    """
        Processes a comment (anti-flood, anti-repost, anti-spam).
        Returns a HTTP Redirect or an error string.
    """

    #gather the data
    author = form.cleaned_data['author_name'].strip()
    email = form.cleaned_data['author_email'].strip()
    website = form.cleaned_data.get('author_website', '').strip()
    ip = request.META['REMOTE_ADDR']
    comment = form.cleaned_data['comment'].strip()

    #anti-flood and anti-repost
    has_comments = Comment.objects.filter(author_email=email).order_by('-date')
    if has_comments:
        #take newest
        c = has_comments[0]
        diff = datetime.now() - c.date
        if diff.seconds < 60:
            return _("You're too fast. Wait for 60 seconds.")
        elif c.content == comment and c.post.name == post.name:
            return _("It looks like you've just said that.")

    has_approved_comments = has_comments.filter(comment_type='comment').count()
    if has_approved_comments:
        #skip "approved" commenters
        comment_type = 'comment'
    else:
        api = Akismet(key=options('akismet_api_key'), blog_url=options('base_url'), agent='justanotherblogsystem')
        if api.verify_key():
            data = {}
            data['comment_author'] = author.encode('ASCII', 'replace')
            data['comment_content'] = comment.encode('ASCII', 'replace')
            data['user_ip'] = ip
            data['user_agent'] = request.META['HTTP_USER_AGENT']
            data['comment_author_email'] = email

            if api.comment_check(data['comment_content'], data):
                comment_type = 'spam'
            else:
                comment_type = 'comment'
        else:
            raise APIKeyError("Your akismet key is invalid.")

    #define a response
    response = HttpResponseRedirect(reverse('blogapp.views.post_by_name', args=[post.name]))

    #remember user's data (pickled)
    response.set_cookie('author_name', pickle.dumps(author), max_age=60*60*24*30)
    response.set_cookie('author_email', pickle.dumps(email), max_age=60*60*24*30)
    if website:
        response.set_cookie('author_website', pickle.dumps(website), max_age=60*60*24*30)

    #save comment
    p = Comment(author_name=escape(author),
            author_email=email,
            author_website=escape(website),
            content=escape(comment),
            date=datetime.now(),
            author_ip=ip,
            post=post,
            comment_type=comment_type)
    p.save()
    return response

def archive():
    p = Post.objects
    dates = p.dates('date', 'month', order='DESC')
    archives = []

    for date in dates:
        archive = {}
        archive['date'] = date
        archive['year'] = date.year
        archive['month'] = date.month
        archive['post_count'] = p.filter(date__month=date.month, date__year=date.year).count()
        archive['uri'] = reverse('blogapp.views.posts_by_date', args=[date.year, date.month])
        archives.append(archive)
    return archives

def tag_list():
    """
        Returns a list of dictionaries containing:
        - tag.title
        - tag.name
        - tag.uri
        - tag.size (for tag cloud)
        - tag.post_count
    """
    max_size = int(options('tag_cloud_font_size_max'))
    min_size = int(options('tag_cloud_font_size_min'))

    tags = Tag.objects.all()
    popular = max([tag.post_set.count() for tag in tags])
    s_range = max_size - min_size
    point = s_range / float(popular)
    cloud = []

    for tag in tags:
        post_count = tag.post_set.count()
        #only add tags with posts
        if post_count:
            t = {}
            t['title'] = tag.title
            t['name'] = tag.name
            t['uri'] = reverse('blogapp.views.posts_by_tag', args=[tag.name])
            t['size'] = int(round(min_size + post_count * point))
            t['post_count'] = post_count
            cloud.append(t)
    return cloud

def tracklist():
    """
        Gets user's tracklist from last.fm feed. Returns a list of dictionaries containing:
        - track.name (title)
        - track.artist
        - track.uri
    """

    username = options('lastfm_username')
    filepath = dirname(__file__) + '/lastfm.cache'
    modified_ago = time() - stat(filepath).st_mtime

    #this is used when file is fresh, or new content is corrupted
    try:
        local = open(filepath)
        tracklist = pickle.load(local)
        local.close()
    except:
        tracklist = []

    #update files older than 15 minutes
    if modified_ago > 900:
        try:
            remote = urlopen('http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.xml' % username)
            content = remote.read()
            remote.close()
        except:
            content = None

        #don't "update" cache with nothing
        if content:
            x = minidom.parseString(content)
            tracks = x.getElementsByTagName('track')
            if tracks:
                tracklist = []
                for track in tracks:
                    t = {}
                    t['name'] = track.getElementsByTagName('name')[0].childNodes[0].nodeValue
                    t['artist'] = track.getElementsByTagName('artist')[0].childNodes[0].nodeValue
                    t['uri'] = track.getElementsByTagName('url')[0].childNodes[0].nodeValue
                    tracklist.append(t)

                #pickle and store tracklist
                pickled = pickle.dumps(tracklist)
                local = open(filepath, 'w')
                local.write(pickled)
                local.close()

    return tracklist


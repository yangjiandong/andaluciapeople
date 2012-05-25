from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist

from blogapp.models import *
from blogapp.utilities import *
from blogapp.forms import CommentForm

from andaluciapeople.sitios.models import DatosUsuario

BLOG_TPL = 'blog.html'
#P_LIMIT = int(options('posts_per_page'))
P_LIMIT = 10

def homepage(request):
    pg = Paginator(Post.objects.all(), P_LIMIT)
    try:
        page_q = int(request.GET.get('page', 1))
    except ValueError:
        page_q = 1

    try:
        p = pg.page(page_q)
        posts = p.object_list
    except InvalidPage:
        return not_found(request, message=_("Sorry, the page does not exist."))
    context = {'posts': posts,
    		   'page': p,
    		   'options': options(),
    		  }
    return render_to_response(BLOG_TPL, context, context_instance=RequestContext(request))

def post_by_name(request, post_name):
    try:
        post = Post.objects.get(name=post_name)
    except ObjectDoesNotExist:
        return not_found(request, message=_("Sorry, the requested post does not exist."))

    #check if comments are enabled
    if not post.disable_comments:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                #result will either be a http redirect or an error string
                result = process_comment(request, post, form)
                if isinstance(result, unicode):
                    form = CommentForm(request.POST, auto_id=False)
                    form.errors['generic'] = result
                else:
                    #redirect
                    return result
            else:
                form.errors['generic'] = _("Check that the required fields are filled in correctly.")
        else:
            #values are pickled to enable unicode strings to be stored
            #unpickle_cookies(request)
            #form = CommentForm(request.COOKIES, auto_id=False)
			if request.user.is_authenticated():
			    form = CommentForm(initial = {
				    "author_name": request.user.username,
					"author_email": request.user.email,
					"author_website": DatosUsuario.objects.get(user=request.user).web
				})
			else:
			   form = CommentForm() 
    else:
        form = None

    #takes comments where comment_type is 'comment' or 'linkback'
    comments = post.comment_set.filter(comment_type='comment') | post.comment_set.filter(comment_type='linkback')
    context = {
        'posts': [post],
        'comments': comments,
        'title': post.title,
        'comment_form': form,
        'options': options(),
        }
    return render_to_response(BLOG_TPL, context, context_instance=RequestContext(request))

def posts_by_tag(request, tag_name):
    try:
        tag = Tag.objects.get(name=tag_name)
    except ObjectDoesNotExist:
        return not_found(request, message=_("Sorry, the tag you are searching for does not exist."))

    pg = Paginator(tag.post_set.all(), P_LIMIT)
    try:
        page_q = int(request.GET.get('page', 1))
    except ValueError:
        page_q = 1

    try:
        p = pg.page(page_q)
        posts = p.object_list
    except InvalidPage:
        return not_found(request, message=_("Sorry, the page does not exist."))
    context = {'posts': posts,
    		   'page': p,
    		   'options': options(),
    		  }
    return render_to_response(BLOG_TPL, context, context_instance=RequestContext(request))

def posts_by_date(request, year, month):
    posts = Post.objects.filter(date__year=year, date__month=month)
    if posts:
        pg = Paginator(posts, P_LIMIT)
        try:
            page_q = int(request.GET.get('page', 1))
        except ValueError:
            page_q = 1

        try:
            p = pg.page(page_q)
            posts = p.object_list
        except InvalidPage:
            return not_found(request, message=_("Sorry, the page does not exist."))
        context = {
					'posts': posts,
					'page': p,
					'options': options(),
				  }
        return render_to_response(BLOG_TPL, context, context_instance=RequestContext(request))
    else:
        return not_found(request, message=_("Sorry, there are no posts written that month."))

def page_by_name(request, page_name):
    try:
        page = Page.objects.get(name=page_name)
    except ObjectDoesNotExist:
        return not_found(request, message=_("Sorry, the requested page does not exist."))

    context = {
        'page': page,
        'title': page.title,
        'options': options(),
        }
    return render_to_response(BLOG_TPL, context, context_instance=RequestContext(request))

def feed(request, feed_type):
    posts = Post.objects.all()[:10]
    template = "feeds/%s.xml" % feed_type
    m_type = "application/xml"#"application/%s+xml" % feed_type
    updated = posts[0].date #used by atom
    context = {
        'posts': posts,
        'updated': updated,
        'options': options(),
        }
    return render_to_response(template, context, mimetype=m_type)

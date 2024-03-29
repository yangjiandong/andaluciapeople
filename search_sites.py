# Auto-discover all `search_indexes.py` and register.
# Most of the time, this is what you want.
try:
    from django.utils import importlib
except ImportError:
    from haystack.utils import importlib
    
def autodiscover():
    """
    Automatically build the site index.
    
    Again, almost exactly as django.contrib.admin does things, for consistency.
    """
    import imp
    from django.conf import settings
    
    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an search_indexes.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for search_indexes.py on that path.
        
        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own index registration.
        try:
            app_path = importlib.import_module(app).__path__
        except AttributeError:
            continue
        
        # Step 2: use imp.find_module to find the app's search_indexes.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its search_indexes.py doesn't exist
        try:
            imp.find_module('search_indexes', app_path)
        except ImportError:
            continue
        
        # Step 3: import the app's search_index file. If this has errors we want them
        # to bubble up.
        #print "Cargando %s" % app
        importlib.import_module("%s.search_indexes" % app)
        
autodiscover()


# Advanced `SearchSite` creation/registration. Rarely needed.
#from haystack.sites import SearchSite
#from andaluciapeople.sitios.models import Sitio
#mysite = SearchSite()
# mysite.register(Cat)
# ... or ...
#from andaluciapeople.sitios.search_indexes import SitioIndex
#mysite.register(Sitio, SitioIndex)

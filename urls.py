from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^comic/', include('comics.urls')),    
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/comic/'}),
)

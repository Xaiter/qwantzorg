from django.conf.urls.defaults import *

urlpatterns = patterns('comics.views',
    (r'^$', 'newComic'),    
    (r'^(?P<comicId>\d+)/$', 'viewComic'),
    (r'^login/$', 'login'),
    (r'^account/create/$', 'createAccount'),
    (r'^account/reset/$', 'resetPasswordRequest'),
    (r'^account/reset/(?P<activationKey>[a-zA-Z0-9]+)$', 'resetPassword'),
    (r'^account/reset/sent/$', 'resetPasswordSent'),
    (r'^account/logout$', 'logout'),
    (r'^account/create/thanks/$', 'createAccountThanks'),
    (r'^account/activate/(?P<activationKey>[a-zA-Z0-9]+)$', 'activateAccount'),
    (r'^about$', 'about'),
)

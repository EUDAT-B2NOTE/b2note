from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^register$', 'accounts.views.register', name='register'),
    url(r'^login$', 'accounts.views.login', name='login'),
    url(r'^consolelogin$', 'accounts.views.consolelogin', name='consolelogin'),
    url(r'^logout$', 'accounts.views.logout', name='logout'),
    url(r'^profilepage$', 'accounts.views.profilepage', name='profile'),
)

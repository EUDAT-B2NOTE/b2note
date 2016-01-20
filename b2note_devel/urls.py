from django.conf.urls import patterns, include, url
#import searchapp, testsearch


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'b2note_devel.views.home', name='home'),
    # url(r'^b2note_devel/', include('b2note_devel.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'searchapp.views.hostpage', name='index'),
    url(r'^hostpage', 'searchapp.views.hostpage'),
    url(r'^interface_main', 'searchapp.views.interface_main'),
    url(r'^create_annotation', 'searchapp.views.create_annotation'),
    url(r'^delete_annotation', 'searchapp.views.delete_annotation'),
)

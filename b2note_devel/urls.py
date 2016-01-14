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
    url(r'^$', 'searchapp.views.index', name='index'),
    url(r'^search/$', 'searchapp.views.typeahead', name='typeahead'),
    url(r'^search/', 'searchapp.views.ontology_search', name='ontology_search'),
    url(r'^testsearch/', 'testsearch.views.search', name='test_search'),
    url(r'^hostpage', 'searchapp.views.hostpage'),
    url(r'^interface_main', 'searchapp.views.interface_main'),
)

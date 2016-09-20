from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^$', 'accounts.views.login', name='index'),
    url(r'^login', 'accounts.views.login'),

    url(r'^hostpage', 'b2note_app.views.hostpage'),
    url(r'^homepage$', 'b2note_app.views.homepage', name='homepage'),
    url(r'^interface_main', 'b2note_app.views.interface_main'),
    url(r'^create_annotation', 'b2note_app.views.create_annotation'),
    url(r'^delete_annotation', 'b2note_app.views.delete_annotation'),
    url(r'^export', 'b2note_app.views.export_annotations'),
    url(r'^download_json', 'b2note_app.views.download_json'),
    url(r'^publish', 'b2note_app.views.publish_annotations'),
    url(r'^settings', 'b2note_app.views.settings'),
    url(r'^search', 'b2note_app.views.search_annotations'),
    url(r'^retrieve_annotations', 'b2note_app.views.retrieve_annotations'),
)

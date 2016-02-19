from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'searchapp.views.hostpage', name='index'),
    url(r'^hostpage', 'searchapp.views.hostpage'),
    url(r'^interface_main', 'searchapp.views.interface_main'),
    url(r'^create_annotation', 'searchapp.views.create_annotation'),
    url(r'^delete_annotation', 'searchapp.views.delete_annotation'),
    url(r'^export', 'searchapp.views.export_annotations'),
    url(r'^download_json', 'searchapp.views.download_json'),
    url(r'^publish', 'searchapp.views.publish_annotations'),
    url(r'^settings', 'searchapp.views.settings'),
)

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^$', 'b2note_app.views.hostpage', name='index'),
    url(r'^login', 'accounts.views.login'),
    url(r'^logout', 'accounts.views.logout'),
    url(r'^hostpage', 'b2note_app.views.hostpage'),
    url(r'^interface_main', 'b2note_app.views.interface_main'),
    url(r'^create_annotation', 'b2note_app.views.create_annotation'),
    url(r'^delete_annotation', 'b2note_app.views.delete_annotation'),
    url(r'^export', 'b2note_app.views.export_annotations'),
    url(r'^download_json', 'b2note_app.views.download_json'),
    url(r'^download_rdfxml', 'b2note_app.views.download_rdfxml'),
    url(r'^publish', 'b2note_app.views.publish_annotations'),
    url(r'^settings', 'b2note_app.views.settings'),
    url(r'^search', 'b2note_app.views.search_annotations'),
    url(r'^retrieve_annotations', 'b2note_app.views.retrieve_annotations'),
    url(r'^edit_annotation', 'b2note_app.views.edit_annotation'),
    url(r'^help$', 'b2note_app.views.helppage'),
    url(r'^allannotations$', 'b2note_app.views.allannotations'),
    url(r'^myannotations$', 'b2note_app.views.myannotations'),
    url(r'^annotation_summary$', 'b2note_app.views.annotation_summary'),
    url(r'^select_search_results$', 'b2note_app.views.select_search_results'),
    url(r'^json_sample$', 'b2note_app.views.json_sample'),
    url(r'^(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'b2note_app.views.hostpage', name='reset_password_test'),
)

#UPGRADE patterns obsolete - use plain old list [ ];
# from django.conf.urls import patterns, include, url
import captcha
from django.conf.urls import include,url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
import accounts
from b2note_app import views as b2note_app_views
from accounts import views as accounts_views 

urlpatterns = [
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^accounts/', include(('accounts.urls','accounts'), namespace='accounts')),
    url(r'^$', b2note_app_views.hostpage, name='index'),
    url(r'^login', accounts_views.login),
    url(r'^logout', accounts_views.logout),
    url(r'^hostpage', b2note_app_views.hostpage),
    url(r'^interface_main', b2note_app_views.interface_main),
    url(r'^create_annotation', b2note_app_views.create_annotation),
    url(r'^delete_annotation', b2note_app_views.delete_annotation),
    url(r'^export', b2note_app_views.export_annotations),
    url(r'^download_json', b2note_app_views.download_json),
    url(r'^download_rdfxml', b2note_app_views.download_rdfxml),
    url(r'^publish', b2note_app_views.publish_annotations),
    url(r'^settings', b2note_app_views.settings),
    url(r'^search', b2note_app_views.search_annotations),
    url(r'^retrieve_annotations', b2note_app_views.retrieve_annotations),
    url(r'^edit_annotation', b2note_app_views.edit_annotation),
    url(r'^help$', b2note_app_views.helppage),
    url(r'^allannotations$', b2note_app_views.allannotations),
    url(r'^myannotations$', b2note_app_views.myannotations),
    url(r'^annotation_summary$', b2note_app_views.annotation_summary),
    url(r'^select_search_results$', b2note_app_views.select_search_results),
    url(r'^json_sample$', b2note_app_views.json_sample),
    url(r'^(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', b2note_app_views.hostpage, name='reset_password_test'),
]

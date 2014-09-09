from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from b2noteapi import views

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'ontologies', views.OntologiesViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'b2note.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^query/', include('query.urls', namespace='query')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^$', include('query.urls', namespace='query')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

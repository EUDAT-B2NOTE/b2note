from django.conf.urls import patterns, url

from query import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^query/query_vocab/$',views.query_vocab,name='query_vocab'),
    url(r'^query/query_file/$',views.query_file,name='query_file'),
    url(r'^query/list/$', 'list', name='list'),
)

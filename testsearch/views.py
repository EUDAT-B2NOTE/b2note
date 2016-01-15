from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from .models import DataTest


def search(request):
     print "type ahead"
     return render_to_response('testsearch/search.html')


def ontology_search(request):
    print "onto search"
    context = RequestContext(request)
    context_dict = {}
    if request.method == 'GET':
        print 'pressed'
        print request
        #search_string = request.GET['query']
        #print request.GET['query']

        # Adds our results list to the template context under name pages.
        #context_dict['search_string'] = search_string

    return render_to_response('testsearch/search.html', context_dict, context)

def save_data(request):
    ontoId = request.POST.get('ontoId')
    labels = request.POST.get('labels')

    data = DataTest.objects.create(ontoId=ontoId, labels=labels)
    data.save()

def fetch_data(request):
    datatestlist = DataTest.objects.all()

    context = RequestContext(request, {
                 'datatestlist': datatestlist,
	         })

    return render_to_response('testsearch/test.html', context)

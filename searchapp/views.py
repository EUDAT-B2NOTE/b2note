from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from .models import Annotation


def index(request):
    return HttpResponse("replace me with index text")



def typeahead(request):
     print "type ahead"
     return render_to_response('searchapp/search.html')


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

    return render_to_response('searchapp/search.html', context_dict, context)


def hostpage(request):
    return render(request, 'searchapp/hostpage.html', {'iframe_on': 350})


def interface_main(request):
    annotation_list = Annotation.objects.all()
    if request.POST.get('subject_tofeed')==None:
        context = RequestContext(request, {
	        'annotation_list': annotation_list,
            'subject_tofeed': ""
        })
    else:
        print request.POST.get('subject_tofeed')
        context = RequestContext(request, {
	        'annotation_list': annotation_list,
            'subject_tofeed': request.POST.get('subject_tofeed'),
        })
    return render_to_response('searchapp/interface_main.html', context)





'''
from searchapp import models
models.Annotation(\
    triple=models.Triple(\
        subject=models.TripleElement(\
            iri="https://b2share.eudat.eu/record/30",\
            label="Orthography-based dating and localisation of Middle Dutch charters",\
            definition="",\
	        curation_status="",\
	        ontology_iri="",\
	        ontology_shortname="",\
	        ontology_version="",\
        ),\
        predicate=models.TripleElement(\
            iri="http://purl.obolibrary.org/obo/IAO_0000136",\
            label="is about",\
            definition="Is_about is a (currently) primitive relation that relates an information artifact to an entity.",\
	        curation_status="pending final vetting",\
	        ontology_iri="http://purl.obolibrary.org/obo/iao.owl",\
	        ontology_shortname="IAO",\
	        ontology_version="2015,02,23",\
        ),\
        object=models.TripleElement(\
            iri="http://purl.obolibrary.org/obo/NCBITaxon_3262",\
            label="Dutch rush",\
            definition="",\
	        curation_status="",\
	        ontology_iri="http://purl.obolibrary.org/obo/ncbitaxon.owl",\
	        ontology_shortname="ncbitaxon",\
	        ontology_version="2015,10,07",\
        ),\
    ),\
    provenance=models.Provenance(\
      createdBy="abremaud@esciencefactory.com",
    ),\
).save()
'''

#models.Annotation(\
    # triple=models.Triple(\
    #   subject=models.TripleElement(iri='https://b2share.eudat.eu/record/30'), \
    # predicate=models.TripleElement(iri='http://purl.obolibrary.org/obo/IAO_0000136', \
    # label='is about', \
    # definition='Is_about is a (currently) primitive relation that relates an information artifact to an entity.', \
    # curation_status='pending final vetting', \
    # ontology_iri='http://purl.obolibrary.org/obo/iao.owl', \
    # ontology_shortname='IAO', ontology_version = '2015,02,23'), \
    # object=models.TripleElement(iri='http://purl.obolibrary.org/obo/NCBITaxon_3262',label='Dutch rush')), provenance=models.Provenance( createdBy = 'abremaud@esciencecfactory.com' )).save()
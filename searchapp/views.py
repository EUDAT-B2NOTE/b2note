from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django_mongodb_engine.query import A

from .mongo_support_functions import *
from .models import Annotation

import json



def index(request):
    return HttpResponse("replace me with index text")


# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
def export_annotations(request):
    """
      Function: export_annotations
      ----------------------------
        Export all annotations in JSON format.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the result of the request.
    """
    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    response = []
    # filter by subject_tofeed:
    #annotation_list = Annotation.objects.raw_query({'triple.subject.iri': subject_tofeed})
    #annotation_list = Annotation.objects.raw_query({})
    annotation_list = [dict(item) for item in Annotation.objects.all().values()]

    #annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    response = model_class_as_string( annotation_list )

    # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
    json_data = HttpResponse(json.dumps(response), mimetype= 'application/json')
    json_data['Content-Disposition'] = 'attachment; filename=annotations.json'
    download_json.file_data = json_data
    
    return render(request, 'searchapp/export.html', {'annotations_json': json.dumps(response),"subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })


def download_json(request):
    """
      Function: download_json
      ----------------------------
        Download a json file with the annotations 
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the file to download.
    """
    return download_json.file_data


# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
def publish_annotations(request):
    """
      Function: publish_annotations
      ----------------------------
        Make annotations available to SPARQL queries.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the result of the request.
    """
    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    text = """
    This functionality will publish selected annotations to a triplestore making them accessible to SPARQL queries.
    """
    return render(request, 'searchapp/default.html', {'text': text,"subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })


# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
def settings(request):
    """
      Function: settings
      ----------------------------
        Select the source of ontologies.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the result of the request.
    """
    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    text = """
    This functionality will allow the user to select the ontologies from which to retrieve the concepts used for creating annotations.
    """
    return render(request, 'searchapp/default.html', {'text': text,"subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })


def hostpage(request):
    """
      Function: hostpage
      ----------------------------
        Displays the initial page of the site.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the initial host page.
    """

    buttons_info_text = """
http://hdl.handle.net/11304/31c0d886-b988-11e3-8cd7-14feb57d12b9
https://b2share.eudat.eu/record/30
Orthography-based dating and localisation of Middle Dutch charters

http://hdl.handle.net/11304/3522daa6-b988-11e3-8cd7-14feb57d12b9
https://b2share.eudat.eu/record/45
ImageJ plugin ColonyArea

http://hdl.handle.net/11304/6a9078c4-c3b0-11e3-8cd7-14feb57d12b9
https://b2share.eudat.eu/record/66
REST paper 2014

http://hdl.handle.net/11304/69430fd2-e7d6-11e3-b2d7-14feb57d12b9
https://b2share.eudat.eu/record/88
piSVM Analytics Runtimes JUDGE Cluster Rome Images 55 Features

http://hdl.handle.net/11304/fe356a8e-3f2b-11e4-81ac-dcbd1b51435e
https://b2share.eudat.eu/record/125
GoNL SNPs and Indels release 5

http://hdl.handle.net/11304/9061f60c-41cf-11e4-81ac-dcbd1b51435e
https://b2share.eudat.eu/record/127
Influence of smoking and obesity in sperm quality
    """

    buttons_info, k = [], 1
    file_pid, file_url, link_label = "", "", ""
    for line in buttons_info_text.splitlines():
        if file_pid!="" and file_url!="" and link_label!="":
            buttons_info.append({\
                "file_pid":file_pid,\
                "file_url":file_url,\
                "link_label":link_label,\
                "button_n":"button"+str(k),\
            })
            k += 1
            file_pid, file_url, link_label = "", "", ""
        if "http://hdl.handle.net" in line:
            file_pid = line
        elif "https://b2share.eudat.eu/record" in line:
            file_url = line
        elif line != "":
            link_label = line

    return render(request, 'searchapp/hostpage.html', {'iframe_on': 350, 'buttons_info':buttons_info})



# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
def delete_annotation(request):
    """
      Function: delete_annotation
      ----------------------------
        Calls DeleteFromPOSTinfo function for removing an annotation.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the remaining annotations.
    """

    if request.POST.get('db_id'):
        DeleteFromPOSTinfo( request.POST.get('db_id') )

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    try:
        annotation_list = Annotation.objects.filter( target = A('jsonld_id', subject_tofeed) )
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    context = RequestContext(request, {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
    })
    return render_to_response('searchapp/interface_main.html', context)



# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
def create_annotation(request):
    """
      Function: create_annotation
      ----------------------------
        Calls CreateFromPOSTinfo function for creating a new annotation.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the annotations.
    """

    if request.POST.get('ontology_json'):
        CreateFromPOSTinfo( request.POST.get('subject_tofeed'), request.POST.get('ontology_json') )

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    try:
        annotation_list = Annotation.objects.filter( target = A('jsonld_id', subject_tofeed) )
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    context = RequestContext(request, {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
    })
    return render_to_response('searchapp/interface_main.html', context)



# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
def interface_main(request):
    """
      Function: interface_main
      ----------------------------
        Displays the iframe with the annotations.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the iframe.
    """

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    #http://stackoverflow.com/questions/5508888/matching-query-does-not-exist-error-in-django
    try:
        # https://blog.scrapinghub.com/2013/05/13/mongo-bad-for-scraped-data/
        # https://github.com/aparo/django-mongodb-engine/blob/master/docs/embedded-objects.rst
        annotation_list = Annotation.objects.filter( target = A('jsonld_id', subject_tofeed) )
        #print "==>", type(annotation_list), len(annotation_list)
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    context = RequestContext(request, {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
    })
    return render_to_response('searchapp/interface_main.html', context)
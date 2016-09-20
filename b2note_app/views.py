import json
import os

from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings as global_settings
from django.core import serializers
from django.forms.models import model_to_dict

from collections import OrderedDict

from .mongo_support_functions import *
from .models import *

from accounts.models import AnnotatorProfile


def index(request):
    return HttpResponse("replace me with index text")


@login_required
def homepage(request):
    """
    User profile view.
    """
    try:
        if request.session.get("user"):

            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))

            annotation_list = RetrieveAnnotations_perUsername( userprofile.nickname )

            file_list = list(annotation_list)

            file_list = set([k.target[0].jsonld_id for k in file_list])

            context = RequestContext(request, {
                'userprofile': userprofile,
                'annotation_list': annotation_list,
                'file_list': file_list})
            return render_to_response('b2note_app/homepage.html', context_instance=context)
        else:
            print "Redirecting from homepage view."
            return redirect('/accounts/logout')
    except Exception:
        print "Could not load or redirect from homepage view."
        return False


# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
@login_required
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
    try:
        subject_tofeed = ""
        if request.POST.get('subject_tofeed')!=None:
            subject_tofeed = request.POST.get('subject_tofeed')

        pid_tofeed = ""
        if request.POST.get('pid_tofeed')!=None:
            pid_tofeed = request.POST.get('pid_tofeed')

        if request.session.get("user"):

            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))

            annotation_list = RetrieveAnnotations_perUsername(userprofile.nickname)

            """
            abremaud@esciencedatalab.com, 20160303
            Upon testing on json-ld online playground, none of the URLs provided in current
             web annotation specification document allowed the context to be retrieved
             with likely origin of trouble being CORS.
            As a consequence we resort here to embedding rather than linking to the context.
            """
            context_str = open(os.path.join(global_settings.STATIC_PATH, 'files/anno_context.jsonld'), 'r').read()

            response = {"@context": json.loads( context_str, object_pairs_hook=OrderedDict ) }

            response["@graph"] = readyQuerySetValuesForDumpAsJSONLD( annotation_list )

            # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
            json_data = HttpResponse(json.dumps(response, indent=2), mimetype= 'application/json')
            json_data['Content-Disposition'] = 'attachment; filename=annotations.json'
            download_json.file_data = json_data

            return render(request, 'b2note_app/export.html', {'annotations_json': json.dumps(response, indent=2),"subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })
        else:
            print "Redirecting from export view."
            return redirect('/accounts/logout')
    except Exception:
        print "Could not export or redirect from export view."
        return False


@login_required
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
@login_required
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
    return render(request, 'b2note_app/default.html', {'text': text,"subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })


# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
@login_required
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
    
    return render(request, 'b2note_app/default.html', {'text': text,"subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })


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

    return render(request, 'b2note_app/hostpage.html', {'iframe_on': 350, 'buttons_info':buttons_info})



# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
@login_required
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

    pagefrom = ""
    if request.POST.get('pagefrom')!=None:
        pagefrom = request.POST.get('pagefrom')

    try:
        annotation_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    context = RequestContext(request, {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'pagefrom': pagefrom,
    })
    if pagefrom == 'homepage':
        return redirect('/homepage')
    else:
        return render_to_response('b2note_app/interface_main.html', context)



# forbidden CSRF verification failed. Request aborted.
@csrf_exempt
@login_required
def create_annotation(request):
    """
      Function: create_annotation
      ----------------------------
        Calls CreateSemanticTag function for creating a new annotation.
        
        input:
            request (object): context of the petition.
        
        output:
            object: HttpResponse with the annotations.
    """
    ann_id1 = None
    ann_id2 = None
    if request.POST.get('ontology_json'):
        ann_id1 = CreateSemanticTag( request.POST.get('subject_tofeed'), request.POST.get('ontology_json') )
        if request.session.get('user'):
            ann_id2 = SetUserAsAnnotationCreator( request.session.get('user'), ann_id1 )
        else:
            print "No user in session, can not attribute creator to semantic tag annotation:", ann_id1

    if request.POST.get('free_text'):
        ann_id1 = CreateFreeText( request.POST.get('subject_tofeed'), request.POST.get('free_text') )
        if request.session.get('user'):
            ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1 )
        else:
            print "No user in session, can not attribute creator to free text annotation:", ann_id1

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    pagefrom = ""
    if request.POST.get('pagefrom')!=None:
        pagefrom = request.POST.get('pagefrom')

    try:
        annotation_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    context = RequestContext(request, {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'pagefrom': pagefrom,
    })
    if pagefrom == 'homepage':
        return redirect('/homepage', context_instance=context)
    else:
        return render_to_response('b2note_app/interface_main.html', context)


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

    request.session["is_console_access"] = True

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)

    pagefrom = ""
    if request.POST.get('pagefrom')!=None:
        pagefrom = request.POST.get('pagefrom')

    #http://stackoverflow.com/questions/5508888/matching-query-does-not-exist-error-in-django
    try:
        # https://blog.scrapinghub.com/2013/05/13/mongo-bad-for-scraped-data/
        # https://github.com/aparo/django-mongodb-engine/blob/master/docs/embedded-objects.rst
        annotation_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
        #print "==>", type(annotation_list), len(annotation_list)
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    context = RequestContext(request, {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'pagefrom': pagefrom,
    })
    return render_to_response('b2note_app/interface_main.html', context)


@csrf_exempt
@login_required
def search_annotations(request):
    return HttpResponse("Search annotations functionality is coming.")


@csrf_exempt
@login_required
def retrieve_annotations(request):
    """
      Function: retrieve_annotations
      ----------------------------
        Retrieves a jsonld with annotations matching with the file in the request
        
        input:
            request (object): context of the petition.
        
        output:
            object: jsonld
    """
    target_id = ""
    if request.GET.get('target_id') != None:
        target_id = request.GET.get('target_id')
    
    annotations = RetrieveAnnotations(target_id)
    
    
    return HttpResponse(annotations)


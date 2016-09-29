import json
import os
import requests
import copy

from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings as global_settings

from collections import OrderedDict

from .mongo_support_functions import *
from .models import *

from itertools import chain

from accounts.models import AnnotatorProfile




def index(request):
    return HttpResponse("replace me with index text")


@login_required
def edit_annotation(request):
    A=None
    owner=False
    error_loc=[]
    try:

        error_loc.append(1)

        if request.session.get("user"):

            error_loc.append(2)

            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))

            error_loc.append(3)

            #annotation_list = RetrieveAnnotations_perUsername(userprofile.nickname)

            if request.POST.get('db_id'):

                error_loc.append(4)

                if isinstance(request.POST.get('db_id'), (str, unicode)):

                    error_loc.append(5)

                    #A = Annotation.objects.get(id="57e1504510d06010314becc8")
                    #A = Annotation.objects.get(id="57dfd3fe10d0600412d056df")
                    A = Annotation.objects.get(id=request.POST.get('db_id'))

                    error_loc.append(6)

                    if A:

                        error_loc.append(7)

                        owner = userprofile.nickname == A.creator[0].nickname

                        error_loc.append(8)

                        if request.POST.get('duplicate_cmd'):

                            error_loc.append(9)

                            db_id = None

                            if A.body[0].jsonld_id:

                                error_loc.append(10)

                                onto_json = json.dumps({'uris': A.body[0].jsonld_id, 'labels': A.body[0].value})
                                db_id = CreateSemanticTag( A.target[0].jsonld_id, onto_json )

                                error_loc.append(11)

                            else:

                                error_loc.append(12)

                                db_id = CreateFreeText( A.target[0].jsonld_id, A.body[0].value )

                                error_loc.append(13)

                            if db_id:

                                error_loc.append(14)

                                db_id = SetUserAsAnnotationCreator( request.session.get('user'), db_id )
                                A     = Annotation.objects.get( id = db_id )
                                owner = userprofile.nickname == A.creator[0].nickname

                                error_loc.append(15)

                            else:
                                print "Edit_annotation view, annotation could not be duplicated."
                                pass

                        elif owner and request.POST.get('delete_cmd'):

                            error_loc.append(16)

                            if request.POST.get('delete_cmd')=='delete_cmd' and request.POST.get('db_id'):

                                error_loc.append(17)

                                DeleteFromPOSTinfo(request.POST.get('db_id'))
                                return redirect('/homepage')

                            else:
                                print "Edit_annotation view, POST parameter 'db_id' is None."
                                pass

                        elif owner:

                            error_loc.append(18)

                            if request.POST.get('ontology_json'):

                                error_loc.append(19)

                                db_id = MakeAnnotationSemanticTag( A.id, request.POST.get('ontology_json') )
                                A = Annotation.objects.get(id=db_id)

                                error_loc.append(20)

                            elif request.POST.get('free_text'):

                                error_loc.append(21)

                                if isinstance(request.POST.get('free_text'), (str, unicode)):

                                    error_loc.append(22)

                                    if request.POST.get('free_text') != A.body[0].value:

                                        error_loc.append(23)

                                        db_id = None
                                        db_id = MakeAnnotationFreeText( A.id, request.POST.get('free_text') )

                                        error_loc.append(24)

                                        if db_id: A = Annotation.objects.get( id = db_id )

                                        error_loc.append(25)

                                    else:
                                        print "Edit_annotation view, not editing due to entered text identical to existing body value."
                                        pass
                                else:
                                    print "Edit_annotation view, provided POST argument 'body.change' does not contain valid str or unicode."
                                    pass

                            if request.POST.get('motivation_selection'):

                                error_loc.append(26)

                                motiv = request.POST.get('motivation_selection')

                                error_loc.append(27)

                                if isinstance(motiv, (str, unicode)):

                                    error_loc.append(28)

                                    db_id = None
                                    db_id = SetAnnotationMotivation( A.id, motiv )

                                    error_loc.append(29)

                                    if db_id: A = Annotation.objects.get( id = db_id )

                                    error_loc.append(30)

                    else:
                        print "Edit_annotation view, could not retrieve annotation with id:", str( request.POST.get('db_id') )
                        pass
                else:
                    print "Edit_annotation view, POST request contains object called 'db_id' that is neither str nor unicode."
                    pass
        else:
            print "Edit_annotation view, unidentified user."
            return redirect('accounts/logout')

    except:
        print "Edit_annotation view did not complete."
        return HttpResponse(json.dumps(error_loc))

    motivation_choices = Annotation.MOTIVATION_CHOICES

    context = RequestContext(request, {"form": A, "owner": owner, "motivation_choices": motivation_choices})
    return render(request, "b2note_app/edit_annotation.html", context)


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

            annotation_list = annotation_list.values()

            """
            abremaud@esciencedatalab.com, 20160303
            Upon testing on json-ld online playground, none of the URLs provided in current
             web annotation specification document allowed the context to be retrieved
             with likely origin of trouble being CORS.
            As a consequence we resort here to embedding rather than linking to the context.
            """
            context_str = open(os.path.join(global_settings.STATIC_PATH, 'files/anno_context.jsonld'), 'r').read()

            response = {"@context": json.loads( context_str, object_pairs_hook=OrderedDict ) }

            response["@graph"] = readyQuerySetValuesForDumpAsJSONLD( [ann for ann in annotation_list] )

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

    user_nickname = None
    if request.session.get("user"):
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname
        if request.POST.get('db_id'):
            if isinstance(request.POST.get('db_id'), (str, unicode)):
                A = Annotation.objects.get(id=request.POST.get('db_id'))
                if A:
                    owner = userprofile.nickname == A.creator[0].nickname
                    if owner:
                        DeleteFromPOSTinfo( request.POST.get('db_id') )
                    else:
                        print "delete_annotation view, cannot delete annotation, current user is not owner."
                        pass
                else:
                    print "delete_annotation view, no annotation with provided 'db_id':", str( request.POST.get('db_id') )
                    pass
            else:
                print "delete_annotation view, provided parameter 'db_id' neither str nor unicode."
                pass
        else:
            print "delete_annotation view, missing POST parameter 'db_id'."
            pass
    else:
        print "delete_annotation view, user is not logged-in."
        pass

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

    data_dict = {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'pagefrom': pagefrom,
        'user_nickanme': user_nickname}
    if pagefrom == 'homepage':
        return redirect('/homepage')
    else:
        return render(request, 'b2note_app/interface_main.html', data_dict)


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
    user_nickname = None
    if request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

        ann_id1 = None
        ann_id2 = None
        if request.POST.get('ontology_json'):
            ann_id1 = CreateSemanticTag( request.POST.get('subject_tofeed'), request.POST.get('ontology_json') )
            ann_id2 = SetUserAsAnnotationCreator( request.session.get('user'), ann_id1 )

        if request.POST.get('free_text'):
            ann_id1 = CreateFreeText( request.POST.get('subject_tofeed'), request.POST.get('free_text') )
            ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1 )

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

    data_dict = {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'pagefrom': pagefrom,
        'user_nickname': user_nickname}
    if pagefrom == 'homepage':
        return redirect('/homepage', context_instance=RequestContext(request, data_dict))
    else:
        return render(request, 'b2note_app/interface_main.html', data_dict)


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

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/consolelogin', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    pagefrom = ""
    if request.POST.get('pagefrom')!=None:
        pagefrom = request.POST.get('pagefrom')

    #http://stackoverflow.com/questions/5508888/matching-query-does-not-exist-error-in-django
    try:
        # https://blog.scrapinghub.com/2013/05/13/mongo-bad-for-scraped-data/
        # https://github.com/aparo/django-mongodb-engine/blob/master/docs/embedded-objects.rst
        annotation_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
        #print "### " * 20
        #print json.dumps(readyQuerySetValuesForDumpAsJSONLD( [item for item in annotation_list.values()] ), indent=2)
        #print "### " * 20
    except Annotation.DoesNotExist:
        annotation_list = []

    annotation_list = sorted(annotation_list, key=lambda Annotation: Annotation.created, reverse=True)

    data_dict = {
        'annotation_list': annotation_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'pagefrom': pagefrom,
        'user_nickname': user_nickname}
    return render(request, 'b2note_app/interface_main.html', data_dict)


@login_required
def search_annotations(request):

    keywd_json = None
    label_match = None
    synonym_match = None

    if request.POST.get('ontology_json'):

        keywd_json = request.POST.get('ontology_json')

        keywd_json = json.loads( keywd_json )

        if keywd_json:

            if isinstance(keywd_json, dict):

                if "labels" in keywd_json.keys():

                    if keywd_json["labels"]:

                        if isinstance(keywd_json["labels"], (str, unicode)):

                            if keywd_json["labels"].lower() != keywd_json["labels"]:

                                label_match = list(chain(SearchAnnotation( keywd_json["labels"] ), SearchAnnotation( keywd_json["labels"].lower() )))

                            else:

                                label_match = list(chain(SearchAnnotation(keywd_json["labels"]),))

                            r = requests.get('https://b2note.bsc.es/solr/b2note_index/select?q=synonyms:"'+ keywd_json["labels"] +'"&fl=labels&wt=json&indent=true&rows=1000')

                            r = r.json()

                            if synonym_match is None: synonym_match = []

                            if r:

                                if isinstance(r, dict):

                                    if "response" in r.keys():

                                        if r["response"]:

                                            if isinstance(r["response"], dict):

                                                if "docs" in r["response"].keys():

                                                    if isinstance(r["response"]["docs"], list):

                                                        for syn_match in r["response"]["docs"]:

                                                            if syn_match:

                                                                if isinstance(syn_match, dict):

                                                                    if "labels" in syn_match.keys():

                                                                        if syn_match["labels"]:

                                                                            if isinstance(syn_match["labels"], (str, unicode)):

                                                                                synonym_match.append(
                                                                                    SearchAnnotation(
                                                                                        syn_match["labels"]))

                                                                                if syn_match["labels"].lower() != syn_match["labels"]:

                                                                                    synonym_match.append(
                                                                                        SearchAnnotation(
                                                                                            syn_match[
                                                                                                "labels"].lower()))


                if "synonyms" in keywd_json.keys():

                    if keywd_json["synonyms"]:

                        if isinstance(keywd_json["synonyms"], list):

                            for syn in keywd_json["synonyms"]:

                                if isinstance( syn, (str, unicode) ):

                                    if synonym_match is None: synonym_match = []

                                    synonym_match.append( SearchAnnotation( syn ) )

                                    r = requests.get('https://b2note.bsc.es/solr/b2note_index/select?q=synonyms:"' + syn + '"&fl=labels&wt=json&indent=true&rows=1000')

                                    r = r.json()

                                    if r:

                                        if isinstance(r, dict):

                                            if "response" in r.keys():

                                                if r["response"]:

                                                    if isinstance(r["response"], dict):

                                                        if "docs" in r["response"].keys():

                                                            if isinstance(r["response"]["docs"], list):

                                                                for syn_match in r["response"]["docs"]:

                                                                    if syn_match:

                                                                        if isinstance(syn_match, dict):

                                                                            if "labels" in syn_match.keys():

                                                                                if syn_match["labels"]:

                                                                                    if isinstance(syn_match["labels"], (str, unicode)):

                                                                                        synonym_match.append(
                                                                                            SearchAnnotation(
                                                                                                syn_match["labels"]))

                                                                                        if syn_match["labels"].lower() != syn_match[
                                                                                                    "labels"]:

                                                                                            synonym_match.append(
                                                                                                SearchAnnotation(
                                                                                                    syn_match[
                                                                                                        "labels"].lower()))

    # Avoid duplicate results being returned in synonym_match:

    id_list = []

    if label_match:

        for qsv in label_match:

            if qsv.jsonld_id:

                if qsv.jsonld_id not in id_list:

                    id_list.append(qsv.jsonld_id)

    pre_synonym_match = None

    if synonym_match:

        pre_synonym_match = copy.deepcopy(synonym_match)

        synonym_match = []

    if pre_synonym_match:

        for qs in pre_synonym_match:

            for qsv in qs.values():

                if isinstance(qsv, dict):

                    if "jsonld_id" in qsv.keys():

                        if qsv["jsonld_id"]:

                            if qsv["jsonld_id"] not in id_list:

                                id_list.append(qsv["jsonld_id"])

                                synonym_match.append(qs)

    return render(request, "b2note_app/searchpage.html", {'keywd_json': keywd_json,'label_match': label_match, 'synonym_match':synonym_match})


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


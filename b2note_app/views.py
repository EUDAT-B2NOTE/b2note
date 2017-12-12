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
from .nav_support_functions import list_navbarlinks, list_shortcutlinks
#from .ext_api_support_functions import b2share_api_get_file_info_on_url

from itertools import chain

from accounts.models import AnnotatorProfile
import logging

from rdflib import Graph, plugin, term
from rdflib.serializer import Serializer


stdlogger = logging.getLogger('b2note')


def b2share_correct_url( url ):
    out = None
    try:
        if url and isinstance(url, (str, unicode)) and len(url)>0:
            if url[:len("http://trng-b2share.eudat.eu")] == "http://trng-b2share.eudat.eu" \
                    or url[:len("https://trng-b2share.eudat.eu")]=="https://trng-b2share.eudat.eu" \
                    or url[:len("https://b2share.eudat.eu")]=="https://b2share.eudat.eu" \
                    or url[:len("http://b2share.eudat.eu")]=="http://b2share.eudat.eu":
                out = url
            else:
                if url[0]=="/":
                    out = "https://trng-b2share.eudat.eu"+url
                else:
                    out = "https://trng-b2share.eudat.eu"+"/"+url
        else:
            print "B2share_correct_url function, URL not valid or too short."
            stdlogger.error("B2share_correct_url function, URL not valid or too short.")
    except:
        print "B2share_correct_url function did not complete succesfully."
        stdlogger.error("B2share_correct_url function did not complete succesfully.")
    return out



def index(request):
    return HttpResponse("replace me with index text")



@login_required
def typeahead_testbench(request):
    return render(request, "b2note_app/typeahead_testbench.html")


@login_required
def json_sample(request):
    print os.getcwd()
    nf = open("static/files/sample.json", "r")
    jsondt = nf.read()
    print json.dumps(jsondt, indent=2)
    nf.close()
    json_data = HttpResponse(json.dumps(jsondt, indent=2), mimetype= 'application/json')
    return json_data



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
        if request.POST.get('subject_tofeed') != None:
            subject_tofeed = request.POST.get('subject_tofeed')
            if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
            request.session["subject_tofeed"] = subject_tofeed
        elif request.session.get('subject_tofeed'):
            subject_tofeed = request.session.get('subject_tofeed')
            if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

        pid_tofeed = ""
        if request.POST.get('pid_tofeed') != None:
            pid_tofeed = request.POST.get('pid_tofeed')

        user_nickname = None
        userprofile = None
        if request.session.get("user"):
            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
            user_nickname = userprofile.nickname

        response = None
        annotation_list = None
        annotations_of = None

        if subject_tofeed and isinstance(subject_tofeed, (str, unicode)):

            if request.POST.get('user_annotations') != None and user_nickname:
                annotation_list = RetrieveUserAnnotations(user_nickname)
                annotation_list = annotation_list.values()
                annotations_of = "mine"

            elif request.POST.get('all_annotations') != None:
                annotation_list = RetrieveFileAnnotations(subject_tofeed)
                annotation_list = annotation_list.values()
                annotations_of = "all"

            if annotation_list:
                now = datetime.datetime.now()
                nowi = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)

                # response = {"@context": global_settings.JSONLD_CONTEXT_URL}

                cleaned = readyQuerySetValuesForDumpAsJSONLD([ann for ann in annotation_list])
                cleaned = ridOflistsOfOneItem(cleaned)
                cleaned = orderedJSONLDfields(cleaned)

                response = cleaned

                # if isinstance(cleaned, list):
                #    response["@graph"] = cleaned
                # else:
                #    response["@graph"] = [cleaned]

                # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
                #json_data = HttpResponse(json.dumps(response, indent=2), mimetype='application/json')
                #json_data['Content-Disposition'] = 'attachment; filename=' + "b2note_export_" + nowi
                download_json.file_data = response #json_data

            navbarlinks = list_navbarlinks(request, ["Download", "Help page"])
            navbarlinks.append({"url": "/help#helpsection_exportpage", "title": "Help page", "icon": "question-sign"})
            shortcutlinks = list_shortcutlinks(request, ["Download"])

            data_dict = {
                'annotations_of': annotations_of,
                'navbarlinks': navbarlinks,
                'shortcutlinks': shortcutlinks,
                'user_nickname': user_nickname,
                'annotations_json': json.dumps(response, indent=2),
                "subject_tofeed": subject_tofeed,
                "pid_tofeed": pid_tofeed
            }

            return render(request, 'b2note_app/export.html', data_dict)

        else:
            print "Redirecting from export view."
            stdlogger.info("Redirecting from export view.")
            return redirect('/accounts/logout')
    except Exception:
        print "Could not export or redirect from export view."
        stdlogger.error("Could not export or redirect from export view.")
        return redirect('/export')


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
    # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
    # json_data = HttpResponse(json.dumps(response, indent=2), mimetype= 'application/json')
    now = datetime.datetime.now()
    nowi = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)
    #json_data = json.dumps( download_json.file_data , indent=2)
    json_data = HttpResponse(json.dumps(download_json.file_data, indent=2), mimetype= 'application/ld+json')
    json_data['Content-Disposition'] = 'attachment; filename=' + "b2note_export_" + nowi + ".jsonld"

    return json_data

    #return download_json.file_data


@login_required
def download_rdfxml(request):
    """
      Function: download_rdfxml
      ----------------------------
        Download a RDF file with the annotations

        input:
            request (object): context of the petition.

        output:
            object: HttpResponse with the file to download.
    """
    now = datetime.datetime.now()
    nowi = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)
    #context = requests.get("https://b2note.bsc.es/jsonld_context_b2note_20161027.jsonld")
    #json_data = json.dumps(download_json.file_data, indent=2)

    #Replace all field names "type" by "@type" for correct rdflib-jsonld processing
    json_data = addarobase_totypefieldname( download_json.file_data )
    g = Graph().parse(data=json.dumps(json_data), format='json-ld')

    # The library adds a trailing slash character to the Software homepage url
    for s, p, o in g.triples((None, None, term.URIRef(u"https://b2note.bsc.es/"))): g.add(
        (s, p, term.URIRef(u"https://b2note.bsc.es")))
    for s, p, o in g.triples((None, None, term.URIRef(u"https://b2note.bsc.es/"))): g.remove(
        (s, p, term.URIRef(u"https://b2note.bsc.es/")))

    rdfxml_data = g.serialize(format='xml')
    rdfxml_data = HttpResponse(rdfxml_data, mimetype='application/rdf+xml')
    rdfxml_data['Content-Disposition'] = 'attachment; filename=' + "b2note_export_" + nowi + ".rdf"

    return rdfxml_data


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
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

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
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')

    text = """
    This functionality will allow the user to select the ontologies from which to retrieve the concepts used for creating annotations.
    """
    
    return render(request, 'b2note_app/default.html', {'text': text, "subject_tofeed":subject_tofeed ,"pid_tofeed":pid_tofeed })


def hostpage(request, uidb64=None, token=None):
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
http://hdl.handle.net/11304/3720bb44-831c-48f3-9847-6988a41236e1
https://b2share.eudat.eu/records/b1092be3cd4844e0bffd7b669521ba3c
Orthography-based dating and localisation of Middle Dutch charters

http://hdl.handle.net/11304/3522daa6-b988-11e3-8cd7-14feb57d12b9
https://b2share.eudat.eu/records/39fa39965b314f658e4a198a78d7f6b5
ImageJ plugin ColonyArea

http://hdl.handle.net/11304/6a9078c4-c3b0-11e3-8cd7-14feb57d12b9
https://b2share.eudat.eu/records/5b1ac2030a9f4338bba9d92593e2e5e4
REST paper 2014

http://hdl.handle.net/11304/69430fd2-e7d6-11e3-b2d7-14feb57d12b9
https://b2share.eudat.eu/records/8f90692d770249f08e42d4613e91dbea
piSVM Analytics Runtimes JUDGE Cluster Rome Images 55 Features

http://hdl.handle.net/11304/fe356a8e-3f2b-11e4-81ac-dcbd1b51435e
https://b2share.eudat.eu/records/f253047b330449d69594f60aebbf3d62
GoNL SNPs and Indels release 5

http://hdl.handle.net/11304/9061f60c-41cf-11e4-81ac-dcbd1b51435e
https://b2share.eudat.eu/records/5a62838104c14932823cfd905eb438fc
Influence of smoking and obesity in sperm quality
    """

    # If the user came from a password reset link they received from an email, we change the page the iframe loads
    reset_password = True
    if uidb64 == None or token == None :
        reset_password = False
    url = "/interface_main"
    if reset_password :
        url = "/accounts/reset_password_confirm/" + uidb64 + '-' + token


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

    return render(request, 'b2note_app/hostpage.html', {'iframe_on': 350, 'buttons_info':buttons_info, 'src': url})


@login_required
def edit_annotation(request):
    """
      Function: edit_annotation
      ----------------------------
        Displays a different form for each annotation type.
        Processes the user-input and performs editing on annotation document.
        Displays editing outcome message/form.
        On clicking redirects to main_interface.

        input:
            request (object): context of the petition.

        output:
            object: HttpResponse with the annotations.
    """

    pid_tofeed = ""
    if request.POST.get('pid_tofeed') != None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed') != None:
        subject_tofeed = request.POST.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    user_nickname = None
    if request.session.get("user"):
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    textinput_primer = None
    if request.POST.get('textinput_primer'):
        textinput_primer = request.POST.get('textinput_primer')

    A = None
    edited_semantic = None
    edited_keyword = None
    edited_comment = None
    shortform = None
    duplicate = None
    long_keyword = None
    has_semantic_equivalent = None
    target_file_title = None
    if request.POST.get('db_id'):
        if isinstance(request.POST.get('db_id'), (str, unicode)):
            a_id = request.POST.get('db_id')
            A = Annotation.objects.get(id=a_id)
            if A:
                '''
                if A.target[0].jsonld_id:
                    target_file_title = b2share_api_get_file_info_on_url(A.target[0].jsonld_id)
                #print "# " * 6 + str(type(target_file_title))
                #print json.dumps(target_file_title, indent=2)
                if target_file_title and isinstance(target_file_title, dict) and "metadata" in target_file_title.keys():
                    target_file_title = target_file_title["metadata"]
                if target_file_title and isinstance(target_file_title, dict) and "titles" in target_file_title.keys():
                    target_file_title = target_file_title["titles"]
                if target_file_title and isinstance(target_file_title, list):
                    target_file_title = target_file_title[0]
                if target_file_title and isinstance(target_file_title, dict) and "title" in target_file_title.keys():
                    target_file_title = target_file_title["title"]
                if not isinstance(target_file_title, (str, unicode)): target_file_title = None
                '''
                if not textinput_primer:
                    if A.body and A.body[0] and A.body[0].type and A.body[0].type=="Composite" and\
                        A.body[0].items and len(A.body[0].items)>1 and A.body[0].items[len(A.body[0].items)-1] and \
                            A.body[0].items[len(A.body[0].items)-1].value:
                        textinput_primer = A.body[0].items[len(A.body[0].items)-1].value

                tg_source = None
                if hasattr(A.target[0], "source"): tg_source = A.target[0].source
                tg_id = None
                if hasattr(A.target[0], "jsonld_id"): tg_id = A.target[0].jsonld_id

                if tg_id or tg_source:
                    if request.POST.get('semantic_submit') is not None:
                        edited_semantic = False
                        if request.POST.get('ontology_json'):
                            jo = request.POST.get('ontology_json')
                            if isinstance(jo, (str, unicode)):
                                o = None
                                o = json.loads( jo )

                                if o and isinstance(o, list) and len(o) > 0:
                                    newbody = {}
                                    for oc in o:
                                        if oc and isinstance(oc, dict):
                                            if "uris" in oc.keys():
                                                if oc["uris"] and isinstance(oc["uris"], (str, unicode)):
                                                    if "body" not in newbody.keys():
                                                        newbody = {"body": {"jsonld_id": [oc["uris"]]}}
                                                    else:
                                                        newbody["body"]["jsonld_id"].append(oc["uris"])
                                                else:
                                                    print "Edit_annotation view, in semantic case, no value to uris key or neither string or unicode."
                                                    stdlogger.error("Edit_annotation view, semantic tag annotation would be a duplicate.")
                                            else:
                                                print "Edit_annotation view, in semantic case, no uris key."
                                                stdlogger.error("Edit_annotation view, in semantic case, no uris key.")
                                        else:
                                            print "Edit_annotation view, in semantic case, list item is not dict."
                                            stdlogger.error("Edit_annotation view, in semantic case, list item is not dict.")
                                    D = None
                                    if newbody and len(newbody) > 0:
                                        D = CheckDuplicateAnnotation(
                                            target_url      = tg_source,
                                            target_pid      = tg_id,
                                            annotation_body = newbody
                                        )
                                    if not D:
                                        id1 = None
                                        id1 = MakeAnnotationSemanticTag(a_id, jo)
                                        if id1: edited_semantic = True
                                        if id1: SetDateTimeModified(id1)
                                    else:
                                        setof_lbls = set()
                                        setof_shortf = set()
                                        for itm in D[0].body[0].items:
                                            if itm.type == "TextualBody":
                                                setof_lbls.add( itm.value )
                                            if itm.type == "SpecificResource":
                                                setof_shortf.add( itm.source[::-1][:itm.source[::-1].find("/")][::-1] )
                                        duplicate = {
                                            "label": ", ".join(setof_lbls),
                                            "shortform": ", ".join(setof_shortf)
                                        }
                                        print "Edit_annotation view, semantic tag annotation would be a duplicate."
                                        stdlogger.info("Edit_annotation view, semantic tag annotation would be a duplicate.")
                                else:
                                    print "Edit_annotation view, in semantic case, could not load json."
                                    stdlogger.error("Edit_annotation view, in semantic case, could not load json.")

                    elif request.POST.get('keyword_submit') is not None:
                        edited_keyword = False
                        if request.POST.get('keyword_text'):
                            k_text = request.POST.get('keyword_text')
                            if isinstance(k_text, (str, unicode)):
                                pass_on = False
                                if not request.POST.get('confirm_flag'):
                                    r = solr_fetchtermonexactlabel( k_text )
                                    if r and len(r) > 0:
                                        has_semantic_equivalent = k_text
                                        print "Create_annotation view, keyword has semantic tag equivalent."
                                        stdlogger.info("Create_annotation view, keyword has semantic tag equivalent.")
                                        pass_on = True

                                if not pass_on and not request.POST.get('enforce_flag'):
                                    L = None
                                    L = CheckLengthFreeText( k_text, 60)
                                    if not L:
                                        long_keyword = k_text
                                        pass_on = True

                                if not pass_on:
                                    newbody = None
                                    newbody = {"body": {"value": k_text}}
                                    D = None
                                    D = CheckDuplicateAnnotation(
                                        target_url      = tg_source,
                                        target_pid      = tg_id,
                                        annotation_body = newbody
                                    )

                                    if not D:
                                        id1 = None
                                        id1 = MakeAnnotationFreeText(a_id, k_text)
                                        id1 = SetAnnotationMotivation(id1, "tagging")
                                        if id1: edited_keyword = True
                                        if id1: SetDateTimeModified(id1)
                                    else:
                                        if D[0].body[0].type=="Composite":
                                            setof_lbls = set()
                                            setof_shortf = set()
                                            for itm in D[0].body[0].items:
                                                if itm.type == "TextualBody":
                                                    setof_lbls.add(itm.value)
                                                if itm.type == "SpecificResource":
                                                    setof_shortf.add(
                                                        itm.source[::-1][:itm.source[::-1].find("/")][::-1])
                                            duplicate = {
                                                "label": ", ".join(setof_lbls),
                                                "shortform": ", ".join(setof_shortf)
                                            }
                                        else:
                                            duplicate = {"label": D[0].body[0].value, }

                    elif request.POST.get('comment_submit') is not None:
                        edited_comment = False
                        if request.POST.get('comment_text'):
                            c_text = request.POST.get('comment_text')
                            if isinstance(c_text, (str, unicode)):
                                id1 = None
                                id1 = MakeAnnotationFreeText( a_id , c_text )
                                id1 = SetAnnotationMotivation( id1, "commenting" )
                                if id1: edited_comment = True
                                if id1: SetDateTimeModified(id1)

                    A = Annotation.objects.get(id=a_id)

                    setof_shortf = set()
                    if A and A.body and A.body[0] and A.body[0].type=="Composite" and A.body[0].items and isinstance(A.body[0].items, list):
                        for itm in A.body[0].items:
                            if itm.type == "SpecificResource":
                                setof_shortf.add(itm.source[::-1][:itm.source[::-1].find("/")][::-1])
                    shortform = ", ".join(setof_shortf)

    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append({"url": "/help#helpsection_editpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, [])

    data_dict = {
        #'target_file_title': target_file_title,
        'textinput_primer': textinput_primer,
        'long_keyword': long_keyword,
        'has_semantic_equivalent': has_semantic_equivalent,
        'shortform': shortform,
        'duplicate': duplicate,
        'edited_semantic': edited_semantic,
        'edited_keyword': edited_keyword,
        'edited_comment': edited_comment,
        'ann': A,
        'navbarlinks': navbarlinks,
        'shortcutlinks': list_shortcutlinks,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'user_nickname': user_nickname,
    }

    return render(request, "b2note_app/edit_annotation.html", data_dict)


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

    request.session["annotation_deleted"] = False

    user_nickname = None
    if request.session.get("user"):
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname
        the_id = None
        the_id = request.POST.get('db_id')
        if the_id:
            if isinstance( the_id, (str, unicode)):
                if request.POST.get("delete_confirmed") is None:
                    navbarlinks = list_navbarlinks(request, [])
                    shortcutlinks = list_shortcutlinks(request, [])
                    data_dict = {
                        'id':the_id,
                        'user_nickname': user_nickname,
                        'navbarlinks':navbarlinks,
                        'shortcutlinks':shortcutlinks,
                    }
                    return render(request, 'b2note_app/delete_confirm.html', data_dict)
                A = Annotation.objects.get( id = the_id )
                if A:
                    owner = userprofile.nickname == A.creator[0].nickname
                    if owner:
                        R = None
                        R = DeleteFromPOSTinfo( the_id )
                        if R:
                            request.session["annotation_deleted"] = True
                            return redirect('/interface_main')
                        else:
                            print "delete_annotation view, annotation delete not successful."
                            stdlogger.error("delete_annotation view, annotation delete not successful.")
                            pass
                    else:
                        print "delete_annotation view, cannot delete annotation, current user is not owner."
                        stdlogger.error("delete_annotation view, cannot delete annotation, current user is not owner.")
                        pass
                else:
                    print "delete_annotation view, no annotation with provided 'db_id': ", str( the_id )
                    stdlogger.error("delete_annotation view, no annotation with provided 'db_id': " + str( the_id ))
                    pass
            else:
                print "delete_annotation view, provided parameter 'db_id' neither str nor unicode."
                stdlogger.error("delete_annotation view, provided parameter 'db_id' neither str nor unicode.")
                pass
        else:
            print "delete_annotation view, missing POST parameter 'db_id'."
            stdlogger.error("delete_annotation view, missing POST parameter 'db_id'.")
            pass
    else:
        print "delete_annotation view, user is not logged-in."
        stdlogger.error("delete_annotation view, user is not logged-in.")
        return redirect('/accounts/logout')

    return redirect('/interface_main')


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
    message = None
    user_nickname = None
    if request.session.get('user')!=None:

        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname
        ann_id1 = None
        ann_id2 = None

        tg_source = None
        if request.POST.get('subject_tofeed'): tg_source = request.POST.get('subject_tofeed')
        if not isinstance(tg_source, (str, unicode)): tg_source = None

        tg_id = None
        if request.POST.get('pid_tofeed'): tg_id = request.POST.get('pid_tofeed')
        if not isinstance(tg_id, (str, unicode)): tg_id = None

        if tg_id or tg_source:

            if request.POST.get('semantic_submit')!=None:
                o = None
                if request.POST.get('ontology_json'):
                    try:
                        o = json.loads(request.POST.get('ontology_json'))
                    except:
                        print "Create_annotation view, in semantic case, could not load json from POST data."
                        stdlogger.error("Create_annotation view, in semantic case, could not load json from POST data.")
                if o and isinstance(o, list) and len(o) > 0:

                    newbody = {}
                    for oc in o:
                        if oc and isinstance(oc, dict):
                            if "uris" in oc.keys():
                                if oc["uris"] and isinstance(oc["uris"], (str, unicode)):
                                    if "body" not in newbody.keys():
                                        newbody = {"body":{"jsonld_id":[oc["uris"]]}}
                                    else:
                                        newbody["body"]["jsonld_id"].append(oc["uris"])
                                else:
                                    print "Create_annotation view, in semantic case, no value to uris key or neither string or unicode."
                                    stdlogger.error("Create_annotation view, semantic tag annotation would be a duplicate.")
                            else:
                                print "Create_annotation view, in semantic case, no uris key."
                                stdlogger.error("Create_annotation view, in semantic case, no uris key.")
                        else:
                            print "Create_annotation view, in semantic case, list item is not dict."
                            stdlogger.error("Create_annotation view, in semantic case, list item is not dict.")
                    D = None
                    if newbody and len(newbody)>0:
                        D = CheckDuplicateAnnotation(
                            target_url      = tg_source,
                            target_pid      = tg_id,
                            annotation_body = newbody
                        )
                    if not D:
                        ann_id1 = CreateSemanticTag(
                            subject_url =   tg_source,
                            subject_pid =   tg_id,
                            object_json =   request.POST.get('ontology_json'),
                        )
                        ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1)
                        A = Annotation.objects.get(id=ann_id2)
                        setof_shortf = set()
                        for oc in A.body[0].items:
                            if oc.type == "SpecificResource":
                                if isinstance(oc.source, (str, unicode)):
                                    setof_shortf.add( oc.source[::-1][:oc.source[::-1].find("/")][::-1] )
                        request.session["new_semantic"] = {
                            "label": A.body[0].items[len(A.body[0].items)-1].value,
                            "shortform": ", ".join(setof_shortf),
                        }
                    else:
                        setof_labels = set()
                        setof_shortf = set()
                        for dupl in D:
                            for oc in dupl.body[0].items:
                                if oc.type == "SpecificResource":
                                    if isinstance(oc.source, (str, unicode)):
                                        setof_shortf.add(oc.source[::-1][:oc.source[::-1].find("/")][::-1])
                                if oc.type == "TextualBody":
                                    if isinstance(oc.value, (str, unicode)):
                                        setof_labels.add( oc.value )
                        request.session["duplicate"] = {
                            "label": ", ".join(setof_labels),
                            "shortform": ", ".join(setof_shortf),
                        }
                        print "Create_annotation view, semantic tag annotation would be a duplicate."
                        stdlogger.info("Create_annotation view, semantic tag annotation would be a duplicate.")
                else:
                    print "Create_annotation view, missing list of ontology classes to create semantic annotation."
                    stdlogger.error("Create_annotation view, missing list of ontology classes to create semantic annotation.")

            elif request.POST.get('keyword_submit')!=None:
                if request.POST.get('keyword_text') and isinstance(request.POST.get('keyword_text'),(str, unicode)):

                    keyword_text = request.POST.get('keyword_text')

                    pass_on = False
                    if not request.POST.get('confirm_flag'):
                        r = solr_fetchtermonexactlabel( keyword_text )
                        if r and len(r)>0:
                            request.session["has_semantic_equivalent"] = keyword_text
                            print "Create_annotation view, keyword has semantic tag equivalent."
                            stdlogger.info("Create_annotation view, keyword has semantic tag equivalent.")
                            pass_on = True

                    if not pass_on and not request.POST.get('enforce_flag'):
                        L = None
                        L = CheckLengthFreeText( keyword_text, 60)
                        if not L:
                            request.session["long_keyword"] = keyword_text
                            pass_on = True

                    if not pass_on:
                        newbody = None
                        newbody = {"body": {"value": keyword_text}}
                        D = None
                        D = CheckDuplicateAnnotation(
                            target_url      = tg_source,
                            target_pid      = tg_id,
                            annotation_body = newbody
                        )

                        if not D:
                            ann_id1 = CreateFreeTextKeyword(
                                subject_url =   tg_source,
                                subject_pid =   tg_id,
                                text        =   keyword_text
                            )
                            ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1 )
                            A = Annotation.objects.get( id = ann_id2 )
                            request.session["new_keyword"] = { "label": A.body[0].value, }
                        else:
                            if D[0].body[0].type=="Composite":
                                request.session["duplicate"] = {
                                    "label": D[0].body[0].items[len(D[0].body[0].items)-1].value,
                                    "shortform": D[0].body[0].items[0].source[::-1][:D[0].body[0].items[0].source[::-1].find("/")][::-1],
                                }
                            else:
                                request.session["duplicate"] = { "label": D[0].body[0].value, }
                            print "Create_annotation view, free-text keyword annotation would be a duplicate."
                            stdlogger.info("Create_annotation view, free-text keyword annotation would be a duplicate.")

            elif request.POST.get('comment_submit')!=None:
                if request.POST.get('comment_text') and isinstance(request.POST.get('comment_text'),(str, unicode)):

                    comment_text = request.POST.get('comment_text')

                    ann_id1 = CreateFreeTextComment(
                        subject_url =   tg_source,
                        subject_pid =   tg_id,
                        text        =   comment_text
                    )
                    ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1)
                    A = Annotation.objects.get(id=ann_id2)
                    request.session["new_comment"] = {"label": A.body[0].value,}

        else:
           print "Create_annotation view, in semantic case, no target file identifier or neither string nor unicode."
           stdlogger.error("Create_annotation view, in semantic case, no target file identifier or neither string nor unicode.")

    return redirect("/interface_main")


@login_required
def annotation_summary(request):
    """
      Function: annotation_summary
      ----------------------------
        Displays 4 sections one with a summarising table
        and 3 listing annotations about the file in each category.

        input:
            request (object): context of the petition.

        output:
            object: HttpResponse with the annotations.
    """
    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    A = None

    r = None

    rrr = None

    r4 = []

    all_or_mine = None

    allannotations_list = []

    if request.POST.get('db_id')!=None:

        if isinstance(request.POST.get('db_id'), (str, unicode)):

            A = Annotation.objects.get( id = request.POST.get('db_id') )

        if A and A.body and A.body[0]:

            if request.POST.get('about_allsimilar')!=None:

                if A.body[0].type and A.body[0].type=="Composite" and A.body[0].items:

                    uri_list = [m.source for m in A.body[0].items if m.type=="SpecificResource"]

                    r = solr_fetchorigintermonid( uri_list )

                    if user_nickname and isinstance(user_nickname, (str, unicode)):

                        allannotations_list = Annotation.objects.raw_query(
                            {'body.items.source': {"$in": uri_list},'creator.nickname': {"$ne": user_nickname}}
                        )

                    else:

                        allannotations_list = Annotation.objects.raw_query({'body.items.source': {"$in": uri_list}})

                elif A.body[0].type and not A.body[0].type=="Composite" and A.body[0].value and A.motivation and A.motivation[0]=="tagging":

                    if user_nickname and isinstance(user_nickname, (str, unicode)):

                        allannotations_list = Annotation.objects.raw_query(
                            {'body.value': A.body[0].value, 'motivation': "tagging", 'creator.nickname': { "$ne": user_nickname} })

                    else:

                        allannotations_list = Annotation.objects.raw_query({'body.value': A.body[0].value, 'motivation': "tagging"})

                elif A.body[0].type and not A.body[0].type=="Composite" and A.body[0].value and A.motivation and A.motivation[0] == "commenting":

                    allannotations_list = A

                if allannotations_list: all_or_mine = "others"


            elif request.POST.get('about_allsimilar_any')!=None:

                if A.body[0].type and A.body[0].type=="Composite" and A.body[0].items:

                    uri_list = [m.source for m in A.body[0].items if m.type == "SpecificResource"]

                    r = solr_fetchorigintermonid( uri_list )

                    allannotations_list = Annotation.objects.raw_query({'body.items.source': {"$in": uri_list}})

                elif A.body[0].type and not A.body[0].type=="Composite" and A.body[0].value and A.motivation and A.motivation[0]=="tagging":

                    allannotations_list = Annotation.objects.raw_query(
                        {'body.value': A.body[0].value, 'motivation': "tagging"})

                elif A.body[0].type and not A.body[0].type=="Composite" and A.body[0].value and A.motivation and A.motivation[0] == "commenting":

                    allannotations_list = A

                if allannotations_list: all_or_mine = "all"

            elif request.POST.get('about_mysimilar') != None:

                if A.body[0].type and A.body[0].type=="Composite" and A.body[0].items:

                    uri_list = [m.source for m in A.body[0].items if m.type == "SpecificResource"]

                    r = solr_fetchorigintermonid( uri_list )

                    allannotations_list = Annotation.objects.raw_query(
                        {'body.items.source': {"$in": uri_list}, 'creator.nickname': user_nickname})

                elif A.body[0].type and not A.body[0].type=="Composite" and A.body[0].value and A.motivation and A.motivation[0] == "tagging":

                    allannotations_list = Annotation.objects.raw_query(
                        {'body.value': A.body[0].value, 'motivation': "tagging", 'creator.nickname': user_nickname})

                elif A.body[0].type and not A.body[0].type=="Composite" and A.body[0].value and A.motivation and A.motivation[0] == "commenting":

                    allannotations_list = A

                if allannotations_list: all_or_mine = "mine"

            if not allannotations_list: allannotations_list = [A]

            r4 = []
            ooarnb = []
            if r:
                for rr in r.keys():
                    rrr = r[rr]
                    setof_syns = set()
                    if isinstance(rrr, dict) and "synonyms" in rrr.keys():
                        if rrr["synonyms"] and isinstance(rrr["synonyms"], list):
                            for syno in rrr["synonyms"]:
                                if isinstance(syno, (str, unicode)):
                                    try:
                                        setof_syns.add(str(syno))
                                    except:
                                        pass
                        elif isinstance(rrr["synonyms"], (str, unicode)):
                            try:
                                setof_syns.add(str(rrr["synonyms"]))
                            except:
                                pass
                        rrr["synonyms"] = str(", ".join(setof_syns))
                    if isinstance(rrr, dict) and "acrs_of_ontologies_reusing_uri" in rrr.keys():
                        ooarnb.append( len(rrr["acrs_of_ontologies_reusing_uri"]) )
                        rrr["acrs_of_ontologies_reusing_uri"] = sorted(rrr["acrs_of_ontologies_reusing_uri"])
                        rrr["acrs_of_ontologies_reusing_uri"] = str(", ".join(rrr["acrs_of_ontologies_reusing_uri"]))
                    else:
                        ooarnb.append( 0 )
                    r4.append( rrr )
            ooarnb = OrderedDict(sorted(enumerate(ooarnb), key=lambda x: x[1])).keys()
            r4 = [ r4[x] for x in ooarnb[::-1] ]


    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append({"url": "/help#helpsection_annotationsummarypage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, [])

    data_dict = {
        'rows_of_dots': range(int((float(len(r4))+float(10))/float(11))),
        'r4': r4,
        'all_or_mine': all_or_mine,
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'annotation_list': allannotations_list,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'user_nickname': user_nickname,
    }

    return render(request, 'b2note_app/annotation_summary.html', data_dict)


@login_required
def myannotations(request):
    """
      Function: myannotations
      ----------------------------
        Displays 4 sections one with a summarising table
        and 3 listing annotations about the file in each category.

        input:
            request (object): context of the petition.

        output:
            object: HttpResponse with the annotations.
    """

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    try:
        #allannotations_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed, 'creator.nickname': user_nickname})
        allannotations_list = Annotation.objects.raw_query( {'creator.nickname': user_nickname} )
    except Annotation.DoesNotExist:
        allannotations_list = []

    allannotations_list = sorted(allannotations_list, key=lambda Annotation: Annotation.created, reverse=True)

    my_s  = 0
    my_k  = 0
    my_c  = 0

    semantic_table = []
    keyword_table  = []
    comment_table  = []

    sem_avoid_dbles = set()
    key_avoid_dbles = set()

    r = None
    r = solr_fetchorigintermonid([A.body[0].items[0].source for A in allannotations_list if A.body and A.body[0] and A.body[0].type and A.body[0].type=="Composite"])

    for A in allannotations_list:

        link_label = ""
        link_info_label = ""
        link_info_creatornickname = ""
        link_info_modified = ""

        if A.body and A.body[0] and A.body[0].type=="Composite" and A.body[0].items and A.body[0].items[len(A.body[0].items) - 1].value:
            last_is_textual_index = len(A.body[0].items) - 1
            if len(A.body[0].items[last_is_textual_index].value) > 20: link_label = '...'
            link_label = A.body[0].items[last_is_textual_index].value[:20] + link_label
            if len(A.body[0].items[last_is_textual_index].value) > 40: link_info_label = '...'
            link_info_label = A.body[0].items[last_is_textual_index].value[:40] + link_info_label
        elif A.body and A.body[0] and not A.body[0].type=="Composite" and A.body[0].value:
            if len(A.body[0].value) > 20: link_label = '...'
            link_label = A.body[0].value[:20] + link_label
            if len(A.body[0].value) > 40: link_info_label = '...'
            link_info_label = A.body[0].value[:40] + link_info_label

        if A.creator and A.creator[0] and A.creator[0].nickname:
            link_info_creatornickname = A.creator[0].nickname
        if A.modified: link_info_modified = A.modified

        if A.body and A.body[0] and A.body[0].type and A.body[0].type=="Composite" and A.body[0].items and A.body[0].items[0].source:

            if A.body[0].items[0].source not in sem_avoid_dbles:

                sem_avoid_dbles.add(A.body[0].items[0].source)

                link_info_ontologyacronym = ""
                link_info_shortform = ""
                if r:
                    if isinstance(r, dict):
                        if A.body[0].items[0].source in r.keys():
                            if isinstance(r[A.body[0].items[0].source], dict):
                                if "ontology_acronym" in r[A.body[0].items[0].source].keys():
                                    link_info_ontologyacronym = r[A.body[0].items[0].source]["ontology_acronym"]
                                if "short_form" in r[A.body[0].items[0].source].keys():
                                    link_info_shortform = r[A.body[0].items[0].source]["short_form"]

                semantic_list = Annotation.objects.raw_query({'body.items.source': A.body[0].items[0].source})

                semantic_dict = {'ann_id': A.id,
                                 'link_label': link_label,
                                 'link_info_label': link_info_label,
                                 'link_info_ontologyacronym': link_info_ontologyacronym,
                                 'link_info_shortform': link_info_shortform,
                                 'link_info_creatornickname': link_info_creatornickname,
                                 'link_info_modified': link_info_modified,
                                 'my_similar': len(semantic_list),
                                 }

                semantic_table.append( semantic_dict )

            my_s += 1

        elif A.body and A.body[0] and A.body[0].type and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="tagging":

            if A.body[0].value not in key_avoid_dbles:

                key_avoid_dbles.add(A.body[0].value)

                keyword_list = Annotation.objects.raw_query({'body.value': A.body[0].value, 'motivation': "tagging"})

                keyword_dict = {'ann_id': A.id,
                                'link_label': link_label,
                                'link_info_label': link_info_label,
                                'link_info_creatornickname': link_info_creatornickname,
                                'link_info_modified': link_info_modified,
                                'my_similar': len(keyword_list),
                                }

                keyword_table.append( keyword_dict )

            my_k += 1

        elif A.body and A.body[0].type and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="commenting":

            comment_dict = {'ann_id': A.id,
                            'link_label': link_label,
                            'link_info_label': link_info_label,
                            'link_info_creatornickname': link_info_creatornickname,
                            'link_info_modified': link_info_modified,
                            }

            comment_table.append(comment_dict)

            my_c += 1

    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append({"url": "/help#helpsection_myannotationspage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, [])

    data_dict = {
        'semantic_table': semantic_table,
        'keyword_table': keyword_table,
        'comment_table': comment_table,
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'annotation_list': allannotations_list,
        'my_s': my_s,
        'my_k': my_k,
        'my_c': my_c,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'user_nickname': user_nickname}

    return render(request, 'b2note_app/myannotations.html', data_dict)


@login_required
def allannotations(request):
    """
      Function: allannotations
      ----------------------------
        Displays 4 sections one with a summarising table
        and 3 listing annotations about the file in each category.

        input:
            request (object): context of the petition.

        output:
            object: HttpResponse with the annotations.
    """

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed": subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    try:
        if subject_tofeed and pid_tofeed:
            allannotations_list = Annotation.objects.raw_query({'target.source': subject_tofeed, 'target.jsonld_id': pid_tofeed})
        elif subject_tofeed:
            allannotations_list = Annotation.objects.raw_query({'target.source': subject_tofeed})
        elif pid_tofeed:
            allannotations_list = Annotation.objects.raw_query({'target.jsonld_id': pid_tofeed})
    except Annotation.DoesNotExist:
        allannotations_list = []

    allannotations_list = sorted(allannotations_list, key=lambda Annotation: Annotation.created, reverse=True)

    all_s = 0
    all_k = 0
    all_c = 0
    my_s  = 0
    my_k  = 0
    my_c  = 0

    semantic_table = []
    keyword_table  = []
    comment_table  = []

    sem_avoid_dbles = set()
    key_avoid_dbles = set()

    r = None
    r = solr_fetchorigintermonid([A.body[0].items[0].source for A in allannotations_list if A.body and A.body[0] and A.body[0].type and A.body[0].type=="Composite"])

    for A in allannotations_list:

        link_label = ""
        link_info_label = ""
        link_info_creatornickname = ""
        link_info_modified = ""

        if A.body and A.body[0] and A.body[0].type=="Composite" and A.body[0].items and A.body[0].items[len(A.body[0].items)-1].value:
            last_is_textual_index = len(A.body[0].items)-1
            if len(A.body[0].items[last_is_textual_index].value) > 20: link_label = '...'
            link_label = A.body[0].items[last_is_textual_index].value[:20] + link_label
            if len(A.body[0].items[last_is_textual_index].value) > 40: link_info_label = '...'
            link_info_label = A.body[0].items[last_is_textual_index].value[:40] + link_info_label
        elif A.body and A.body[0] and not A.body[0].type=="Composite" and A.body[0].value:
            if len(A.body[0].value) > 20: link_label = '...'
            link_label = A.body[0].value[:20] + link_label
            if len(A.body[0].value) > 40: link_info_label = '...'
            link_info_label = A.body[0].value[:40] + link_info_label

        if A.creator and A.creator[0] and A.creator[0].nickname:
            link_info_creatornickname = A.creator[0].nickname
        if A.modified:
            link_info_modified = A.modified

        if A.body and A.body[0] and A.body[0].type and A.body[0].type=="Composite" and A.body[0].items and A.body[0].items[0].source:

            if A.body[0].items[0].source not in sem_avoid_dbles:

                sem_avoid_dbles.add(A.body[0].items[0].source)

                link_info_ontologyacronym = ""
                link_info_shortform = ""
                if r:
                    if isinstance(r, dict):
                        if A.body[0].items[0].source in r.keys():
                            if isinstance(r[A.body[0].items[0].source], dict):
                                if "ontology_acronym" in r[A.body[0].items[0].source].keys():
                                    link_info_ontologyacronym = r[A.body[0].items[0].source]["ontology_acronym"]
                                if "ontology_acronym" in r[A.body[0].items[0].source].keys():
                                    link_info_shortform = r[A.body[0].items[0].source]["short_form"]

                semantic_list = Annotation.objects.raw_query({'body.items.source': A.body[0].items[0].source})

                my_similar = len([A for A in semantic_list if A.creator and A.creator[0].nickname==user_nickname])
                all_similar = len(semantic_list) - my_similar
                if all_similar<0: all_similar = 0

                semantic_dict = {'ann_id': A.id,
                                 'link_label': link_label,
                                 'link_info_label': link_info_label,
                                 'link_info_ontologyacronym': link_info_ontologyacronym,
                                 'link_info_shortform': link_info_shortform,
                                 'link_info_creatornickname': link_info_creatornickname,
                                 'link_info_modified': link_info_modified,
                                 'all_similar': all_similar,
                                 'my_similar': my_similar,
                                 }

                semantic_table.append( semantic_dict )

            if A.creator and A.creator[0].nickname==user_nickname:
                my_s += 1
            else:
                all_s += 1

        elif A.body and A.body[0] and A.body[0].type and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="tagging":

            if A.body[0].value not in key_avoid_dbles:

                key_avoid_dbles.add(A.body[0].value)

                keyword_list = Annotation.objects.raw_query({'body.value': A.body[0].value, 'motivation': "tagging"})

                my_similar = len([A for A in keyword_list if A.creator and A.creator[0].nickname==user_nickname])
                all_similar = len(keyword_list) - my_similar
                if all_similar<0: all_similar = 0

                keyword_dict = {'ann_id': A.id,
                                'link_label': link_label,
                                'link_info_label': link_info_label,
                                'link_info_creatornickname': link_info_creatornickname,
                                'link_info_modified': link_info_modified,
                                'all_similar': all_similar,
                                'my_similar': my_similar,
                                }

                keyword_table.append( keyword_dict )

            if A.creator and A.creator[0].nickname==user_nickname:
                my_k += 1
            else:
                all_k += 1

        elif A.body and A.body[0].type and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="commenting":

            comment_dict = {'ann_id': A.id,
                            'link_label': link_label,
                            'link_info_label': link_info_label,
                            'link_info_creatornickname': link_info_creatornickname,
                            'link_info_modified': link_info_modified,
                            }

            comment_table.append(comment_dict)

            if A.creator and A.creator[0] and A.creator[0].nickname==user_nickname:
                my_c += 1
            else:
                all_c += 1

    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append({"url": "/help#helpsection_allannotationspage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, [])

    data_dict = {
        'semantic_table': semantic_table,
        'keyword_table': keyword_table,
        'comment_table': comment_table,
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'annotation_list': allannotations_list,
        'all_s': all_s,
        'all_k': all_k,
        'all_c': all_c,
        'my_s': my_s,
        'my_k': my_k,
        'my_c': my_c,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'user_nickname': user_nickname}

    return render(request, 'b2note_app/allannotations.html', data_dict)


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

    duplicate = None
    if request.session.get("duplicate"):
        duplicate = request.session.get("duplicate")
        request.session["duplicate"] = None

    new_semantic = None
    if request.session.get("new_semantic"):
        new_semantic = request.session.get("new_semantic")
        request.session["new_semantic"] = None

    new_keyword = None
    if request.session.get("new_keyword"):
        new_keyword = request.session.get("new_keyword")
        request.session["new_keyword"] = None

    new_comment = None
    if request.session.get("new_comment") is not None:
        new_comment = request.session.get("new_comment")
        request.session["new_comment"] = None

    has_semantic_equivalent = None
    if "has_semantic_equivalent" in request.session.keys() and request.session["has_semantic_equivalent"]:
        has_semantic_equivalent = request.session["has_semantic_equivalent"]
        request.session["has_semantic_equivalent"] = None

    long_keyword = None
    if "long_keyword" in request.session.keys() and request.session["long_keyword"]:
        long_keyword = request.session["long_keyword"]
        request.session["long_keyword"] = None

    textinput_primer = None
    if request.POST.get('textinput_primer'):
        textinput_primer = request.POST.get('textinput_primer')

    annotation_deleted = None
    if "annotation_deleted" in request.session.keys() and request.session["annotation_deleted"]==True:
        annotation_deleted = "success"
        request.session["annotation_deleted"] = None
    elif "annotation_deleted" in request.session.keys() and request.session["annotation_deleted"]==False:
        annotation_deleted = "abort"
        request.session["annotation_deleted"] = None

    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    user_nickname = None
    if not request.session.get('user') and request.session.get('registration_state') == "todo" and request.session.get('auth_email') is not None:
        context = RequestContext(request, {"subject_tofeed": subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/register', context=context)
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed": subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    annotation_list = []
    allannotations_list = []

    #http://stackoverflow.com/questions/5508888/matching-query-does-not-exist-error-in-django
    try:
        # https://blog.scrapinghub.com/2013/05/13/mongo-bad-for-scraped-data/
        # https://github.com/aparo/django-mongodb-engine/blob/master/docs/embedded-objects.rst
        if user_nickname:
            annotation_list = Annotation.objects.raw_query({'creator.nickname': user_nickname})
        if subject_tofeed and pid_tofeed:
            allannotations_list = Annotation.objects.raw_query({'target.source': subject_tofeed, 'target.jsonld_id': pid_tofeed})
        elif subject_tofeed:
            allannotations_list = Annotation.objects.raw_query({'target.source': subject_tofeed})
        elif pid_tofeed:
            allannotations_list = Annotation.objects.raw_query({'target.jsonld_id': pid_tofeed})
    except Annotation.DoesNotExist:
        annotation_list = []
        allannotations_list = []

    allannotations_list = sorted(allannotations_list, key=lambda Annotation: Annotation.created, reverse=True)

    all_s = None
    all_k = None
    all_c = None
    my_s  = None
    my_k  = None
    my_c  = None
    myf_s = None
    myf_k = None
    myf_c = None

    all_s = len([A for A in allannotations_list if A.body and A.body[0].type=="Composite" ])
    all_k = len([A for A in allannotations_list if A.body and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="tagging" ])
    all_c = len([A for A in allannotations_list if A.body and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="commenting" ])
    if user_nickname:
        my_s  = len([A for A in annotation_list if A.creator and A.creator[0].nickname==user_nickname
                     and A.body and A.body[0].type=="Composite" ])
        my_k  = len([A for A in annotation_list if A.creator and A.creator[0].nickname==user_nickname
                     and A.body and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="tagging" ])
        my_c  = len([A for A in annotation_list if A.creator and A.creator[0].nickname==user_nickname
                     and A.body and not A.body[0].type=="Composite" and A.motivation and A.motivation[0]=="commenting" ])
        myf_s = len([A for A in allannotations_list if A.creator and A.creator[0].nickname == user_nickname
                    and A.body and A.body[0].type=="Composite" ])
        myf_k = len([A for A in allannotations_list if A.creator and A.creator[0].nickname == user_nickname
                    and A.body and not A.body[0].type=="Composite" and A.motivation and A.motivation[0] == "tagging"])
        myf_c = len([A for A in allannotations_list if A.creator and A.creator[0].nickname == user_nickname
                    and A.body and not A.body[0].type=="Composite" and A.motivation and A.motivation[0] == "commenting"])

    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append( {"url": "/help#helpsection_mainpage", "title": "Help page", "icon": "question-sign"} )
    shortcutlinks = []

    if all_s and myf_s: all_s = all_s - myf_s
    if all_k and myf_k: all_k = all_k - myf_k
    if all_c and myf_c: all_c = all_c - myf_c

    if all_s <0: all_s = 0
    if all_k <0: all_k = 0
    if all_c <0: all_c = 0

    data_dict = {
        'annotation_deleted': annotation_deleted,
        'new_comment': new_comment,
        'long_keyword': long_keyword,
        'textinput_primer': textinput_primer,
        'has_semantic_equivalent': has_semantic_equivalent,
        'new_keyword': new_keyword,
        'new_semantic': new_semantic,
        'duplicate': duplicate,
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'annotation_list': allannotations_list,
        'all_s': all_s,
        'all_k': all_k,
        'all_c': all_c,
        'my_s': my_s,
        'my_k': my_k,
        'my_c': my_c,
        'myf_s': myf_s,
        'myf_k': myf_k,
        'myf_c': myf_c,
        'subject_tofeed': subject_tofeed,
        'pid_tofeed': pid_tofeed,
        'user_nickname': user_nickname}

    return render(request, 'b2note_app/interface_main.html', data_dict)


def extract_shortform( e=None ):
    out=None
    if e:
        if isinstance(e, dict):
            sf = "--"
            if "short_form" in e.keys():
                if e["short_form"] and isinstance(e["short_form"], (str, unicode)):
                    sf = e["short_form"]
                    if "ontology_acronym" in e.keys():
                        if e["ontology_acronym"] and isinstance(e["ontology_acronym"], (str, unicode)):
                            if e["ontology_acronym"] not in e["short_form"]:
                                sf = e["ontology_acronym"] + ":" + e["short_form"]
            elif "uris" in e.keys():
                if e["uris"] and isinstance( e["uris"], (str,unicode) ):
                    uri = e["uris"]
                    sf = uri[::-1][:uri[::-1].find(" / ")][::-1]
            out = sf
    return out

def process_semantic_entry( entry=None, query_dict=None, search_str=None ):
    if not search_str: search_str = ""
    if query_dict and entry:
        if isinstance(query_dict, dict) and isinstance(entry, dict):
            if "search_param" in entry.keys():
                if entry["search_param"]:
                    #if isinstance(entry["search_param"], (str, unicode)): entry["search_param"] = json.loads(entry["search_param"])
                    if isinstance(entry["search_param"], list) and len(entry["search_param"]) > 0:
                        setof_labels = set()
                        setof_uris = set()
                        setof_shortf = set()
                        setof_syns = set()
                        if "logical" in entry.keys():
                            if entry["logical"] and isinstance(entry["logical"], (str, unicode)):
                                for logic in ["AND", "OR", "NOT", "XOR"]:
                                    if entry["logical"] == logic:
                                        for oc in entry["search_param"]:
                                            if isinstance(oc, dict):
                                                if "uris" in oc.keys() and oc["uris"] and isinstance(oc["uris"], (str, unicode)):
                                                    setof_uris = oc["uris"]
                                                if "labels" in oc.keys() and oc["labels"] and isinstance( oc["labels"], (str,unicode) ):
                                                    setof_labels.add( str(oc["labels"]) )
                                                setof_shortf.add( str(extract_shortform( oc )) )
                                        for u in setof_uris:
                                            query_dict["body_id_" + str(logic).lower()].append( u )
                                        for labl in setof_labels:
                                            query_dict["body_val_" + str(logic).lower()].append( labl )
                                        search_str += " " + str(logic).upper() + \
                                                      " " + ", ".join(setof_labels) + \
                                                      "  (" + ", ".join(setof_shortf) + ")"
                            elif entry["logical"] is None:
                                for oc in entry["search_param"]:
                                    if isinstance(oc, dict):
                                        if "uris" in oc.keys() and oc["uris"] and isinstance(oc["uris"], (str, unicode)):
                                            setof_uris = oc["uris"]
                                        if "labels" in oc.keys() and oc["labels"] and isinstance( oc["labels"], (str,unicode) ):
                                            setof_labels.add( str(oc["labels"]) )
                                        setof_shortf.add( str(extract_shortform( oc )) )
                                for u in setof_uris:
                                    query_dict["body_id_or"].append( u )
                                for labl in setof_labels:
                                    query_dict["body_val_or"].append( labl )
                                search_str += " " + ", ".join(setof_labels) + \
                                              "  (" + ", ".join(setof_shortf) + ")"
                            else:
                                for oc in entry["search_param"]:
                                    if isinstance(oc, dict):
                                        setof_shortf.add(str(extract_shortform( oc )))
                                search_str += " " + ", ".join(setof_shortf)

                        if "syn_incl" in entry.keys() and entry["syn_incl"] is True:
                            for oc in entry["search_param"]:
                                if isinstance(oc, dict) and "synonyms" in oc.keys():
                                    syns = None
                                    syns = oc["synonyms"]
                                    if syns and isinstance(syns, list):
                                        for syn in syns:
                                            if syn and isinstance(syn, (str, unicode)):
                                                setof_syns.add( syn )
                            for syn in setof_syns:
                                query_dict["body_val_syn"].append( syn )
                            if len(setof_syns)>0:
                                search_str += " SYN " + ", ".join(setof_syns)
                            else:
                                search_str += " NOSYN "
    return query_dict, search_str


def process_keyword_entry( entry=None, query_dict=None, search_str=None ):
    if not search_str: search_str = ""
    if query_dict and entry:
        if isinstance(query_dict, dict) and isinstance(entry, dict):
            if "search_param" in entry.keys():
                if entry["search_param"]:
                    if isinstance(entry["search_param"], (str, unicode)):
                        kwd = None
                        kwd = entry["search_param"]
                        if kwd and isinstance(kwd, (str, unicode)):
                            if "logical" in entry.keys():
                                if entry["logical"] and isinstance(entry["logical"], (str, unicode)):
                                    for logic in ["AND", "OR", "NOT", "XOR"]:
                                        if entry["logical"] == logic:
                                            query_dict["body_val_"+str(logic).lower()].append( kwd )
                                            search_str += " " + str(logic).upper() + " " + kwd
                                elif entry["logical"] is None:
                                    query_dict["body_val_or"].append( kwd )
                                    search_str += " " + kwd
    return query_dict, search_str


def process_search_query( form ):
    query_dict = {"body_val_and": [],
                  "body_val_or" : [],
                  "body_val_not": [],
                  "body_val_xor": [],
                  "body_id_and" : [],
                  "body_id_or"  : [],
                  "body_id_not" : [],
                  "body_id_xor" : [],
                  "body_val_syn": [],
                  "commenting"  : False,
                  }
    search_str = ""

    if form:
        for entry in form:
            if isinstance(entry, dict):
                if "type" in entry.keys():
                    if entry["type"] and isinstance(entry["type"], (str, unicode)):
                        if entry["type"] == "Semantic tag":
                            query_dict, search_str = process_semantic_entry( entry, query_dict, search_str )
                        elif entry["type"] == "Free-text keyword":
                            query_dict, search_str = process_keyword_entry( entry, query_dict, search_str )
                        elif entry["type"] == "Comment":
                            query_dict["commenting"] = True
                            search_str += " ALL COMMENTED FILES"

    VA=""
    VX=""
    VO=""
    VN=""
    VS=""
    IA=""
    IO=""
    IN=""
    IX=""

    for k, v in query_dict.iteritems():

        if v and isinstance(v,list) and len(v)>0:

            if k == "body_val_and":
                #VA = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
                VA = Annotation.objects.raw_query({"$or": [{"body.value": {"$in": query_dict[k]}},
                                                           {"body.items.value": {"$in": query_dict[k]}}]})
            if k == "body_val_or":
                #VO = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
                VO = Annotation.objects.raw_query({"$or": [{"body.value": {"$in": query_dict[k]}},
                                                           {"body.items.value": {"$in": query_dict[k]}}]})
            if k == "body_val_not":
                #VN = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
                VN = Annotation.objects.raw_query({"$or": [{"body.value": {"$in": query_dict[k]}},
                                                           {"body.items.value": {"$in": query_dict[k]}}]})
            if k == "body_val_xor":
                #VX = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
                VX = Annotation.objects.raw_query({"$or": [{"body.value": {"$in": query_dict[k]}},
                                                           {"body.items.value": {"$in": query_dict[k]}}]})
            if k == "body_val_syn":
                #VS = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
                VS = Annotation.objects.raw_query({"$or": [{"body.value": {"$in": query_dict[k]}},
                                                           {"body.items.value": {"$in": query_dict[k]}}]})

            if k == "body_id_and":
                IA = Annotation.objects.raw_query({"body.items.source": {"$in": query_dict[ k ]}})
            if k == "body_id_or":
                IO = Annotation.objects.raw_query({"body.items.source": {"$in": query_dict[ k ]}})
            if k == "body_id_not":
                IN = Annotation.objects.raw_query({"body.items.source": {"$in": query_dict[ k ]}})
            if k == "body_id_xor":
                IX = Annotation.objects.raw_query({"body.items.source": {"$in": query_dict[ k ]}})

    exact = []
    related = []

    if VA:
        for ann in VA:
            # Each annotation retrieve by matching on tag label value within a list of labels
            v = {}
            if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type=="Composite":
                v = { ann.body[0].items[len(ann.body[0].items)-1].value }
            elif ann.body and ann.body[0] and ann.body[0].value:
                v = { ann.body[0].value }
            for anno in VA:
                # Compare to other retrieved annotations
                if hasattr(ann.target[0], "source") and hasattr(anno.target[0], "source") and \
                        hasattr(ann.target[0], "jsonld_id") and hasattr(anno.target[0], "jsonld_id"):
                    if ann.target[0].source == anno.target[0].source and ann.target[0].jsonld_id == anno.target[0].jsonld_id:
                        # Collect outer loop annotation tag label value if they share the same target file
                        if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                            v.add( ann.body[0].items[len(ann.body[0].items)-1].value )
                        elif ann.body and ann.body[0] and ann.body[0].value:
                            v.add( ann.body[0].value )
                        break
                elif hasattr(ann.target[0], "source") and hasattr(anno.target[0], "source"):
                    if ann.target[0].source == anno.target[0].source:
                        # Collect outer loop annotation tag label value if they share the same target file
                        if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                            v.add( ann.body[0].items[len(ann.body[0].items)-1].value )
                        elif ann.body and ann.body[0] and ann.body[0].value:
                            v.add( ann.body[0].value )
                        break
                elif hasattr(ann.target[0], "jsonld_id") and hasattr(anno.target[0], "jsonld_id"):
                    if ann.target[0].jsonld_id == anno.target[0].jsonld_id:
                        # Collect outer loop annotation tag label value if they share the same target file
                        if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                            v.add( ann.body[0].items[len(ann.body[0].items)-1].value )
                        elif ann.body and ann.body[0] and ann.body[0].value:
                            v.add( ann.body[0].value )
                        break
            z = {}
            if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                z = set( [ str(itm.source) for itm in ann.body[0].items if itm.type == "SpecificResource" ] )
            if IA:
                for anno in IA:
                    if hasattr(ann.target[0], "source") and hasattr(anno.target[0], "source") and \
                            hasattr(ann.target[0], "jsonld_id") and hasattr(anno.target[0], "jsonld_id"):
                        if ann.target[0].source == anno.target[0].source and \
                                        ann.target[0].jsonld_id == anno.target[0].jsonld_id:
                            if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                                for itm in ann.body[0].items:
                                    if itm.type == "SpecificResource": z.add( str(itm.source) )
                            break
                    elif hasattr(ann.target[0], "source") and hasattr(anno.target[0], "source"):
                        if ann.target[0].source == anno.target[0].source:
                            if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                                for itm in ann.body[0].items:
                                    if itm.type == "SpecificResource": z.add( str(itm.source) )
                            break
                    elif hasattr(ann.target[0], "jsonld_id") and hasattr(anno.target[0], "jsonld_id"):
                        if ann.target[0].jsonld_id == anno.target[0].jsonld_id:
                            if ann.body and ann.body[0] and ann.body[0].type and ann.body[0].type == "Composite":
                                for itm in ann.body[0].items:
                                    if itm.type == "SpecificResource": z.add( str(itm.source) )
                            break
            # Sets of labels and ids from annotations and sharing a target file match those constructed from the search form
            if v == set(query_dict["body_val_and"]) and z == set(query_dict["body_id_and"]):
                exact.append( ann.target[0].source )
                #exact.append( ann )

    if VO:
        for ann in VO:
            #exact.append(ann.target[0].source)
            exact.append( ann )

    if IO:
        for ann in IO:
            #exact.append(ann.target[0].source)
            exact.append( ann )

    if VS:
        for ann in VS:
            #related.append( ann.target[0].source )
            related.append( ann )

    if VX:
        for ann in VX:
            if exact:
                coll = set()
                for anno_temp in exact:
                    if hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source") and \
                            hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                        if anno_temp.target[0].source == ann.target[0].source and \
                                        anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                            coll.add( anno_temp )
                    elif hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source"):
                        if anno_temp.target[0].source == ann.target[0].source:
                            coll.add( anno_temp )
                    elif hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                        if anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                            coll.add( anno_temp )
                for anno_temp in coll:
                    exact.remove( anno_temp )
                if len(coll)==0:
                    if hasattr(ann.target[0], "source"):
                        exact.append(ann)
                    elif hasattr(ann.target[0], "jsonld_id"):
                        exact.append(ann)
                #if ann.target[0].source: exact.append( ann.target[0].source )
                #coll = set()
                #for url in exact:
                #    if url == ann.target[0].source:
                #        coll.add( url )
                #for url in coll:
                #    exact.remove( url )

    if IX:
        for ann in IX:
            if exact:
                coll = set()
                for anno_temp in exact:
                    if hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source") and \
                            hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                        if anno_temp.target[0].source == ann.target[0].source and \
                                        anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                            coll.add( anno_temp )
                    elif hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source"):
                        if anno_temp.target[0].source == ann.target[0].source:
                            coll.add( anno_temp )
                    elif hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                        if anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                            coll.add( anno_temp )
                for anno_temp in coll:
                    exact.remove( anno_temp )
                if len(coll)==0:
                    if hasattr(ann.target[0], "source"):
                        exact.append(ann)
                    elif hasattr(ann.target[0], "jsonld_id"):
                        exact.append(ann)
                # if ann.target[0].source: exact.append( ann.target[0].source )
                # coll = set()
                # for url in exact:
                #     if url == ann.target[0].source:
                #         coll.add( url )
                # for url in coll:
                #     exact.remove( url )

    if exact and VN:
        for ann in VN:
            coll = set()
            for anno_temp in exact:
                if hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source") and \
                        hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                    if anno_temp.target[0].source == ann.target[0].source and \
                                    anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                        coll.add(anno_temp)
                elif hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source"):
                    if anno_temp.target[0].source == ann.target[0].source:
                        coll.add(anno_temp)
                elif hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                    if anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                        coll.add(anno_temp)
            for anno_temp in coll:
                exact.remove(anno_temp)
            # for url in exact:
            #     if ann.target[0].source == url:
            #         exact.remove( url )

    if exact and IN:
        for ann in IN:
            coll = set()
            for anno_temp in exact:
                if hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source") and \
                        hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                    if anno_temp.target[0].source == ann.target[0].source and \
                                    anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                        coll.add(anno_temp)
                elif hasattr(ann.target[0], "source") and hasattr(anno_temp.target[0], "source"):
                    if anno_temp.target[0].source == ann.target[0].source:
                        coll.add(anno_temp)
                elif hasattr(ann.target[0], "jsonld_id") and hasattr(anno_temp.target[0], "jsonld_id"):
                    if anno_temp.target[0].jsonld_id == ann.target[0].jsonld_id:
                        coll.add(anno_temp)
            for anno_temp in coll:
                exact.remove(anno_temp)
            # for url in exact:
            #     if ann.target[0].source == url:
            #         exact.remove( url )

    if exact and query_dict["commenting"] is True:

        C = None
        C = Annotation.objects.raw_query({"$or":[
            {"target.source": {"$in": [ann.target[0].source for ann in exact if hasattr(ann.target[0], "source")]}},
            {"target.jsonld_id": {"$in": [ann.target[0].jsonld_id for ann in exact if hasattr(ann.target[0], "jsonld_id")]}}
        ]})
        #C = Annotation.objects.raw_query({"target.source":{"$in": [u for u in exact]}})

        exact = set()
        if C:
            for ann in C:
                if ann.motivation and ann.motivation[0] == "commenting":
                    exact.add( ann )

    if related and query_dict["commenting"] is True:

        C = None
        C = Annotation.objects.raw_query({"$or":[
            {"target.source": {"$in": [ann.target[0].source for ann in exact if hasattr(ann.target[0], "source")]}},
            {"target.jsonld_id": {"$in": [ann.target[0].jsonld_id for ann in exact if hasattr(ann.target[0], "jsonld_id")]}}
        ]})
        #C = Annotation.objects.raw_query({"target.source": {"$in": [u for u in related]}})

        related = set()
        if C:
            for ann in C:
                if ann.motivation and ann.motivation[0] == "commenting":
                    related.add( ann )

    uniq_tgt = set()
    exact = list(set( exact ))
    exact_cc = exact
    for ann in exact_cc:
        if hasattr(ann.target[0], "source") and hasattr(ann.target[0], "jsonld_id"):
            if ann.target[0].source not in uniq_tgt and ann.target[0].jsonld_id not in uniq_tgt:
                uniq_tgt.add( ann.target[0].source )
                uniq_tgt.add( ann.target[0].jsonld_id )
            else:
                exact.remove( ann )
        elif hasattr(ann.target[0], "source"):
            if ann.target[0].source not in uniq_tgt:
                uniq_tgt.add( ann.target[0].source )
            else:
                exact.remove( ann )
        elif hasattr(ann.target[0], "jsonld_id"):
            if ann.target[0].jsonld_id not in uniq_tgt:
                uniq_tgt.add( ann.target[0].jsonld_id )
            else:
                exact.remove( ann )
    related = list(set( related ))
    related_cc = related
    for ann in related_cc:
        if hasattr(ann.target[0], "source") and hasattr(ann.target[0], "jsonld_id"):
            if ann.target[0].source not in uniq_tgt and ann.target[0].jsonld_id not in uniq_tgt:
                uniq_tgt.add( ann.target[0].source )
                uniq_tgt.add( ann.target[0].jsonld_id )
        elif hasattr(ann.target[0], "source"):
            if ann.target[0].source not in uniq_tgt:
                uniq_tgt.add( ann.target[0].source )
            else:
                related.remove( ann )
        elif hasattr(ann.target[0], "jsonld_id"):
            if ann.target[0].jsonld_id not in uniq_tgt:
                uniq_tgt.add( ann.target[0].jsonld_id )
            else:
                related.remove( ann )

    exact   = list(set( exact ))
    related = list(set( related ))
    related = [ u for u in related if u not in exact ]

    return exact, related, search_str


@login_required
def search_annotations(request):
    user_nickname = None
    if request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    exact = None
    related = None
    search_str = None
    form = []
    cbc = True
    fmessage = None
    while request.POST.get("select"+str(len(form))):
        fdic = {"types": ["Semantic tag", "Free-text keyword", "Comment"],
                "type": "Semantic tag",
                "logicals": ["AND", "OR", "NOT", "XOR"],
                "logical": "AND",
                "syn_incl": False,
                "search_param": None}
        if not cbc: fdic["types"] = ["Semantic tag", "Free-text keyword"]
        if request.POST.get("logical" + str(len(form))):
            if request.POST.get("logical" + str(len(form))) == "AND":
                fdic["logical"] = "AND"
            elif request.POST.get("logical" + str(len(form))) == "OR":
                fdic["logical"] = "OR"
            elif request.POST.get("logical" + str(len(form))) == "NOT":
                fdic["logical"] = "NOT"
            elif request.POST.get("logical" + str(len(form))) == "XOR":
                fdic["logical"] = "XOR"
        if request.POST.get("select"+str(len(form))) == "Semantic tag":
            fdic["type"] = "Semantic tag"
            fdic["search_param"] = None
            if request.POST.get("ontology_json"+ str(len(form))):
                jdic = None
                jdic = json.loads(request.POST.get("ontology_json"+ str(len(form))))
                if jdic:
                    fdic["search_param"] = jdic
                    jstr = None
                    jstr = json.dumps(jdic)
                    if jstr:
                        fdic["search_json"] = jstr
            fdic["syn_incl"] = False
            if request.POST.get("cbox" + str(len(form))) == "syn":
                fdic["syn_incl"] = True
        elif request.POST.get("select" + str(len(form))) == "Free-text keyword":
            fdic["type"] = "Free-text keyword"
            fdic["search_param"] = None
            if request.POST.get("keyword" + str(len(form))):
                fdic["search_param"] = request.POST.get("keyword" + str(len(form)))
        elif cbc and request.POST.get("select" + str(len(form))) == "Comment":
            cbc = False
            fdic["type"] = "Comment"
            fdic["logicals"] = None
            fdic["logical"] = None
        if len(form) == 0:
            fdic["logicals"] = None
            fdic["logical"] = None

        form.append( fdic )

    if request.POST.get("launch_search")!=None:
        if form:
            exact, related, search_str = process_search_query( form )
            exact = [ann.target[0].source for ann in exact if hasattr(ann.target[0], "source")] + \
                    [ann.target[0].jsonld_id for ann in exact if \
                     hasattr(ann.target[0], "jsonld_id") and not hasattr(ann.target[0], "source")]
            related = [ann.target[0].source for ann in related if hasattr(ann.target[0], "source")] + \
                      [ann.target[0].jsonld_id for ann in related if \
                       hasattr(ann.target[0], "jsonld_id") and not hasattr(ann.target[0], "source")]

    elif request.POST.get("plus")!=None:
        if form[len(form)-1]["search_param"] is not None or form[len(form)-1]["type"] == "Comment":
            fdic = {"types": ["Semantic tag", "Free-text keyword", "Comment"],
                    "type": "Semantic tag",
                    "logicals": ["AND", "OR", "NOT", "XOR"],
                    "logical": "AND",
                    "search_param": None,
                           }
            form.append( fdic )
        else:
            fmessage = "Please fill-in the existing fields before adding new ones."

    if form == []: form = [{'logicals': None,
                            'logical': None,
                            'types': ["Semantic tag", "Free-text keyword", "Comment"],
                            'type':"Semantic tag",
                            "syn_incl": False,
                            "search_param":None
                            }]

    navbarlinks = list_navbarlinks(request, ["Search", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_searchpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, ["Search"])

    if search_str or exact or related:

        data_dict = {
            'exact': exact,
            'related': related,
            'search_str': search_str,
            'user_nickname': user_nickname,
            'navbarlinks': navbarlinks,
            'shortcutlinks': shortcutlinks,
        }

        request.session["search_str"] = search_str
        request.session["exact"] = list(exact)
        request.session["related"] = list(related)

        return render(request, "b2note_app/searchresult.html", data_dict)

    data_dict = {
        'fmessage': fmessage,
        'form': form,
        'user_nickname': user_nickname,
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
    }

    return render(request, "b2note_app/searchpage.html", data_dict)


@login_required
def select_search_results(request):
    pid_tofeed = ""
    if request.POST.get('pid_tofeed')!=None:
        pid_tofeed = request.POST.get('pid_tofeed')
        request.session["pid_tofeed"] = pid_tofeed
    elif request.session.get('pid_tofeed'):
        pid_tofeed = request.session.get('pid_tofeed')

    subject_tofeed = ""
    if request.POST.get('subject_tofeed')!=None:
        subject_tofeed = request.POST.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')
        if b2share_correct_url(subject_tofeed): subject_tofeed = b2share_correct_url(subject_tofeed)

    user_nickname = None
    if request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    navbarlinks = list_navbarlinks(request, ["Search", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_exportsearchpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, ["Search"])

    search_str = None
    exact = None
    related = None
    all_exact_cbox = True
    all_related_cbox = True
    export_dic = {
        "exact": [],
        "related": [],
    }

    if "search_str" in request.session.keys() and request.session["search_str"]:
        if isinstance(request.session["search_str"], (str, unicode)):
            search_str = request.session["search_str"]

    if request.POST.get("submit_toselect") is not None:
        if "search_str" in request.session.keys() and request.session["search_str"]:
            if isinstance(request.session["search_str"], (str, unicode)):
                search_str = request.session["search_str"]
        if "exact" in request.session.keys() and request.session["exact"]:
            if isinstance(request.session["exact"], (list,set)):
                for url in request.session["exact"]:
                    if url and isinstance(url, (str, unicode)):
                        export_dic["exact"].append( {"checked": True, "url": url} )
                        all_exact_cbox = True
        if "related" in request.session.keys() and request.session["related"]:
            if isinstance(request.session["related"], (list,set)):
                for url in request.session["related"]:
                    if url and isinstance(url, (str, unicode)):
                        export_dic["related"].append( {"checked": True, "url": url} )
                        all_related_cbox = True

    if request.POST.get("submit_toexport") is not None:
        iterator = 0
        export_dic = {"exact":[], "related":[]}
        while request.POST.get("exact_url"+str(iterator)) or request.POST.get("related_url"+str(iterator)):
            if request.POST.get("exact_cbox"+str(iterator)) and request.POST.get("exact_url"+str(iterator)):
                export_dic["exact"].append( request.POST.get("exact_url"+str(iterator)) )
            if request.POST.get("related_cbox" + str(iterator)) and request.POST.get("related_url" + str(iterator)):
                export_dic["related"].append(request.POST.get("related_url" + str(iterator)))
            iterator += 1

        response = []
        if export_dic and isinstance(export_dic, dict):
            now = datetime.datetime.now()
            nowi = str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)

            #if search_str and isinstance(search_str, (str, unicode)): response["query string"] = search_str
            if "exact" in export_dic.keys() and export_dic["exact"] and isinstance(export_dic["exact"], list):
                #response["exact_match"] = []

                A = Annotation.objects.raw_query({"$or":[\
                    {"target.source": {"$in": export_dic["exact"] }},
                    {"target.jsonld_id": {"$in": export_dic["exact"] }}
                ]}).values()

                for url in export_dic["exact"]:
                    if isinstance(url, (str, unicode)):
                        #exac = {"@context": global_settings.JSONLD_CONTEXT_URL}
                        cleaned = readyQuerySetValuesForDumpAsJSONLD(
                            [ann for ann in A if ann["target"][0][1]["source"] == url or ann["target"][0][1]["jsonld_id"] == url]
                        )
                        #cleaned = ridOflistsOfOneItem( cleaned )
                        #cleaned = orderedJSONLDfields( cleaned )

                        #if isinstance(cleaned, list):
                        #    exac["@graph"] = cleaned
                        #else:
                        #    exac["@graph"] = [cleaned]

                        #response["exact_match"].append(
                        #    {"file_url": url,
                        #    "annotations": exac,}
                        #)

                        if not isinstance(cleaned, list): cleaned = [cleaned]
                        response = cleaned

            if "related" in export_dic.keys() and export_dic["related"] and isinstance(export_dic["related"], list):
                #response["synonym_match"] = []

                A = Annotation.objects.raw_query({"$or": [ \
                    {"target.source": {"$in": export_dic["related"]}},
                    {"target.jsonld_id": {"$in": export_dic["related"]}}
                ]}).values()

                for url in export_dic["related"]:
                    if isinstance(url, (str, unicode)):
                        #relat = {"@context": global_settings.JSONLD_CONTEXT_URL}
                        cleaned = readyQuerySetValuesForDumpAsJSONLD(
                            [ann for ann in A if ann["target"][0][1]["source"] == url or ann["target"][0][1]["jsonld_id"] == url]
                        )
                        #cleaned = ridOflistsOfOneItem(cleaned)
                        #cleaned = orderedJSONLDfields(cleaned)

                        #if isinstance(cleaned, list):
                        #    relat["@graph"] = cleaned
                        #else:
                        #    relat["@graph"] = [cleaned]

                        #response["synonym_match"].append(
                        #    {"file_url": url,
                        #     "annotations": relat, }
                        #)

                        if not isinstance(cleaned, list): cleaned = [cleaned]
                        response = response + cleaned

            if response and isinstance(response, list):
                response = ridOflistsOfOneItem( response )
                response = orderedJSONLDfields( response )

            # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
            #json_data = HttpResponse(json.dumps(response, indent=2), mimetype='application/json')
            #json_data['Content-Disposition'] = 'attachment; filename=' + "b2note_search_" + nowi
            download_json.file_data = response #json_data

        data_dict = {
            'annotations_of': "search_results",
            'navbarlinks': navbarlinks,
            'shortcutlinks': shortcutlinks,
            'user_nickname': user_nickname,
            'annotations_json': json.dumps(response, indent=2),
            "subject_tofeed": subject_tofeed,
            "pid_tofeed": pid_tofeed,
        }

        return render(request, 'b2note_app/export.html', data_dict)

    elif request.POST.get("submit_toselect") is None:
        if request.POST.get("exact_cbox") == "on":
            all_exact_cbox = True
        else:
            all_exact_cbox = False
        if "exact" in request.session.keys() and request.session["exact"]:
            if isinstance(request.session["exact"], (list, set)):
                for url in request.session["exact"]:
                    if url and isinstance(url, (str, unicode)):
                        export_dic["exact"].append({"checked": all_exact_cbox, "url": url})

        if request.POST.get("related_cbox") == "on":
            all_related_cbox = True
        else:
            all_related_cbox = False
        if "related" in request.session.keys() and request.session["related"]:
            if isinstance(request.session["related"], (list, set)):
                for url in request.session["related"]:
                    if url and isinstance(url, (str, unicode)):
                        export_dic["related"].append({"checked": all_related_cbox, "url": url})

    data_dict = {
        'all_exact_cbox': all_exact_cbox,
        'all_related_cbox': all_related_cbox,
        'search_str': search_str,
        'export_dic': export_dic,
        'user_nickname': user_nickname,
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
    }

    return render(request, "b2note_app/select_search_results.html", data_dict)


def helppage(request):
    """
      Function: helppage
      ----------------------------
        Displays help topics centralised on a single page as successive anchors.

        input:
            request (object): context of the petition.

        output:
    """

    navbarlinks = list_navbarlinks(request, ["Help page"])
    shortcutlinks = list_shortcutlinks(request, ["Help page"])

    pagefrom = None
    if request.GET.get('pagefrom') != None:
        pagefrom = request.GET.get('pagefrom')

    user_nickname = None
    if request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    return render(request, "b2note_app/help.html",
                  {'navbarlinks': navbarlinks,
                   'shortcutlinks': shortcutlinks,
                   'pagefrom': pagefrom,
                   'user_nickname':user_nickname})


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

    annotations = RetrieveFileAnnotations(target_id)

    return HttpResponse(annotations)

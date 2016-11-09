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

from itertools import chain

from accounts.models import AnnotatorProfile
import logging



stdlogger = logging.getLogger('b2note')

def index(request):
    return HttpResponse("replace me with index text")


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
            request.session["subject_tofeed"] = subject_tofeed
        elif request.session.get('subject_tofeed'):
            subject_tofeed = request.session.get('subject_tofeed')

        pid_tofeed = ""
        if request.POST.get('pid_tofeed')!=None:
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

            if request.POST.get('user_annotations')!=None and user_nickname:
                annotation_list = RetrieveUserFileAnnotations(subject_tofeed, user_nickname)
                annotation_list = annotation_list.values()
                annotations_of = "mine"

            elif request.POST.get('all_annotations')!=None:
                annotation_list = RetrieveFileAnnotations( subject_tofeed )
                annotation_list = annotation_list.values()
                annotations_of = "all"

            if annotation_list:
                """
                abremaud@esciencedatalab.com, 20160303
                Upon testing on json-ld online playground, none of the URLs provided in current
                 web annotation specification document allowed the context to be retrieved
                 with likely origin of trouble being CORS.
                As a consequence we resort here to embedding rather than linking to the context.
                """
                now = datetime.datetime.now()
                nowi = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)

                #context_str = open(os.path.join(global_settings.STATIC_PATH, 'files/anno_context.jsonld'), 'r').read()
                contextfile_name = "jsonld_context_b2note_20161027.json"
                context_str = "https://b2note-dev.bsc.es/" + contextfile_name

                #response = {"@context": json.loads( context_str, object_pairs_hook=OrderedDict ) }
                response = {"@context": context_str}

                response["@graph"] = readyQuerySetValuesForDumpAsJSONLD( [ann for ann in annotation_list] )

                # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
                json_data = HttpResponse(json.dumps(response, indent=2), mimetype= 'application/json')
                json_data['Content-Disposition'] = 'attachment; filename=' + "b2note_export_" + nowi
                download_json.file_data = json_data

            navbarlinks = list_navbarlinks(request, ["Download"])
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
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

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
    if request.POST.get('db_id'):
        if isinstance(request.POST.get('db_id'), (str, unicode)):
            a_id = request.POST.get('db_id')
            A = Annotation.objects.get(id=a_id)
            if A:
                if request.POST.get('semantic_submit') is not None:
                    edited_semantic = False
                    if request.POST.get('ontology_json'):
                        jo = request.POST.get('ontology_json')
                        if isinstance(jo, (str, unicode)):
                            o = None
                            o = json.loads( jo )
                            if o and isinstance(o, dict):
                                if "uris" in o.keys():
                                    if o["uris"] and isinstance(o["uris"], (str, unicode)):
                                        newbody = None
                                        newbody = {"body": {"jsonld_id": o["uris"]}}
                                        D = None
                                        D = CheckDuplicateAnnotation( A.target[0].jsonld_id , newbody)
                                        if not D:
                                            id1 = None
                                            id1 = MakeAnnotationSemanticTag(a_id, jo)
                                            if id1: edited_semantic = True
                                        else:
                                            duplicate = {
                                                "label": D[0].body[0].value,
                                                "shortform": D[0].body[0].jsonld_id[::-1][:D[0].body[0].jsonld_id[::-1].find("/")][::-1],
                                            }

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
                                D = CheckDuplicateAnnotation( A.target[0].jsonld_id , newbody)
                                if not D:
                                    id1 = None
                                    id1 = MakeAnnotationFreeText(a_id, k_text)
                                    id1 = SetAnnotationMotivation(id1, "tagging")
                                    if id1: edited_keyword = True
                                else:
                                    if D[0].body[0].jsonld_id:
                                        duplicate = {
                                            "label": D[0].body[0].value,
                                            "shortform": D[0].body[0].jsonld_id[::-1][:D[0].body[0].jsonld_id[::-1].find("/")][::-1],
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

                A = Annotation.objects.get(id=a_id)

                if A and A.body and A.body[0] and A.body[0].jsonld_id:
                    shortform = A.body[0].jsonld_id[::-1][:A.body[0].jsonld_id[::-1].find("/")][::-1]

    navbarlinks = list_navbarlinks(request, [])
    shortcutlinks = list_shortcutlinks(request, [])

    data_dict = {
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
        if request.POST.get('db_id'):
            if isinstance(request.POST.get('db_id'), (str, unicode)):
                if request.POST.get("delete_confirmed") is None:
                    navbarlinks = list_navbarlinks(request, [])
                    shortcutlinks = list_shortcutlinks(request, [])
                    data_dict = {
                        'id':request.POST.get('db_id'),
                        'user_nickname': user_nickname,
                        'navbarlinks':navbarlinks,
                        'shortcutlinks':shortcutlinks,
                    }
                    return render(request, 'b2note_app/delete_confirm.html', data_dict)
                A = Annotation.objects.get(id=request.POST.get('db_id'))
                if A:
                    owner = userprofile.nickname == A.creator[0].nickname
                    if owner:
                        R = None
                        R = DeleteFromPOSTinfo( request.POST.get('db_id') )
                        if R:
                            request.session["annotation_deleted"] = True
                            return redirect('/interface_main')
                        else:
                            print "delete_annotation view, annotation delete not successful."
                            pass
                    else:
                        print "delete_annotation view, cannot delete annotation, current user is not owner."
                        stdlogger.error("delete_annotation view, cannot delete annotation, current user is not owner.")
                        pass
                else:
                    print "delete_annotation view, no annotation with provided 'db_id': ", str( request.POST.get('db_id') )
                    stdlogger.error("delete_annotation view, no annotation with provided 'db_id': " + str( request.POST.get('db_id') ))
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
        return redirect('/accounts/logout')
        stdlogger.error("delete_annotation view, user is not logged-in.")
        pass

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
        if request.POST.get('semantic_submit')!=None:
            if request.POST.get('ontology_json') and request.POST.get('subject_tofeed'):
                if isinstance(request.POST.get('subject_tofeed'), (str, unicode)):
                    o = None
                    o = json.loads( request.POST.get('ontology_json') )
                    if o and isinstance(o, dict):
                        if "uris" in o.keys():
                            if o["uris"] and isinstance(o["uris"], (str, unicode)):
                                newbody = None
                                newbody = {"body":{"jsonld_id": o["uris"] }}
                                D = None
                                D = CheckDuplicateAnnotation( request.POST.get('subject_tofeed'), newbody )
                                if not D:
                                    ann_id1 = CreateSemanticTag( request.POST.get('subject_tofeed'), request.POST.get('ontology_json') )
                                    ann_id2 = SetUserAsAnnotationCreator( request.session.get('user'), ann_id1 )
                                    A = Annotation.objects.get( id = ann_id2 )
                                    request.session["new_semantic"] = {
                                        "label": A.body[0].value,
                                        "shortform": A.body[0].jsonld_id[::-1][:A.body[0].jsonld_id[::-1].find("/")][::-1],
                                    }
                                else:
                                    request.session["duplicate"] = {
                                        "label": D[0].body[0].value,
                                        "shortform": D[0].body[0].jsonld_id[::-1][:D[0].body[0].jsonld_id[::-1].find("/")][::-1],
                                    }
                                    print "Create_annotation view, semantic tag annotation would be a duplicate."
                            else:
                                print "Create_annotation view, in semantic case, no value to uris key or neither string or unicode."
                        else:
                            print "Create_annotation view, in semantic case, no uris key."
                    else:
                        print "Create_annotation view, in semantic case, could not load json."
                else:
                    print "Create_annotation view, in semantic case, target file id neither string nor unicode."
            else:
                print "Create_annotation view, missing parameter to create semantic annotation."

        elif request.POST.get('keyword_submit')!=None:
            if request.POST.get('keyword_text') and request.POST.get('subject_tofeed'):

                pass_on = False
                if not request.POST.get('confirm_flag'):
                    r = solr_fetchtermonexactlabel( request.POST.get('keyword_text') )
                    if r and len(r)>0:
                        request.session["has_semantic_equivalent"] = request.POST.get('keyword_text')
                        print "Create_annotation view, keyword has semantic tag equivalent."
                        pass_on = True

                if not pass_on and not request.POST.get('enforce_flag'):
                    L = None
                    L = CheckLengthFreeText( request.POST.get('keyword_text'), 60)
                    if not L:
                        request.session["long_keyword"] = request.POST.get('keyword_text')
                        pass_on = True

                if not pass_on:
                    newbody = None
                    newbody = {"body": {"value": request.POST.get('keyword_text')}}
                    D = None
                    D = CheckDuplicateAnnotation(request.POST.get('subject_tofeed'), newbody)
                    if not D:
                        ann_id1 = CreateFreeTextKeyword( request.POST.get('subject_tofeed'), request.POST.get('keyword_text') )
                        ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1 )
                        A = Annotation.objects.get( id = ann_id2 )
                        request.session["new_keyword"] = { "label": A.body[0].value, }
                    else:
                        if D[0].body[0].jsonld_id:
                            request.session["duplicate"] = {
                                "label": D[0].body[0].value,
                                "shortform": D[0].body[0].jsonld_id[::-1][:D[0].body[0].jsonld_id[::-1].find("/")][::-1],
                            }
                        else:
                            request.session["duplicate"] = { "label": D[0].body[0].value, }
                        print "Create_annotation view, free-text keyword annotation would be a duplicate."

        elif request.POST.get('comment_submit')!=None:
            if request.POST.get('comment_text') and request.POST.get('subject_tofeed'):
                ann_id1 = CreateFreeTextComment(request.POST.get('subject_tofeed'), request.POST.get('comment_text'))
                ann_id2 = SetUserAsAnnotationCreator(request.session.get('user'), ann_id1)
                A = Annotation.objects.get(id=ann_id2)
                request.session["new_comment"] = {"label": A.body[0].value,}

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
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

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

    all_or_mine = None

    allannotations_list = []

    if request.POST.get('db_id')!=None:

        if isinstance(request.POST.get('db_id'), (str, unicode)):

            A = Annotation.objects.get( id = request.POST.get('db_id') )

        if A and A.body and A.body[0]:

            if request.POST.get('about_allsimilar')!=None:

                if A.body[0].jsonld_id!=None:

                    r = solr_fetchorigintermonid([A.body[0].jsonld_id])

                    allannotations_list = Annotation.objects.raw_query({'body.jsonld_id': A.body[0].jsonld_id})

                elif A.body[0].value and A.motivation and A.motivation[0]=="tagging":

                    allannotations_list = Annotation.objects.raw_query(
                        {'body.value': A.body[0].value, 'motivation': "tagging"})

                elif A.body[0].value and A.motivation and A.motivation[0] == "commenting":

                    allannotations_list = A

                if allannotations_list: all_or_mine = "all"

            elif request.POST.get('about_mysimilar') != None:

                if A.body[0].jsonld_id!=None:

                    r = solr_fetchorigintermonid( [A.body[0].jsonld_id] )

                    allannotations_list = Annotation.objects.raw_query(
                        {'body.jsonld_id': A.body[0].jsonld_id, 'creator.nickname': user_nickname})

                elif A.body[0].value and A.motivation and A.motivation[0] == "tagging":

                    allannotations_list = Annotation.objects.raw_query(
                        {'body.value': A.body[0].value, 'motivation': "tagging", 'creator.nickname': user_nickname})

                elif A.body[0].value and A.motivation and A.motivation[0] == "commenting":

                    allannotations_list = A

                if allannotations_list: all_or_mine = "mine"

            if r:
                for rr in r.keys():
                    rrr = r[rr]
                    break

    navbarlinks = list_navbarlinks(request, [])
    shortcutlinks = list_shortcutlinks(request, [])

    data_dict = {
        'r': rrr,
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
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    try:
        allannotations_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed, 'creator.nickname': user_nickname})
    except Annotation.DoesNotExist:
        allannotations_list = []

    allannotations_list = sorted(allannotations_list, key=lambda Annotation: Annotation.created, reverse=True)

    my_s  = 0
    my_k  = 0
    my_c  = 0

    semantic_table = []
    keyword_table  = []
    comment_table  = []

    r = None
    r = solr_fetchorigintermonid([A.body[0].jsonld_id for A in allannotations_list if A.body and A.body[0] and A.body[0].jsonld_id])

    for A in allannotations_list:

        link_label = ""
        link_info_label = ""
        link_info_creatornickname = ""
        link_info_modified = ""

        if A.body and A.body[0] and A.body[0].value:
            if len(A.body[0].value) > 25: link_label = '...'
            link_label = A.body[0].value[:25] + link_label
            if len(A.body[0].value) > 50: link_info_label = '...'
            link_info_label = A.body[0].value[:50] + link_info_label

        if A.creator and A.creator[0] and A.creator[0].nickname:
            link_info_creatornickname = A.creator[0].nickname
        if A.modified: link_info_modified = A.modified

        if A.body and A.body[0] and A.body[0].jsonld_id:

            link_info_ontologyacronym = ""
            link_info_shortform = ""
            if r:
                if isinstance(r, dict):
                    if A.body[0].jsonld_id in r.keys():
                        if isinstance(r[A.body[0].jsonld_id], dict):
                            if "ontology_acronym" in r[A.body[0].jsonld_id].keys():
                                link_info_ontologyacronym = r[A.body[0].jsonld_id]["ontology_acronym"]
                            if "ontology_acronym" in r[A.body[0].jsonld_id].keys():
                                link_info_shortform = r[A.body[0].jsonld_id]["short_form"]

            semantic_list = Annotation.objects.raw_query({'body.jsonld_id': A.body[0].jsonld_id})

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

        elif A.body and A.body[0] and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="tagging":

            print

            keyword_list = Annotation.objects.raw_query({'body.jsonld_id': None, 'body.value': A.body[0].value, 'motivation': "tagging"})

            keyword_dict = {'ann_id': A.id,
                            'link_label': link_label,
                            'link_info_label': link_info_label,
                            'link_info_creatornickname': link_info_creatornickname,
                            'link_info_modified': link_info_modified,
                            'my_similar': len(keyword_list),
                            }

            keyword_table.append( keyword_dict )

            my_k += 1

        elif A.body and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="commenting":

            comment_dict = {'ann_id': A.id,
                            'link_label': link_label,
                            'link_info_label': link_info_label,
                            'link_info_creatornickname': link_info_creatornickname,
                            'link_info_modified': link_info_modified,
                            }

            comment_table.append(comment_dict)

            my_c += 1

    navbarlinks = list_navbarlinks(request, [])
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
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    try:
        allannotations_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
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

    r = None
    r = solr_fetchorigintermonid([A.body[0].jsonld_id for A in allannotations_list if A.body and A.body[0] and A.body[0].jsonld_id])

    for A in allannotations_list:

        link_label = ""
        link_info_label = ""
        link_info_creatornickname = ""
        link_info_modified = ""

        if A.body and A.body[0] and A.body[0].value:
            if len(A.body[0].value) > 25: link_label = '...'
            link_label = A.body[0].value[:25] + link_label
            if len(A.body[0].value) > 50: link_info_label = '...'
            link_info_label = A.body[0].value[:50] + link_info_label

        if A.creator and A.creator[0] and A.creator[0].nickname:
            link_info_creatornickname = A.creator[0].nickname
        if A.modified:
            link_info_modified = A.modified

        if A.body and A.body[0] and A.body[0].jsonld_id:

            link_info_ontologyacronym = ""
            link_info_shortform = ""
            if r:
                if isinstance(r, dict):
                    if A.body[0].jsonld_id in r.keys():
                        if isinstance(r[A.body[0].jsonld_id], dict):
                            if "ontology_acronym" in r[A.body[0].jsonld_id].keys():
                                link_info_ontologyacronym = r[A.body[0].jsonld_id]["ontology_acronym"]
                            if "ontology_acronym" in r[A.body[0].jsonld_id].keys():
                                link_info_shortform = r[A.body[0].jsonld_id]["short_form"]

            semantic_list = Annotation.objects.raw_query({'body.jsonld_id': A.body[0].jsonld_id})

            semantic_dict = {'ann_id': A.id,
                             'link_label': link_label,
                             'link_info_label': link_info_label,
                             'link_info_ontologyacronym': link_info_ontologyacronym,
                             'link_info_shortform': link_info_shortform,
                             'link_info_creatornickname': link_info_creatornickname,
                             'link_info_modified': link_info_modified,
                             'all_similar': len(semantic_list),
                             'my_similar': len([A for A in semantic_list if A.creator and A.creator[0].nickname==user_nickname]),
                             }

            semantic_table.append( semantic_dict )

            all_s += 1

            if A.creator and A.creator[0].nickname==user_nickname:

                my_s += 1

        elif A.body and A.body[0] and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="tagging":

            keyword_list = Annotation.objects.raw_query({'body.jsonld_id': None, 'body.value': A.body[0].value, 'motivation': "tagging"})

            keyword_dict = {'ann_id': A.id,
                            'link_label': link_label,
                            'link_info_label': link_info_label,
                            'link_info_creatornickname': link_info_creatornickname,
                            'link_info_modified': link_info_modified,
                            'all_similar': len(keyword_list),
                            'my_similar': len([A for A in keyword_list if A.creator and A.creator[0].nickname==user_nickname]),
                            }

            keyword_table.append( keyword_dict )

            all_k += 1

            if A.creator and A.creator[0].nickname==user_nickname:

                my_k += 1

        elif A.body and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="commenting":

            comment_dict = {'ann_id': A.id,
                            'link_label': link_label,
                            'link_info_label': link_info_label,
                            'link_info_creatornickname': link_info_creatornickname,
                            'link_info_modified': link_info_modified,
                            }

            comment_table.append(comment_dict)

            all_c += 1

            if A.creator and A.creator[0] and A.creator[0].nickname==user_nickname:

                my_c += 1

    navbarlinks = list_navbarlinks(request, [])
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
    if request.session.get("new_comment"):
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
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

    user_nickname = None
    if not request.session.get('user'):
        context = RequestContext(request, {"subject_tofeed":subject_tofeed, "pid_tofeed":pid_tofeed})
        return redirect('accounts/login', context=context)
    elif request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    #http://stackoverflow.com/questions/5508888/matching-query-does-not-exist-error-in-django
    try:
        # https://blog.scrapinghub.com/2013/05/13/mongo-bad-for-scraped-data/
        # https://github.com/aparo/django-mongodb-engine/blob/master/docs/embedded-objects.rst
        annotation_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
        allannotations_list = Annotation.objects.raw_query({'target.jsonld_id': subject_tofeed})
    except Annotation.DoesNotExist:
        allannotations_list = []

    allannotations_list = sorted(allannotations_list, key=lambda Annotation: Annotation.created, reverse=True)

    all_s = None
    all_k = None
    all_c = None
    my_s  = None
    my_k  = None
    my_c  = None

    all_s = len([A for A in allannotations_list if A.body and A.body[0].jsonld_id ])
    all_k = len([A for A in allannotations_list if A.body and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="tagging" ])
    all_c = len([A for A in allannotations_list if A.body and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="commenting" ])
    if user_nickname:
        my_s  = len([A for A in allannotations_list if A.creator and A.creator[0].nickname==user_nickname
                     and A.body and A.body[0].jsonld_id ])
        my_k  = len([A for A in allannotations_list if A.creator and A.creator[0].nickname==user_nickname
                     and A.body and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="tagging" ])
        my_c  = len([A for A in allannotations_list if A.creator and A.creator[0].nickname==user_nickname
                     and A.body and not A.body[0].jsonld_id and A.motivation and A.motivation[0]=="commenting" ])

    navbarlinks = list_navbarlinks(request, [])
    shortcutlinks = []

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
                    if isinstance(entry["search_param"], dict):
                        if "uris" in entry["search_param"].keys():
                            uri = None
                            uri = entry["search_param"]["uris"]
                            if uri and isinstance(uri, (str, unicode)):
                                if "logical" in entry.keys():
                                    if entry["logical"] and isinstance(entry["logical"], (str, unicode)):
                                        for logic in ["AND", "OR", "NOT", "XOR"]:
                                            if entry["logical"] == logic:
                                                query_dict["body_id_"+str(logic).lower()].append( uri )
                                                if "labels" in entry["search_param"].keys() and \
                                                    entry["search_param"]["labels"] and \
                                                    isinstance( entry["search_param"]["labels"], (str,unicode) ):
                                                        search_str += " " + str(logic).upper() + \
                                                                      " " + str(entry["search_param"]["labels"]) + \
                                                                      "  (" + str(extract_shortform( entry["search_param"] )) + ")"
                                                else:
                                                    search_str += " " + str(logic).upper() + \
                                                                  " " + str(extract_shortform( entry["search_param"] ))
                                    elif entry["logical"] is None:
                                        query_dict["body_id_or"].append(uri)
                                        if "labels" in entry["search_param"].keys() and \
                                                entry["search_param"]["labels"] and \
                                                isinstance(entry["search_param"]["labels"], (str, unicode)):
                                                search_str += " " + str(entry["search_param"]["labels"]) + \
                                                              "  (" + str(extract_shortform(entry["search_param"])) + ")"
                                        else:
                                            search_str += " " + extract_shortform(entry["search_param"])

                        if "syn_incl" in entry.keys() and entry["syn_incl"] is True:
                            if "synonyms" in entry["search_param"].keys():
                                syns = None
                                syns = entry["search_param"]["synonyms"]
                                if syns and isinstance(syns, list):
                                    for syn in syns:
                                        if syn and isinstance(syn, (str, unicode)):
                                            query_dict["body_val_syn"].append( syn )
                                            search_str += " SYN " + syn
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
                VA = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
            if k == "body_val_or":
                VO = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
            if k == "body_val_not":
                VN = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
            if k == "body_val_xor":
                VX = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})
            if k == "body_val_syn":
                VS = Annotation.objects.raw_query({"body.value": {"$in": query_dict[ k ]}})

            if k == "body_id_and":
                IA = Annotation.objects.raw_query({"body.jsonld_id": {"$in": query_dict[ k ]}})
            if k == "body_id_or":
                IO = Annotation.objects.raw_query({"body.jsonld_id": {"$in": query_dict[ k ]}})
            if k == "body_id_not":
                IN = Annotation.objects.raw_query({"body.jsonld_id": {"$in": query_dict[ k ]}})
            if k == "body_id_xor":
                IX = Annotation.objects.raw_query({"body.jsonld_id": {"$in": query_dict[ k ]}})

    exact = []
    related = []

    if VA:
        for ann in VA:
            v = { ann.body[0].value }
            for anno in VA:
                if ann.target[0].jsonld_id == anno.target[0].jsonld_id:
                    if ann.body[0].value: v.add( ann.body[0].value )
            z = { ann.body[0].value }
            if IA:
                for anno in IA:
                    if ann.target[0].jsonld_id == anno.target[0].jsonld_id:
                        if ann.body[0].jsonld_id: z.add( ann.body[0].jsonld_id )
            if v == set(query_dict["body_val_and"]) and z == set(query_dict["body_id_and"]):
                exact.append( ann.target[0].jsonld_id )

    if VO:
        for ann in VO:
            exact.append(ann.target[0].jsonld_id)

    if IO:
        for ann in IO:
            exact.append(ann.target[0].jsonld_id)

    if VS:
        for ann in VS:
            related.append( ann.target[0].jsonld_id )

    if VX:
        for ann in VX:
            if exact:
                if ann.target[0].jsonld_id: exact.add( ann.target[0].jsonld_id )
                coll = set()
                for url in exact:
                    if url == ann.target[0].jsonld_id:
                        coll.add( url )
                for url in coll:
                    exact.remove( url )

    if IX:
        for ann in IX:
            if exact:
                if ann.target[0].jsonld_id: exact.add( ann.target[0].jsonld_id )
                coll = set()
                for url in exact:
                    if url == ann.target[0].jsonld_id:
                        coll.add( url )
                for url in coll:
                    exact.remove( url )

    if exact and VN:
        for ann in VN:
            for url in exact:
                if ann.target[0].jsonld_id == url:
                    exact.remove( url )

    if exact and IN:
        for ann in IN:
            for url in exact:
                if ann.target[0].jsonld_id == url:
                    exact.remove( url )

    if exact and query_dict["commenting"] is True:

        C = None
        C = Annotation.objects.raw_query({"target.jsonld_id": {"$in": [u for u in exact]}})

        exact = set()
        if C:
            for ann in C:
                if ann.target[0].jsonld_id not in exact:
                    if ann.motivation and ann.motivation[0] == "commenting":
                        exact.add( ann.target[0].jsonld_id )

    if related and query_dict["commenting"] is True:

        C = None
        C = Annotation.objects.raw_query({"target.jsonld_id": {"$in": [u for u in related]}})

        related = set()
        if C:
            for ann in C:
                if ann.target[0].jsonld_id not in related:
                    if ann.motivation and ann.motivation[0] == "commenting":
                        related.add(ann.target[0].jsonld_id)

    exact = list(set( exact ))
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

    navbarlinks = list_navbarlinks(request, ["Search"])
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
        request.session["subject_tofeed"] = subject_tofeed
    elif request.session.get('subject_tofeed'):
        subject_tofeed = request.session.get('subject_tofeed')

    user_nickname = None
    if request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    navbarlinks = list_navbarlinks(request, ["Search"])
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

        response = {}
        if export_dic and isinstance(export_dic, dict):
            now = datetime.datetime.now()
            nowi = str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)
            contextfile_name = "jsonld_context_b2note_20161027.json"
            context_str = "https://b2note-dev.bsc.es/" + contextfile_name

            if search_str and isinstance(search_str, (str, unicode)): response["query string"] = search_str
            if "exact" in export_dic.keys() and export_dic["exact"] and isinstance(export_dic["exact"], list):
                response["exact_match"] = []

                A = Annotation.objects.raw_query({"target.jsonld_id": {"$in": export_dic["exact"] }}).values()

                for url in export_dic["exact"]:
                    if isinstance(url, (str, unicode)):
                        exac = {"@context": context_str}
                        exac["@graph"] = readyQuerySetValuesForDumpAsJSONLD([ann for ann in A if
                                                                             ann["target"][0][1]["jsonld_id"] == url])
                        response["exact_match"].append(
                            {"file_url": url,
                            "annotations": exac,}
                        )

            if "related" in export_dic.keys() and export_dic["related"] and isinstance(export_dic["related"], list):
                response["synonym_match"] = []

                A = Annotation.objects.raw_query({"target.jsonld_id": {"$in": export_dic["related"]}}).values()

                for url in export_dic["related"]:
                    if isinstance(url, (str, unicode)):
                        relat = {"@context": context_str}
                        relat["@graph"] = readyQuerySetValuesForDumpAsJSONLD([ann for ann in A if
                                                                             ann["target"][0][1]["jsonld_id"] == url])
                        response["synonym_match"].append(
                            {"file_url": url,
                             "annotations": relat, }
                        )

            # http://stackoverflow.com/questions/7732990/django-provide-dynamically-generated-data-as-attachment-on-button-press
            json_data = HttpResponse(json.dumps(response, indent=2), mimetype='application/json')
            json_data['Content-Disposition'] = 'attachment; filename=' + "b2note_search_" + nowi
            download_json.file_data = json_data

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


@login_required
def search_annotations_bck(request):
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

    user_nickname = None
    if request.session.get('user')!=None:
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        user_nickname = userprofile.nickname

    navbarlinks = list_navbarlinks(request, ["Search"])
    shortcutlinks = list_shortcutlinks(request, ["Search"])

    return render(request, "b2note_app/searchpage.html", {
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'user_nickname': user_nickname,
        'keywd_json': keywd_json,
        'label_match': label_match,
        'synonym_match':synonym_match})


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

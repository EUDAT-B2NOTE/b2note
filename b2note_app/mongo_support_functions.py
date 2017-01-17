import os, re, datetime, copy, collections
import json, bson
import requests

from .models import *
from accounts.models import AnnotatorProfile

from django.forms.models import model_to_dict
from django.conf import settings as global_settings
import logging

stdlogger = logging.getLogger('b2note')



def solr_fetchtermonexactlabel(label=None):
    out = None
    try:
        if label:
            if isinstance(label, (str, unicode)):
                r = requests.get('https://b2note.bsc.es/solr/b2note_index/select?q=labels:"' + label + '"&wt=json&indent=true&start=0&rows=100')
                out = []
                for rr in r.json()["response"]["docs"]:
                    if rr["labels"].lower() == label.lower():
                        out.append( rr )
                return out
            else:
                print "solr_fetchtermonexactlabel fuction, parameter neither string nor unicode."
                stdlogger.error("solr_fetchtermonexactlabel fuction, parameter neither string nor unicode.")
        else:
            print "solr_fetchtermonexactlabel function, empty parameter."
            stdlogger.error("solr_fetchtermonexactlabel function, empty parameter.")
    except:
        print "solr_fetchtermonexactlabel function, could not complete."
        stdlogger.error("solr_fetchtermonexactlabel function, could not complete.")
        return False
    return False


def solr_fetchorigintermonid(ids=None):
    out = None
    try:
        if ids:
            if isinstance(ids, list):
                q_str = ""
                for id in ids:
                    if isinstance(id, (str, unicode)):
                        q_str += 'OR "' + id + '" '
                if q_str:
                    q_str = q_str.replace("#","%23")
                    q_str = "(" + q_str[3:] + ")"
                    r = None
                    r = requests.get(
                        'https://b2note.bsc.es/solr/b2note_index/select?q=uris:' + q_str +'&fl=ontology_acronym,ontology_name,description,uris,labels,short_form&wt=json&indent=true&start=0&rows=' + str(10*len(ids)))
                    if r and r.json():
                        if isinstance(r.json(), dict):
                            if "response" in r.json().keys():
                                if isinstance(r.json()["response"], dict):
                                    if "docs" in r.json()["response"].keys():
                                        if isinstance(r.json()["response"]["docs"], list):
                                            out = {}
                                            for rr in r.json()["response"]["docs"]:
                                                if isinstance(rr, dict):
                                                    if "ontology_acronym" in rr.keys() and "uris" in rr.keys():
                                                        if rr["uris"] not in out.keys():
                                                            out[ rr["uris"] ] = rr
                                                        elif rr["ontology_acronym"] in rr["uris"]:
                                                            out[ rr["uris"] ] = rr
                                            return out
                                        else:
                                            print "solr_fetchorigintermonid fuction, requests object json>response>docs not a list."
                                            stdlogger.error("solr_fetchorigintermonid fuction, requests object json>response>docs not a list.")
                                    else:
                                        print "solr_fetchorigintermonid fuction, 'docs' not a key of requests object json>response dict."
                                        stdlogger.error("solr_fetchorigintermonid fuction, 'docs' not a key of requests object json>response dict.")
                                else:
                                    print "solr_fetchorigintermonid fuction, requests object json>response not a dict"
                                    stdlogger.error("solr_fetchorigintermonid fuction, requests object json>response not a dict")
                            else:
                                print "solr_fetchorigintermonid fuction, 'response' not a key of requests object json dict."
                                stdlogger.error("solr_fetchorigintermonid fuction, 'response' not a key of requests object json dict.")
                        else:
                            print "solr_fetchorigintermonid fuction, requests object json not a dict."
                            stdlogger.error("solr_fetchorigintermonid fuction, requests object json not a dict.")
                    else:
                        print "solr_fetchorigintermonid fuction, sorl fetch with no response or response not json."
                        stdlogger.error("solr_fetchorigintermonid fuction, sorl fetch with no response or response not json.")
                else:
                    print "solr_fetchorigintermonid fuction, list item neither string nor unicode."
                    stdlogger.error("solr_fetchorigintermonid fuction, list item neither string nor unicode.")
            else:
                print "solr_fetchorigintermonid fuction, paramter not a list."
                stdlogger.error("solr_fetchorigintermonid fuction, paramter not a list.")
        else:
            print "solr_fetchorigintermonid function, empty parameter."
            stdlogger.error("solr_fetchorigintermonid function, empty parameter.")
    except:
        print "solr_fetchorigintermonid function, could not complete."
        stdlogger.error("solr_fetchorigintermonid function, could not complete.")
        return False
    return False


def solr_fetchtermonid(id=None):
    out = None
    try:
        if id:
            if isinstance(id, (str, unicode)):
                r = requests.get('https://b2note.bsc.es/solr/b2note_index/select?q=uris:"' + id + '"&wt=json&indent=true&start=0&rows=100')
                return r
            else:
                print "solr_fetchtermonid fuction, parameter neither string nor unicode."
                stdlogger.error("solr_fetchtermonid fuction, parameter neither string nor unicode.")
        else:
            print "solr_fetchtermonid function, empty parameter."
            stdlogger.error("solr_fetchtermonid function, empty parameter.")
    except:
        print "solr_fetchtermonid function, could not complete."
        stdlogger.error("solr_fetchtermonid function, could not complete.")
        return False
    return False


def SearchAnnotation( kw ):
    """
      Function: SearchAnnotation
      ----------------------------
        Seaches for an annotation matching with the provided body value.

        params:
            kw (str): Body value.

        returns:
            A (object): Object of the matching annotation, False otherwise.
    """

    try:

        if kw:

            if isinstance( kw, (str, unicode)):

                A = Annotation.objects.raw_query({'body.value': kw})

                print "SearchAnnotation function, returning annotations with body value: ", kw
                stdlogger.info("SearchAnnotation function, returning annotations with body value: " + str(kw))
                return A

            else:
                print "SearchAnnotation function, provided keyword argument neither str nor unicode."
                stdlogger.error("SearchAnnotation function, provided keyword argument neither str nor unicode.")
                return False
        else:
            print "SearchAnnotation function, missing 'kw' string argument."
            stdlogger.error("SearchAnnotation function, missing 'kw' string argument.")
            return False
    except:
        print "SearchAnnotation function did not complete."
        stdlogger.error("SearchAnnotation function did not complete.")
        return False

    print "SearchAnnotation function did not complete succesfully."
    stdlogger.error("SearchAnnotation function did not complete succesfully.")
    return False


def RetrieveUserAnnotations( nickname=None ):
    """
      Function: RetrieveAnnotations_perUsername
      ----------------------------
        Retrieves all annotations having creator.nickname for a given file.

        params:
            subject_url (str): ID of the file.
            nickname (str): user nickname as from user profile DB record.

        returns:
            dic: Dictionary with the values of the annotations.
    """
    try:

        if nickname and isinstance(nickname, (str, unicode)):
            annotations = None
            annotations = Annotation.objects.raw_query({'creator.nickname': nickname})
            #annotations = sorted(annotations, key=lambda Annotation: Annotation.created, reverse=True)
            if annotations:
                print "RetrieveUserFileAnnotations function, returning annotations."
                stdlogger.info("RetrieveUserFileAnnotations function, returning annotations.")
                return annotations
            else:
                print "RetrieveUserFileAnnotations function, no annotations retrieved."
                stdlogger.info("RetrieveUserFileAnnotations function, no annotations retrieved.")
                return None
        else:
            print "RetrieveUserFileAnnotations function, provided nickname not valid:", nickname
            stdlogger.info("RetrieveUserFileAnnotations function, provided nickname not valid:" + str(nickname))
            return False

    except Annotation.DoesNotExist:
        print "RetrieveUserFileAnnotations function did not complete."
        stdlogger.error("RetrieveUserFileAnnotations function did not complete.")
        return False

    print "RetrieveUserFileAnnotations function did not complete succesfully."
    stdlogger.error("RetrieveUserFileAnnotations function did not complete succesfully.")
    return False


def RetrieveFileAnnotations( subject_url ):
    """
      Function: RetrieveAnnotations
      ----------------------------
        Retrieves all annotations for a given file.
        
        params:
            subject_url (str): ID of the file.
        
        returns:
            dic: Dictionary with the values of the annotations.
    """
    try:
        annotations = Annotation.objects.raw_query({'target.jsonld_id': subject_url})

    except Annotation.DoesNotExist:
        annotations = []

    #annotations = sorted(annotations, key=lambda Annotation: Annotation.created, reverse=True)

    return annotations


def DeleteFromPOSTinfo( db_id ):
    """
      Function: DeleteFromPOSTinfo
      ----------------------------
        Removes an annotation from MongoDB.
        
        params:
            db_id (str): ID of the document to remove.
        
        returns:
            bool: True if successful, False otherwise.
    """
    del_flag = False
    try:
        if db_id and isinstance(db_id, (str, unicode)) and len(db_id)>0:
            Annotation.objects.get(id=db_id).delete()
            del_flag = True
        else:
            print "Argument provided is not a valid collection document id"
            stdlogger.error("Argument provided is not a valid collection document id")
    except ValueError:
        pass

    if del_flag:
        print "Removed an Annotation from DB"
        stdlogger.info("Removed an Annotation from DB")
        return True

    print "Could not remove from DB"
    stdlogger.error("Could not remove from DB")
    return False


def SetDateTimeModified( db_id=None ):
    """
      Function: SetDateTimeModified
      ----------------------------
        Sets date time of modified fields in annotation on change.

        params:
            db_id (str): database id of the document to modify.

        returns:
            id (str): database id of the modified document if successful, False otherwise.
    """
    try:

        if db_id:

            if isinstance(db_id, (str, unicode)):

                A = None
                A = Annotation.objects.get(id=db_id)

                if A:

                    nowdt = datetime.datetime.now()

                    A.modified = nowdt

                    if A.body:

                        if isinstance(A.body, list):

                            if len(A.body)>0:

                                A.body[0].modified = nowdt

                    A.save()

                    print 'SetDateTimeModified function, "' + str(nowdt) + '" set as modified date time of annotation: ', str(db_id)
                    stdlogger.info('SetDateTimeModified function, "' + str(nowdt) + '" set as modified date time of annotation: ' + str(db_id))
                    return A.id

                else:
                    print "SetDateTimeModified function, no annotation wit id: ", str(db_id)
                    stdlogger.error("SetDateTimeModified function, no annotation wit id: " + str(db_id))
                    return False
            else:
                print "SetDateTimeModified function, 'db_id' parameter neither str nor unicode."
                stdlogger.error("SetDateTimeModified function, 'db_id' parameter neither str nor unicode.")
                return False
        else:
            print "SetDateTimeModified function, missing parameter called 'db_id'."
            stdlogger.error("SetDateTimeModified function, missing parameter called 'db_id'.")
            return False

    except ValueError:
        print "SetDateTimeModified function did not complete."
        stdlogger.error("SetDateTimeModified function did not complete.")
        return False

    print "SetDateTimeModified function did not complete succesfully."
    stdlogger.error("SetDateTimeModified function did not complete succesfully.")
    return False



def SetAnnotationMotivation( db_id=None, motiv=None ):
    """
      Function: SetAnnotationMotivation
      ----------------------------
        Sets annotation motivation from existing Web Annotation set.

        params:
            db_id (str): database id of the document to modify.
            motiv (str): motivation to be attributed to annotation document and as body purpose.

        returns:
            id (str): database id of the modified document if successful, False otherwise.
    """
    try:

        if db_id:

            if isinstance(db_id, (str, unicode)):

                A = None
                A = Annotation.objects.get(id=db_id)

                if A:

                    if motiv:

                        if isinstance(motiv, (str, unicode)):

                            if (motiv, motiv) in Annotation.MOTIVATION_CHOICES:

                                A.motivation = [ motiv ]

                                if A.body:

                                    if isinstance(A.body, list):

                                        if len(A.body)>0:

                                            A.body[0].purpose = motiv

                                A.save()

                                print 'SetAnnotationMotivation function, "' + motiv + '" set as motivation of annotation: ', str(db_id)
                                stdlogger.info('SetAnnotationMotivation function, "' + motiv + '" set as motivation of annotation: ' + str(db_id))
                                return A.id

                            else:
                                print "SetAnnotationMotivation function, provided string parameter not part of predefined set of motivations."
                                stdlogger.error("SetAnnotationMotivation function, provided string parameter not part of predefined set of motivations.")
                                return False
                        else:
                            print "SetAnnotationMotivation function, parameter provided for motivation neither string nor unicode."
                            stdlogger.error("SetAnnotationMotivation function, parameter provided for motivation neither string nor unicode.")
                            return False
                    else:
                        print "SetAnnotationMotivation function, missing motivation parameter."
                        stdlogger.error("SetAnnotationMotivation function, missing motivation parameter.")
                        return False
                else:
                    print "SetAnnotationMotivation function, no annotation wit id: ", str(db_id)
                    stdlogger.error("SetAnnotationMotivation function, no annotation wit id: " + str(db_id))
                    return False
            else:
                print "SetAnnotationMotivation function, 'db_id' parameter neither str nor unicode."
                stdlogger.error("SetAnnotationMotivation function, 'db_id' parameter neither str nor unicode.")
                return False
        else:
            print "SetAnnotationMotivation function, missing parameter called 'db_id'."
            stdlogger.error("SetAnnotationMotivation function, missing parameter called 'db_id'.")
            return False

    except ValueError:
        print "SetAnnotationMotivation function did not complete."
        stdlogger.error("SetAnnotationMotivation function did not complete.")
        return False

    print "SetAnnotationMotivation function did not complete succesfully."
    stdlogger.error("SetAnnotationMotivation function did not complete succesfully.")
    return False


def SetUserAsAnnotationCreator( user_id=None, db_id=None ):
    """
      Function: SetUserAsAnnotationCreator
      ----------------------------
        Sets annotator profile corresponding to user_id input parameter
            as creator agent of annotation document with id matching db_id
            input parameter.

        params:
            user_id (int): sqlite3 primary key of annotator profile model.
            db_id (unicode): mongodb document id.

        returns:
            id (str): database id of the create document if successful, False otherwise.
    """
    try:

        if user_id and isinstance(user_id, int) and user_id>=0:

            ap = None

            ap = AnnotatorProfile.objects.using('users').get(annotator_id=user_id)

            if ap and ap.nickname and isinstance(ap.nickname, (str, unicode)):

                if db_id and isinstance(db_id, (str, unicode)):

                    annotation = None

                    annotation = Annotation.objects.get(id=db_id)

                    if annotation:

                        annotation.creator = [Agent(
                            type = ['Person'],
                            nickname = str(ap.nickname)
                        )]
                        annotation.save()

                        print "User with nickname ", str(ap.nickname) ,", set as annotation ", annotation.id ," creator"
                        stdlogger.info("User with nickname " + str(ap.nickname) + ", set as annotation " + annotation.id + " creator")
                        return annotation.id

                    else:
                        print "SetUserAsAnnotationCreator function, no annotation were found matching this id: ", str(db_id)
                        stdlogger.error("SetUserAsAnnotationCreator function, no annotation were found matching this id: " + str(db_id))

                else:
                    print "SetUserAsAnnotationCreator function, provided parameter for annotation id invalid."
                    stdlogger.error("SetUserAsAnnotationCreator function, provided parameter for annotation id invalid.")

            else:
                print "SetUserAsAnnotationCreator function, no registered annotator profile with id: ", user_id
                stdlogger.error("SetUserAsAnnotationCreator function, no registered annotator profile with id: " + user_id)

        else:
            print "SetCurrentUserAsAnnotationCreator function, provided parameter for annotator profile id invalid."
            stdlogger.error("SetCurrentUserAsAnnotationCreator function, provided parameter for annotator profile id invalid.")

    except Exception:
        print "SetUserAsAnnotationCreator function did not complete."
        stdlogger.error("SetUserAsAnnotationCreator function did not complete.")
        return False

    print "SetUserAsAnnotationCreator function did not complete succesfully."
    stdlogger.error("SetUserAsAnnotationCreator function did not complete succesfully.")
    return False


# def DuplicateAnnotation( db_id=None ):
#     """
#       Function: DulicateAnnotation
#       ----------------------------
#         Duplicates an annotation in MongoDB.
#
#         params:
#             db_id (str): database id of the annotation document to duplicate.
#
#         returns:
#             id (str): database id of the created annotation document.
#     """
#     try:
#
#         if db_id:
#
#             if isinstance(db_id, (str, unicode)):
#
#                 A = None
#                 A = Annotation.objects.get(id=db_id)
#
#                 if A:
#
#                     if A.target:
#
#                         if isinstance(A.target, list):
#
#                             if len(A.target)>0:
#
#                                 if A.target[0]:
#
#                                     if A.target[0].jsonld_id:
#
#                                         if isinstance(A.target[0].jsonld_id, (str, unicode)):
#
#                                             B = CreateAnnotation( A.target[0].jsonld_id )
#                                             B = Annotation.objects.get( id = B )
#
#                                             ann = copy.deepcopy( A )
#
#                                             B_dict = {k: v for k, v in B.__dict__.iteritems() if v is not None}
#                                             ann.__dict__.update(B_dict)
#
#                                             ann.save()
#
#                                             print "DuplicateAnnotation function, created annotation document with id: " + str(ann.id)
#                                             stdlogger.info("DuplicateAnnotation function, created annotation document with id: " + str(ann.id))
#                                             return ann.id
#
#                                         else:
#                                             print "DuplicateAnnotation function, annotation document target 'jsonld_id' neither str nor unicode."
#                                             stdlogger.error("DuplicateAnnotation function, annotation document target 'jsonld_id' neither str nor unicode.")
#                                             return False
#                                     else:
#                                         print "DuplicateAnnotation function, missing annotation document target 'jsonld_id'."
#                                         stdlogger.error("DuplicateAnnotation function, missing annotation document target 'jsonld_id'.")
#                                         return False
#                                 else:
#                                     print "DuplicateAnnotation function, no element in annotation document target list."
#                                     stdlogger.error("DuplicateAnnotation function, no element in annotation document target list.")
#                                     return False
#                             else:
#                                 print "DuplicateAnnotation function, annotation doument target list empty."
#                                 stdlogger.error("DuplicateAnnotation function, annotation doument target list empty.")
#                                 return False
#                         else:
#                             print "DuplicateAnnotation function, annotation doument target is not of type list."
#                             stdlogger.error("DuplicateAnnotation function, annotation doument target is not of type list.")
#                             return False
#                     else:
#                         print "DuplicateAnnotation function, annotation document missing target field."
#                         stdlogger.error("DuplicateAnnotation function, annotation document missing target field.")
#                         return False
#             else:
#                 print "DuplicateAnnotation function, provided 'db_id' argument neither str nor unicode."
#                 stdlogger.error("DuplicateAnnotation function, provided 'db_id' argument neither str nor unicode.")
#                 return False
#
#         else:
#             print "DuplicateAnnotation function, missing 'db_id' argument."
#             stdlogger.error("DuplicateAnnotation function, missing 'db_id' argument.")
#             return False
#
#     except ValueError:
#         print "DuplicateAnnotation function, did not complete."
#         stdlogger.error("DuplicateAnnotation function, did not complete.")
#         return False
#
#     print "DuplicateAnnotation function did not complete succesfully."
#     stdlogger.error("DuplicateAnnotation function did not complete succesfully.")
#     return False


def CreateSemanticTag( subject_url=None, object_json=None ):
    """
      Function: CreateSemanticTag
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            subject_url (str): URL of the annotation to create.
            object_json (str): JSON of the annotation provided by SOLR
        
        returns:
            db_id (str): database id of the modified annotation if successful, False otherwise.
    """
    try:

        if subject_url and isinstance(subject_url, (str, unicode)):

            my_id = None
            my_id = CreateAnnotation(subject_url)
    
            if my_id:

                if object_json and isinstance(object_json, (str, unicode)):

                    db_id = MakeAnnotationSemanticTag( my_id, object_json )

                    db_id = SetAnnotationMotivation( db_id, "tagging" )

                    print "MakeAnnotationSemanticTag function, made annotation semantic tag: ", str(db_id)
                    stdlogger.info("MakeAnnotationSemanticTag function, made annotation semantic tag: " + str(db_id))
                    return db_id

                else:
                    print "CreateSemanticTag function, provided json object is neither string nor unicode."
                    stdlogger.error("CreateSemanticTag function, provided json object is neither string nor unicode.")
                    return False
            else:
                print "CreateSemanticTag function, internal call to CreateAnnotation function did not return an exploitable id reference."
                stdlogger.error("CreateSemanticTag function, internal call to CreateAnnotation function did not return an exploitable id reference.")
                return False
        else:
            print "CreateSemanticTag function, provided parameter is not a valid string for subject_url."
            stdlogger.error("CreateSemanticTag function, provided parameter is not a valid string for subject_url.")
            return False

    except ValueError:
        print "CreateSemanticTag function did not complete."
        stdlogger.error("CreateSemanticTag function did not complete.")
        return False

    print "CreateSemanticTag function did not complete succesfully."
    stdlogger.error("CreateSemanticTag function did not complete succesfully.")
    return False


def CreateFreeTextKeyword( subject_url=None, text=None ):
    """
      Function: CreateFreeTextKeyword
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            subject_url (str): URL of the annotation to create.
            text (str): Free text introduced by the user
        
        returns:
            db_id (str): database id of the modified annotation if successful, False otherwise.
    """
    try:

        my_id = CreateAnnotation(subject_url)

        if my_id:

            if isinstance( my_id, (str, unicode) ):

                if isinstance(text, (str, unicode)) and len(text) > 0:

                    db_id = None
                    db_id = MakeAnnotationFreeText(my_id, text)

                    db_id = SetAnnotationMotivation( db_id, "tagging" )

                    if db_id:
                        print "CreateFreeTextKeyword function, created free-text keyword annotation:", str(db_id)
                        stdlogger.info("CreateFreeTextKeyword function, created free-text keyword annotation:" + str(db_id))
                        return db_id
                    else:
                        print "CreateFreeTextKeyword function, free-text keyword annotation make unreturned."
                        stdlogger.info("CreateFreeTextKeyword function, free-text keyword annotation make unreturned.")
                        return False
                else:
                    print "CreateFreeTextKeyword function, wrong text codification or empty text."
                    stdlogger.error("CreateFreeTextKeyword function, wrong text codification or empty text.")
                    return False
            else:
                print "CreateFreeTextKeyword function, 'my_id' parameter neither str nor unicode."
                stdlogger.error("CreateFreeTextKeyword function, 'my_id' parameter neither str nor unicode.")
                return False
        else:
            print "CreateFreeTextKeyword function, annotation not created or id not returned."
            stdlogger.error("CreateFreeText function, annotation not created or id not returned.")
            return False

    except ValueError:
        print "CreateFreeTextKeyword function did not complete."
        stdlogger.error("CreateFreeTextKeyword function did not complete.")
        return False

    print "CreateFreeTextKeyword function did not complete succesfully."
    stdlogger.error("CreateFreeTextKeyword function did not complete succesfully.")
    return False


def CreateFreeTextComment(subject_url=None, text=None):
    """
      Function: CreateFreeTextComment
      ----------------------------
        Creates an annotation in MongoDB.

        params:
            subject_url (str): URL of the annotation to create.
            text (str): Free text introduced by the user

        returns:
            db_id (str): database id of the modified annotation if successful, False otherwise.
    """
    try:

        my_id = CreateAnnotation(subject_url)

        if my_id:

            if isinstance(my_id, (str, unicode)):

                if isinstance(text, (str, unicode)) and len(text) > 0:

                    db_id = None
                    db_id = MakeAnnotationFreeText(my_id, text)

                    db_id = SetAnnotationMotivation(db_id, "commenting")

                    if db_id:
                        print "CreateFreeTextComment function, created free-text comment annotation:", str(db_id)
                        stdlogger.info("CreateFreeTextComment function, created free-text comment annotation:", str(db_id))
                        return db_id
                    else:
                        print "CreateFreeTextComment function, free-text comment annotation created not returned."
                        stdlogger.info("CreateFreeTextComment function, free-text comment annotation created not returned.")
                        return False

                else:
                    print "CreateFreeTextComment function, wrong text codification or empty text."
                    stdlogger.info("CreateFreeTextComment function, wrong text codification or empty text.")
                    return False
            else:
                print "CreateFreeTextComment function, 'my_id' parameter neither str nor unicode."
                stdlogger.info("CreateFreeTextComment function, 'my_id' parameter neither str nor unicode.")
                return False
        else:
            print "CreateFreeTextComment function, annotation not created or id not returned."
            stdlogger.info("CreateFreeTextComment function, annotation not created or id not returned.")
            return False

    except ValueError:
        print "CreateFreeTextComment function did not complete."
        stdlogger.info("CreateFreeTextComment function did not complete.")
        return False

    print "CreateFreeTextComment function did not complete succesfully."
    stdlogger.info("CreateFreeTextComment function did not complete succesfully.")
    return False


def MakeAnnotationSemanticTag( db_id=None, object_json=None ):
    """
      Function: MakeAnnotationSemanticTag
      -----------------------------------
        Adds semantic tag body to an annotation.

        params:
            db_id (str): database id of the annotation to which the semantic tag body can be attached.
            object_json (str): JSON of the annotation provided by SOLR.

        returns:
            db_id (str): database id of the modified annotation if successful, False otherwise.
    """
    try:

        if db_id:

            if isinstance(db_id, (str, unicode)):

                A = None
                A = Annotation.objects.get(id=db_id)

                if A:

                    if object_json and isinstance(object_json, (str, unicode)):
                        o = None
                        o = json.loads(object_json)

                        if o and isinstance(o, dict):
                            if "uris" in o.keys():
                                if o["uris"] and isinstance(o["uris"], (str, unicode)):
                                    object_uri = ""
                                    object_label = ""
                                    object_uri = o["uris"]

                                    if "labels" in o.keys():
                                        if o["labels"] and isinstance(o["labels"], (str, unicode)):
                                            object_label = o["labels"]

                                    stsr = SemanticTagSpecificResource(
                                                    type = "SpecificResource",
                                                    source = object_uri
                                                )
                                    sttb = SemanticTagTextualBody(
                                                    type = "TextualBody",
                                                    value = object_label
                                                )
                                    itemz = [stsr, sttb]

                                    A.body = [
                                        SemanticTagBodySet(
                                            type    = "Composite",
                                            items   = itemz,
                                            purpose = "tagging"
                                        )
                                    ]

                                    A.save()

                                    db_id = SetAnnotationMotivation( A.id, "tagging" )

                                    print "MakeAnnotationSemanticTag function, made annotation semantic tag: ", str(db_id)
                                    stdlogger.info("MakeAnnotationSemanticTag function, made annotation semantic tag: " + str(db_id))
                                    return db_id

                                else:
                                    print "MakeAnnotationSemanticTag function, dictionary field at key 'uris' does not resolve in a valid string."
                                    stdlogger.error("MakeAnnotationSemanticTag function, dictionary field at key 'uris' does not resolve in a valid string.")
                                    return False
                            else:
                                print "MakeAnnotationSemanticTag function, dictionary does not contain a field with key 'uris'."
                                stdlogger.error("MakeAnnotationSemanticTag function, dictionary does not contain a field with key 'uris'.")
                                return False
                        else:
                            print "MakeAnnotationSemanticTag function, provided json does not load as a python dictionary."
                            stdlogger.error("MakeAnnotationSemanticTag function, provided json does not load as a python dictionary.")
                            return False
                    else:
                        print "MakeAnnotationSemanticTag function, provided json object is neither string nor unicode."
                        stdlogger.error("MakeAnnotationSemanticTag function, provided json object is neither string nor unicode.")
                        return False
                else:
                    print "MakeAnnotationSemanticTag function, no annotation wit id: ", str(db_id)
                    stdlogger.error("MakeAnnotationSemanticTag function, no annotation wit id: " + str(db_id))
                    return False
            else:
                print "MakeAnnotationSemanticTag function, 'db_id' parameter neither str nor unicode."
                stdlogger.error("MakeAnnotationSemanticTag function, 'db_id' parameter neither str nor unicode.")
                return False
        else:
            print "MakeAnnotationSemanticTag function, missing parameter called 'db_id'."
            stdlogger.error("MakeAnnotationSemanticTag function, missing parameter called 'db_id'.")
            return False

    except ValueError:
        print "MakeAnnotationSemanticTag function did not complete."
        stdlogger.error("MakeAnnotationSemanticTag function did not complete.")
        return False

    print "MakeAnnotationSemanticTag function did not complete succesfully."
    stdlogger.error("MakeAnnotationSemanticTag function did not complete succesfully.")
    return False


def MakeAnnotationFreeText( db_id=None, text=None ):
    """
      Function: MakeAnnotationFreeText
      --------------------------------
        Makes an existing annotation document free-text comment.

        params:
            db_id (str): database id of the annotation to create.
            text (str): Free text introduced by the user.

        returns:
            db_id (str): database id of the modified annotation if successful, False otherwise.
    """
    try:

        if db_id:

            if isinstance(db_id, (str, unicode)):

                A = None
                A = Annotation.objects.get(id=db_id)

                if A:

                    if isinstance(text, (str, unicode)) and len(text) > 0:

                        A.body = [TextualBody(type=["TextualBody"], value=text)]

                        A.save()

                        print "MakeAnnotationFreeText function, made free-text annotation: ", str(db_id)
                        stdlogger.info("MakeAnnotationFreeText function, made free-text annotation: " + str(db_id))
                        return db_id

                    else:
                        print "MakeAnnotationFreeText function, wrong text codification or empty text"
                        stdlogger.error("MakeAnnotationFreeText function, wrong text codification or empty text")
                        return False
                else:
                    print "MakeAnnotationFreeText function, no annotation wit id: ", str(db_id)
                    stdlogger.error("MakeAnnotationFreeText function, no annotation wit id: " + str(db_id))
                    return False
            else:
                print "MakeAnnotationFreeText function, 'db_id' parameter neither str nor unicode."
                stdlogger.error("MakeAnnotationFreeText function, 'db_id' parameter neither str nor unicode.")
                return False
        else:
            print "MakeAnnotationFreeText function, missing parameter called 'db_id'."
            stdlogger.error("MakeAnnotationFreeText function, missing parameter called 'db_id'.")
            return False

    except ValueError:
        print "MakeAnnotationFreeText function did not complete."
        stdlogger.error("MakeAnnotationFreeText function did not complete.")
        return False

    print "MakeAnnotationFreeText function did not complete succesfully."
    stdlogger.error("MakeAnnotationFreeText function did not complete succesfully.")
    return False


def CreateAnnotation(target=None):
    """
      Function: CreateAnnotation
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            target (str): URL of the annotation to create.
        
        returns:
            id (str): database id of the created annotation document.
    """
    try:

        if target:

            if isinstance(target, (str, unicode)) and len(target)>0:

                gen_agt = Agent(
                    type        = ["Software"],
                    name        = ["B2Note v1.0"],
                    #name       = ["B2Note semantic annotator"],
                    #nickname   = "B2Note v1.0",
                    #email      = ["abremaud@esciencefactory.com"],
                    homepage   = ["https://b2note.bsc.es"],
                    )

                ann = Annotation(
                    jsonld_context  = [global_settings.JSONLD_CONTEXT_URL],
                    type            = ["Annotation"],
                    target          = [ExternalResource( jsonld_id = target )],
                    generator       = [ gen_agt ]
                    )
                ann.save()

                ann = Annotation.objects.get(id=ann.id)
                ann.jsonld_id = global_settings.ROOT_ANNOTATION_ID + ann.id
                ann.save()

                print "CreateAnnotation function, created annotation document with id: " + str(ann.id)
                stdlogger.info("CreateAnnotation function, created annotation document with id: " + str(ann.id))
                return ann.id

            else:
                print "CreateAnnotation function, provided 'target' argument not a valid str or unicode."
                stdlogger.error("CreateAnnotation function, provided 'target' argument not a valid str or unicode.")
                return False

        else:
            print "CreateAnnotation function, missing 'target' argument."
            stdlogger.error("CreateAnnotation function, missing 'target' argument.")
            return False
    
    except ValueError:
        print "CreateAnnotation function, did not complete."
        stdlogger.error("CreateAnnotation function, did not complete.")
        return False

    print "CreateAnnotation function did not complete succesfully."
    stdlogger.error("CreateAnnotation function did not complete succesfully.")
    return False


def orderedJSONLDfields(o_in):
    out = None
    try:
        if o_in:
            out = o_in
            if isinstance(o_in, list):
                out = []
                for item in o_in:
                    out.append(orderedJSONLDfields(item))
            if isinstance(o_in, dict):
                out = collections.OrderedDict()
                for k in ["@context", "id", "type", "target", "body", "value", "motivation", "purpose", "creator", "generator"]:
                    if k in o_in.keys():
                        out[k] = orderedJSONLDfields(o_in[k])
                for k in o_in.keys():
                    if k not in out.keys():
                        out[k] = orderedJSONLDfields(o_in[k])
    except:
        out = None
        print "orderedJSONLDfields function, Exception."
        pass

    return out


def ridOflistsOfOneItem(o_in):
    out = None
    try:
        if o_in:
            out = o_in
            if isinstance(o_in, list) or isinstance(o_in, tuple):
                if len(o_in) == 1:
                    out = ridOflistsOfOneItem( o_in[0] )
                else:
                    out = []
                    for item in o_in:
                        out.append( ridOflistsOfOneItem( item ) )
            if isinstance(o_in, dict):
                out = {}
                for k in o_in.keys():
                    out[k] = ridOflistsOfOneItem( o_in[k] )
    except:
        out = None
        print "ridOflistsOfOneItem function, Exception."
        pass
    return out



def readyQuerySetValuesForDumpAsJSONLD( o_in ):
    """
      Function: readyQuerySetValuesForDumpAsJSONLD
      --------------------------------------------
        Recursively drops embedded custom model class objects and model
         class field names beginning with "jsonld_whatever" to "@whatever",
         while avoiding returning fields with no content and making
         datetimes to xsd:datetime strings.
        input:
            o_in (object): In nesting order, Django queryset values
                list then tuple or list or set or dict or datetime or
                out-of-scope object.
        output:
            o_out: None (execution failed) or list of native python
                objects, where each out-of-scope object was replaced
                by its "string-ified" avatar, designed for subsequent
                JSON-ification.
    """

    o_out = None

    try:
        if type(o_in) is tuple:
            o_out = ()
            if len(o_in) == 1 and readyQuerySetValuesForDumpAsJSONLD( o_in[0] ):
                o_out = readyQuerySetValuesForDumpAsJSONLD( o_in[0] )
            else:
                for item in o_in:
                    if item and readyQuerySetValuesForDumpAsJSONLD( item ):
                        o_out += ( readyQuerySetValuesForDumpAsJSONLD( item ), )
        elif type(o_in) is list or type(o_in) is set:
            o_out = []
            if len(o_in) == 1 and readyQuerySetValuesForDumpAsJSONLD( o_in[0] ):
                o_out = readyQuerySetValuesForDumpAsJSONLD( o_in[0] )
            else:
                for item in o_in:
                    if item and readyQuerySetValuesForDumpAsJSONLD( item ):
                        o_out.append( readyQuerySetValuesForDumpAsJSONLD( item ) )
        elif type(o_in) is dict:
            o_out = {}
            for k in o_in.keys():
                if o_in[k] and readyQuerySetValuesForDumpAsJSONLD( o_in[k] ) and k != "id":
                    newkey = k
                    m = re.match(r'^jsonld_(.*)', k)
                    if m:
                        newkey = "@{0}".format(m.group(1))
                    if newkey=="@id": newkey="id"
                    #if newkey!="@context":
                    o_out[newkey] = readyQuerySetValuesForDumpAsJSONLD( o_in[k] )
        elif isinstance(o_in, datetime.datetime) or isinstance(o_in, datetime.datetime):
            o_out = o_in.isoformat()
        elif o_in and o_in != "None" and not re.match(r'^<class (.*)>', o_in):
            o_out = str(o_in)

    except:
        o_out = None
        pass

    return o_out



def CheckDuplicateAnnotation( target=None, annotation_body=None ):
    """
      Function: CheckDuplicateAnnotation
      --------------------------------------------
        Will be used to send feedback message to user in case they attempt to
        create an annotation with a body that is a duplicate of a previously
        existing annotation for the same target file.
        input:
            target (str): URL of the annotation to check.
            annotation_body (dict): intended (new) annotation body.
        output:
            boolean: True/False
    """
    try:    
        if target:
            if isinstance(target, (str, unicode)):
                if 'body' in annotation_body:
                    A = None
                    if 'jsonld_id' in annotation_body['body'] and isinstance(annotation_body['body']['jsonld_id'], (str, unicode)) and len(annotation_body['body']['jsonld_id']) > 0:
                        A = Annotation.objects.raw_query({'target.jsonld_id':target,'body.items.source':annotation_body['body']['jsonld_id']})
                    else:
                        if 'value' in annotation_body['body']:
                            A = Annotation.objects.raw_query({'target.jsonld_id':target,'body.value':annotation_body['body']['value']})
                        else:
                            print "CheckDuplicateAnnotation function, provided 'annotation_body' argument not a valid dictionary."
                            stdlogger.error("CheckDuplicateAnnotation function, provided 'annotation_body' argument not a valid dictionary.")
                            return False
                    if len(A) > 0:
                        return A
                    else:
                        return False
                else:
                    print "CheckDuplicateAnnotation function, provided 'annotation_body' argument not a valid dictionary."
                    stdlogger.error("CheckDuplicateAnnotation function, provided 'annotation_body' argument not a valid dictionary.")
                    return False
            else:
                print "CheckDuplicateAnnotation function, provided 'target' argument not a valid str or unicode."
                stdlogger.error("CheckDuplicateAnnotation function, provided 'target' argument not a valid str or unicode.")
                return False
        else:
            print "CheckDuplicateAnnotation function, missing 'target' argument."
            stdlogger.error("CheckDuplicateAnnotation function, missing 'target' argument.")
            return False
    
    except ValueError:
        print "CheckDuplicateAnnotation function, did not complete."
        stdlogger.error("CheckDuplicateAnnotation function, did not complete.")
        return False


def CheckLengthFreeText( body_value=None, length_limit=60 ):
    """
      Function: CheckLengthFreeText
      --------------------------------------------
        Will be used to send feedback message to the user in case they attempt to create
        a free-text tag annotation with a long body value, to check whether their intent
        is "tagging" or "commenting" (resulting in 2 different types of annotations:
        "free-text tag" or "(free-text) comment").
        input:
            body_value (str): intended (new) annotation body value.
            length_limit (int): tag string length check limit
        output:
            boolean: True/False
    """
    try:
        if body_value:
            if isinstance(body_value, (str, unicode)):
                if len(body_value) <= length_limit:
                    return True
                else:
                    return False
            else:
                print "CheckLengthFreeText function, provided 'body_value' argument not a valid str or unicode."
                stdlogger.error("CheckLengthFreeText function, provided 'body_value' argument not a valid str or unicode.")
                return False
        else:
            print "CheckLengthFreeText function, missing parameter called 'body_value'."
            stdlogger.error("CheckLengthFreeText function, missing parameter called 'body_value'.")
            return False
    
    except ValueError:
        print "CheckLengthFreeText function, did not complete."
        stdlogger.error("CheckLengthFreeText function, did not complete.")
        return False
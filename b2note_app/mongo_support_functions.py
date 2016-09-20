import os, re, datetime
import json, bson

from .models import *
from accounts.models import AnnotatorProfile

from django.forms.models import model_to_dict



def RetrieveAnnotations_perUsername( nickname=None ):
    """
      Function: RetrieveAnnotations_perUsername
      ----------------------------
        Retrieves all annotations having creator.nickname for a given file.

        params:
            subject_url (str): ID of the file.

        returns:
            dic: Dictionary with the values of the annotations.
    """
    try:

        if nickname and isinstance(nickname, (str, unicode)):

            annotations = Annotation.objects.raw_query({'creator.nickname': nickname})

            annotations = sorted(annotations, key=lambda Annotation: Annotation.created, reverse=True)

            print "RetrieveAnnotations_perUsername function, returning annotations."
            return annotations

        else:

            print "RetrieveAnnotations_perUsername function, provided nickname not valid:", nickname
            return False

    except Annotation.DoesNotExist:
        "RetrieveAnnotations_perUsername function did not complete."
        return False

    print "RetrieveAnnotations_perUsername function did not complete succesfully."
    return False


def RetrieveAnnotations( subject_url ):
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

    annotations = sorted(annotations, key=lambda Annotation: Annotation.created, reverse=True)
    
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
    except ValueError:
        pass

    if del_flag:
        print "Removed an Annotation from DB"
        return True

    print "Could not remove from DB"
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
            Annotation mongodb document id as unicode if succesful, False otherwise.
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
                            type = ['Human agent'],
                            nickname = str(ap.nickname)
                        )]
                        annotation.save()

                        print "User with nickname", str(ap.nickname) ,", set as annotation", annotation.id ,"creator"
                        return annotation.id

                    else:
                        print "SetUserAsAnnotationCreator function, no annotation were found matching this id:", str(db_id)

                else:
                    print "SetUserAsAnnotationCreator function, provided parameter for annotation id invalid."

            else:
                print "SetUserAsAnnotationCreator function, no registered annotator profile with id:", user_id

        else:
            print "SetCurrentUserAsAnnotationCreator function, provided parameter for annotator profile id invalid."

    except Exception:
        print "SetUserAsAnnotationCreator function did not complete."
        return False

    print "SetUserAsAnnotationCreator function did not complete succesfully."
    return False


def CreateSemanticTag( subject_url, object_json ):
    """
      Function: CreateSemanticTag
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            subject_url (str): URL of the annotation to create.
            object_json (str): JSON of the annotation provided by SOLR
        
        returns:
            bool: True if successful, False otherwise.
    """
    
    try:
        if subject_url and isinstance(subject_url, (str, unicode)):
            my_id = None
            my_id = CreateAnnotation(subject_url)
    
            if my_id:
                if object_json and isinstance(object_json, (str, unicode)):
                    o = None
                    o = json.loads(object_json)

                    if o and isinstance(o, dict):
                        if "uris" in o.keys():
                            if o["uris"] and isinstance(o["uris"], (str, unicode)):
                                object_uri   = ""
                                object_label = ""
                                object_uri = o["uris"]

                                if "labels" in o.keys():
                                    if o["labels"] and isinstance(o["labels"], (str, unicode)):
                                        object_label = o["labels"]

                                #print object_label, " ", object_uri

                                annotation = None
                                annotation = Annotation.objects.get(id=my_id)
                                if annotation:
                                    annotation.body = [TextualBody( jsonld_id = object_uri, type = ["TextualBody"], value = object_label )]
                                    annotation.save()
                                    print "Created semantic tag annotation"
                                    return annotation.id
                                else:
                                    print "Could not retrieve from DB the annotation-basis with below id:"
                                    print my_id
                                    return False
                            else:
                                print "Dictionary field at key 'uris' does not resolve in a valid string."
                                return False
                        else:
                            print "Dictionary does not contain a field with key 'uris'."
                            return False
                    else:
                        print "Provided json does not load as a python dictionary."
                        return False
                else:
                    print "Provided json object is neither string nor unicode."
                    return False
            else:
                print "Internal call to CreateAnnotation function did not return an exploitable id reference."
                return False
        else:
            print "Provided parameter is not a valid string for subject_url."
            return False

    except ValueError:
        print "CreateSemanticTag function did not complete."
        return False

    print "CreateSemanticTag function did not complete succesfully."
    return False




def CreateFreeText( subject_url, text ):
    """
      Function: CreateFreeText
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            subject_url (str): URL of the annotation to create.
            text (str): Free text introduced by the user
        
        returns:
            bool: id of the document created, False otherwise.
    """
    
    try:
        my_id = CreateAnnotation(subject_url)
    
        if not my_id:
            print "Could not save free text to DB"
            return False
    
        if isinstance(text, (str, unicode)) and len(text)>0: 
            annotation = Annotation.objects.get(id=my_id)
            annotation.body = [TextualBody( type = ["TextualBody"], value = text )]
            annotation.save()
            print "Created free text annotation"
            return annotation.id
        else:
            print "Wrong text codification or empty text"
            return False

    except ValueError:
        print "CreateFreeText function did not complete."
        return False

    print "CreateFreeText function did not complete succesfully."
    return False


def CreateAnnotation(target):
    """
      Function: CreateAnnotation
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            target (str): URL of the annotation to create.
        
        returns:
            int: id of the document created.
    """
    try:
        if target and isinstance(target, (str, unicode)) and len(target)>0:
            ann = Annotation(
                jsonld_context  = ["http://www.w3.org/ns/anno.jsonld"],
                type         = ["Annotation"],
                target       = [ExternalResource( jsonld_id = target )]
                )
            ann.save()
            ann = Annotation.objects.get(id=ann.id)
            ann.jsonld_id = "https://b2note.bsc.es/annotations/" + ann.id
            ann.save()
            print "CreateAnnotation with id: " + str(ann.id)
            return ann.id
        else:
            print "Bad target for CreateAnnotation"
            return False
    
    except ValueError:
        print "Could not save to DB"
        return False
        

def CreateFromPOSTinfo( subject_url, object_json ):
    """
      Function: CreateFromPOSTinfo
      ----------------------------
        Creates an annotation in MongoDB.
        
        params:
            subject_url (str): URL of the annotation to create.
            object_json (str): JSON of the annotation provided by SOLR
        
        returns:
            bool: True if successful, False otherwise.
    """
    object_uri   = ""
    object_label = ""

    try:

        if subject_url and isinstance(subject_url, (str, unicode)) and len(subject_url)>0:

            o = json.loads(object_json)

            if "uris" in o.keys():
                object_uri = o["uris"]
                if "labels" in o.keys(): object_label = o["labels"]

                print object_label, " ", object_uri

                # creator = Agent(
                #     jsonld_id 	= "http://example.com/user1",
                #     jsonld_type	= ["Person"],
                #     name		= "Default Anonymous",
                #     nick	    = "default_anonymous",
                #     email		= ["danonymous@example.com"],
                #     homepage	= ["http://example.com/DAnonymous_homepage"],
                # )
                #
                # generator = Agent(
                #     jsonld_id 	= "http://example.com/agent1",
                #     jsonld_type	= ["Software"],
                #     name		= "B2Note semantic annotator prototype",
                #     nick	    = "B2Note v0.5",
                #     email		= ["abremaud@esciencedatalab.com"],
                #     homepage	= ["https://b2note.bsc.es/devel"],
                # )
                #
                # source = ExternalResource(
                #     jsonld_id   = subject_url,
                #     jsonld_type = ["Text"],
                # )
                #
                # ann = Annotation(
                #     jsonld_id   = "https://b2note.bsc.es/annotation/temporary_id",
                #     jsonld_type = ["Annotation"],
                #     body        = [TextualBody( jsonld_id = object_uri, jsonld_type = ["TextualBody"], text = object_label, language = ["en"], role = "tagging", creator = [creator] )],
                #     target      = [ExternalResource( jsonld_id = subject_url, language = ["en"], creator = [creator] )],
                #     #target      = [SpecificResource( jsonld_type = "oa:SpecificResource", source = source )],
                #     creator     = [creator],
                #     generator   = [generator],
                #     motivation  = ["tagging"],
                # ).save()

                ann = Annotation(
                    jsonld_context  = ["http://www.w3.org/ns/anno.jsonld"],
                    jsonld_id       = "https://b2note.bsc.es/annotation/temporary_id",
                    type            = ["Annotation"],
                    target          = [ExternalResource( jsonld_id = subject_url )]
                ).save()

                anns = Annotation.objects.filter( jsonld_id = "https://b2note.bsc.es/annotation/temporary_id" )

                for ann in anns:
                    ann.jsonld_id = "https://b2note.bsc.es/annotation/" + ann.id
                    ann.save()
                    #ann.update( jsonld_id = "https://b2note.bsc.es/annotation/" + ann.id )


    except ValueError:

        print "Could not save to DB"
        return False

    print "Created an Annotation"
    return True


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
        if type(o_in) is str or type(o_in) is unicode:
            o_out = str(o_in)
        elif type(o_in) is list or type(o_in) is set:
            o_out = []
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
                    if newkey == "@id": newkey = "id"
                    o_out[newkey] = readyQuerySetValuesForDumpAsJSONLD( o_in[k] )
        elif not re.match(r'^<class (.*)>', str(o_in)):
            o_out = readyQuerySetValuesForDumpAsJSONLD( model_to_dict(o_in) )
    except:
        o_out = None
        pass
    return o_out

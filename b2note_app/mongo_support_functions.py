import os, re, datetime, copy
import json, bson

from .models import *
from accounts.models import AnnotatorProfile

from django.forms.models import model_to_dict



def SearchAnnotation( kw ):

    try:

        if kw:

            if isinstance( kw, (str, unicode)):

                A = Annotation.objects.raw_query({'body.value': kw})

                print "SearchAnnotation function, returning annotations with body value:", kw
                return A

            else:
                print "SearchAnnotation function, provided keyword argument neither str nor unicode."
                return False
        else:
            print "SearchAnnotation function, missing 'kw' string argument."
            return False
    except:
        print "SearchAnnotation function did not complete."
        return False

    print "SearchAnnotation function did not complete succesfully."
    return False




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

            #annotations = sorted(annotations, key=lambda Annotation: Annotation.created, reverse=True)

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

                                print 'SetAnnotationMotivation function, "' + motiv + '" set as motivation of annotation:', str(db_id)
                                return A.id

                            else:
                                print "SetAnnotationMotivation function, provided string parameter not part of predefined set of motivations."
                                return False
                        else:
                            print "SetAnnotationMotivation function, parameter provided for motivation neither string nor unicode."
                            return False
                    else:
                        print "SetAnnotationMotivation function, missing motivation parameter."
                        return False
                else:
                    print "SetAnnotationMotivation function, no annotation wit id:", str(db_id)
                    return False
            else:
                print "SetAnnotationMotivation function, 'db_id' parameter neither str nor unicode."
                return False
        else:
            print "SetAnnotationMotivation function, missing parameter called 'db_id'."
            return False

    except ValueError:
        print "SetAnnotationMotivation function did not complete."
        return False

    print "SetAnnotationMotivation function did not complete succesfully."
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


def DuplicateAnnotation( db_id=None ):
    """
      Function: DulicateAnnotation
      ----------------------------
        Duplicates an annotation in MongoDB.

        params:
            db_id (str): database id of the annotation document to duplicate.

        returns:
            id (str): database id of the created annotation document.
    """
    try:

        if db_id:

            if isinstance(db_id, (str, unicode)):

                A = None
                A = Annotation.objects.get(id=db_id)

                if A:

                    if A.target:

                        if isinstance(A.target, list):

                            if len(A.target)>0:

                                if A.target[0]:

                                    if A.target[0].jsonld_id:

                                        if isinstance(A.target[0].jsonld_id, (str, unicode)):

                                            B = CreateAnnotation( A.target[0].jsonld_id )
                                            B = Annotation.objects.get( id = B )

                                            ann = copy.deepcopy( A )

                                            B_dict = {k: v for k, v in B.__dict__.iteritems() if v is not None}
                                            ann.__dict__.update(B_dict)

                                            ann.save()

                                            print "DuplicateAnnotation function, created annotation document with id: " + str(ann.id)
                                            return ann.id

                                        else:
                                            print "DuplicateAnnotation function, annotation document target 'jsonld_id' neither str nor unicode."
                                            return False
                                    else:
                                        print "DuplicateAnnotation function, missing annotation document target 'jsonld_id'."
                                        return False
                                else:
                                    print "DuplicateAnnotation function, no element in annotation document target list."
                                    return False
                            else:
                                print "DuplicateAnnotation function, annotation doument target list empty."
                                return False
                        else:
                            print "DuplicateAnnotation function, annotation doument target is not of type list."
                            return False
                    else:
                        print "DuplicateAnnotation function, annotation document missing target field."
                        return False
            else:
                print "DuplicateAnnotation function, provided 'db_id' argument neither str nor unicode."
                return False

        else:
            print "DuplicateAnnotation function, missing 'db_id' argument."
            return False

    except ValueError:
        print "DuplicateAnnotation function, did not complete."
        return False

    print "DuplicateAnnotation function did not complete succesfully."
    return False


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

                    #db_id = SetAnnotationMotivation( db_id, "tagging" )

                    print "MakeAnnotationSemanticTag function, made annotation semantic tag:", str(db_id)
                    return db_id

                else:
                    print "CreateSemanticTag function, provided json object is neither string nor unicode."
                    return False
            else:
                print "CreateSemanticTag function, internal call to CreateAnnotation function did not return an exploitable id reference."
                return False
        else:
            print "CreateSemanticTag function, provided parameter is not a valid string for subject_url."
            return False

    except ValueError:
        print "CreateSemanticTag function did not complete."
        return False

    print "CreateSemanticTag function did not complete succesfully."
    return False


def CreateFreeText( subject_url=None, text=None ):
    """
      Function: CreateFreeText
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

                    #db_id = SetAnnotationMotivation( db_id, "commenting" )

                    print "CreateFreeText function, created free-text annotation:", str(db_id)
                    return db_id

                else:
                    print "CreateFreeText function, wrong text codification or empty text."
                    return False
            else:
                print "CreateFreeText function, 'my_id' parameter neither str nor unicode."
                return False
        else:
            print "CreateFreeText function, annotation not created or id not returned."
            return False

    except ValueError:
        print "CreateFreeText function did not complete."
        return False

    print "CreateFreeText function did not complete succesfully."
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

                                    A.body = [
                                        TextualBody(
                                            jsonld_id = object_uri,
                                            type      = ["TextualBody"],
                                            value     = object_label
                                        )
                                    ]

                                    A.save()

                                    #db_id = SetAnnotationMotivation( A.id, "tagging" )

                                    print "MakeAnnotationSemanticTag function, made annotation semantic tag:", str(db_id)
                                    return db_id

                                else:
                                    print "MakeAnnotationSemanticTag function, dictionary field at key 'uris' does not resolve in a valid string."
                                    return False
                            else:
                                print "MakeAnnotationSemanticTag function, dictionary does not contain a field with key 'uris'."
                                return False
                        else:
                            print "MakeAnnotationSemanticTag function, provided json does not load as a python dictionary."
                            return False
                    else:
                        print "MakeAnnotationSemanticTag function, provided json object is neither string nor unicode."
                        return False
                else:
                    print "MakeAnnotationSemanticTag function, no annotation wit id:", str(db_id)
                    return False
            else:
                print "MakeAnnotationSemanticTag function, 'db_id' parameter neither str nor unicode."
                return False
        else:
            print "MakeAnnotationSemanticTag function, missing parameter called 'db_id'."
            return False

    except ValueError:
        print "MakeAnnotationSemanticTag function did not complete."
        return False

    print "MakeAnnotationSemanticTag function did not complete succesfully."
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

                        #db_id = SetAnnotationMotivation( A.id, "commenting" )

                        print "MakeAnnotationFreeText function, made free-text annotation:", str(db_id)
                        return db_id

                    else:
                        print "MakeAnnotationFreeText function, wrong text codification or empty text"
                        return False
                else:
                    print "MakeAnnotationFreeText function, no annotation wit id:", str(db_id)
                    return False
            else:
                print "MakeAnnotationFreeText function, 'db_id' parameter neither str nor unicode."
                return False
        else:
            print "MakeAnnotationFreeText function, missing parameter called 'db_id'."
            return False

    except ValueError:
        print "MakeAnnotationFreeText function did not complete."
        return False

    print "MakeAnnotationFreeText function did not complete succesfully."
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
                     type       = ["Software"],
                     name       = ["B2Note semantic annotator"],
                     nickname   = "B2Note v1.0",
                     email      = ["abremaud@esciencefactory.com"],
                     homepage   = ["https://b2note.bsc.es"],
                    )

                ann = Annotation(
                    jsonld_context  = ["http://www.w3.org/ns/anno.jsonld"],
                    type            = ["Annotation"],
                    target          = [ExternalResource( jsonld_id = target )],
                    generator       = [ gen_agt ]
                    )
                ann.save()

                ann = Annotation.objects.get(id=ann.id)
                ann.jsonld_id = "https://b2note.bsc.es/annotations/" + ann.id
                ann.save()

                print "CreateAnnotation function, created annotation document with id: " + str(ann.id)
                return ann.id

            else:
                print "CreateAnnotation function, provided 'target' argument not a valid str or unicode."
                return False

        else:
            print "CreateAnnotation function, missing 'target' argument."
            return False
    
    except ValueError:
        print "CreateAnnotation function, did not complete."
        return False

    print "CreateAnnotation function did not complete succesfully."
    return False


def readyQuerySetValuesForDumpAsJSONLD2( o_in ):
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
    print "#", o_out
    return o_out


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
            for item in o_in:
                if item and readyQuerySetValuesForDumpAsJSONLD( item ):
                    o_out += ( readyQuerySetValuesForDumpAsJSONLD( item ), )
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
                    if newkey=="@id": newkey="id"
                    o_out[newkey] = readyQuerySetValuesForDumpAsJSONLD( o_in[k] )
        elif isinstance(o_in, datetime.datetime) or isinstance(o_in, datetime.datetime):
            o_out = o_in.isoformat()
        elif o_in and o_in != "None" and not re.match(r'^<class (.*)>', o_in):
            o_out = str(o_in)
        #if len(o_out) <= 0: o_out = None
    except:
        o_out = None
        pass

    return o_out
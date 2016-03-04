import re, datetime
import json, bson

from .models import *

import os, datetime, json


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
        if db_id and type(db_id) is unicode and len(db_id)>0:
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

        if subject_url and type(subject_url) is unicode and len(subject_url)>0:

            o = json.loads(object_json)

            if "uris" in o.keys():
                object_uri = o["uris"][0]
                if "labels" in o.keys(): object_label = o["labels"]

                print object_label, " ", object_uri

                creator = Agent(
                    jsonld_id 	= "http://example.com/user1",
                    jsonld_type	= ["Person"],
                    name		= "Default Anonymous",
                    nick	    = "default_anonymous",
                    email		= ["danonymous@example.com"],
                    homepage	= ["http://example.com/DAnonymous_homepage"],
                )

                generator = Agent(
                    jsonld_id 	= "http://example.com/agent1",
                    jsonld_type	= ["Software"],
                    name		= "B2Note semantic annotator prototype",
                    nick	    = "B2Note v0.5",
                    email		= ["abremaud@esciencedatalab.com"],
                    homepage	= ["https://b2note.bsc.es/devel"],
                )

                source = ExternalResource(
                    jsonld_id   = subject_url,
                    jsonld_type = ["Text"],
                )

                ann = Annotation(
                    jsonld_id   = "https://b2note.bsc.es/annotation/temporary_id",
                    jsonld_type = ["Annotation"],
                    body        = [TextualBody( jsonld_id = object_uri, jsonld_type = ["TextualBody"], text = object_label, language = ["en"], role = "tagging", creator = [creator] )],
                    target      = [ExternalResource( jsonld_id = subject_url, language = ["en"], creator = [creator] )],
                    #target      = [SpecificResource( jsonld_type = "oa:SpecificResource", source = source )],
                    creator     = [creator],
                    generator   = [generator],
                    motivation  = ["tagging"],
                ).save()

                anns = Annotation.objects.filter( jsonld_id = "https://b2note.bsc.es/annotation/temporary_id" )

                for ann in anns:
                    ann.jsonld_id = "https://b2note.bsc.es/annotation/" + ann.id
                    ann.save()
                    #ann.update( jsonld_id = "https://b2note.bsc.es/annotation/" + ann.id )

                # ann = Annotation(\
                #         triple=Triple(\
                #                 subject=TripleElement(iri=subject_url,label="", definition="",curation_status="", ontology_iri="",ontology_shortname="",ontology_version="",),\
                #                 predicate=TripleElement(iri="http://purl.obolibrary.org/obo/IAO_0000136",label="is about",definition="Is_about is a (currently) primitive relation that relates an information artifact to an entity.",curation_status="pending final vetting",ontology_iri="http://purl.obolibrary.org/obo/iao.owl",ontology_shortname="IAO",ontology_version="2015,02,23",),\
                #                 object=TripleElement(\
                #                         iri     =   object_uri,\
                #                         label   =   object_label,\
                #                         definition = "",\
                #                         curation_status = "",\
                #                         ontology_iri = "",\
                #                         ontology_shortname= "",\
                #                         ontology_version= "",\
                #                 ),\
                #         ),\
                #         provenance=Provenance(\
                #                 createdBy="abremaud@esciencefactory.com",
                #         ),\
                # ).save()

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

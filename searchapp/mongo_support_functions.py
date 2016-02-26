import json, bson



from .models import *


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
                    jsonld_type	= ["foaf:Person"],
                    name		= "Ludwig Combi Van",
                    account	    = "Ludo99",
                    email		= ["lcombivan@esciencedatalab.com"],
                    homepage	= ["http://example.com/LudwigCombiVan_homepage"],
                )

                generator = Agent(
                    jsonld_id 	= "http://example.com/agent1",
                    jsonld_type	= ["prov:SoftwareAgent"],
                    name		= "B2Note annotator",
                    account	    = "B2Note v1.0",
                    email		= ["abremaud@esciencedatalab.com"],
                    homepage	= ["https://b2note.bsc.es/devel"],
                )

                source = ExternalResource(
                    jsonld_id   = subject_url,
                    jsonld_type = ["dctypes:Text"],
                )

                ann = Annotation(
                    jsonld_id   = ["https://b2note.bsc.es/annotation/temporary_id"],
                    jsonld_type = ["oa:Annotation"],
                    body        = [TextualBody( jsonld_id = object_uri, jsonld_type = ["oa:TextualBody"], text = object_label, language = ["en"], role = "oa:tagging" )],
                    target      = [ExternalResource( jsonld_id = subject_url, language = ["en"], creator = [creator] )],
                    #target      = [SpecificResource( jsonld_type = "oa:SpecificResource", source = source )],
                    creator     = [creator],
                    generator   = [generator],
                    motivation  = ["oa:tagging"],
                ).save()

                anns = Annotation.objects.filter( jsonld_id = ["https://b2note.bsc.es/annotation/temporary_id"] )

                for ann in anns:
                    ann.jsonld_id = ["https://b2note.bsc.es/annotation/" + ann.id]
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

#http://stackoverflow.com/questions/23285558/datetime-date2014-4-25-is-not-json-serializable-in-django
def date_handler(obj):
    """
      Function: date_handler
      ----------------------------
        Converts a JSON serialized date to iso format.
        
        params:
            obj (object): Date JSON coded.
        
        returns:
            object: the date in iso format.
    """
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

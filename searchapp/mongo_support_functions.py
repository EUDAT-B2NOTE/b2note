from pymongo import MongoClient

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

                ann = Annotation(\
                        triple=Triple(\
                                subject=TripleElement(iri=subject_url,label="", definition="",curation_status="", ontology_iri="",ontology_shortname="",ontology_version="",),\
                                predicate=TripleElement(iri="http://purl.obolibrary.org/obo/IAO_0000136",label="is about",definition="Is_about is a (currently) primitive relation that relates an information artifact to an entity.",curation_status="pending final vetting",ontology_iri="http://purl.obolibrary.org/obo/iao.owl",ontology_shortname="IAO",ontology_version="2015,02,23",),\
                                object=TripleElement(\
                                        iri     =   object_uri,\
                                        label   =   object_label,\
                                        definition = "",\
                                        curation_status = "",\
                                        ontology_iri = "",\
                                        ontology_shortname= "",\
                                        ontology_version= "",\
                                ),\
                        ),\
                        provenance=Provenance(\
                                createdBy="abremaud@esciencefactory.com",
                        ),\
                ).save()

    except ValueError:

        print "Could not save to DB"
        return False

    print "Created an Annotation"
    return True

def ExtractAllDocuments():
    """
      Function: ExtractAllDocuments
      ----------------------------
        Extracts all annotations from MongoDB to Django.
        
        params:
            none
        
        returns:
            documents (list): A list of all documents stored in the collection searchapp_annotation.
    """
    import urllib
    
    pwd = urllib.quote_plus(os.environ['MONGODB_PWD'])
    uri = "mongodb://" + os.environ['MONGODB_USR'] + ":" + pwd + "@127.0.0.1/" + os.environ['MONGODB_NAME'] + "?authMechanism=SCRAM-SHA-1"
    client = MongoClient(uri)
    db = client[os.environ['MONGODB_NAME']]
    
    collection = db["searchapp_annotation"]
    documents = []
    for doc in collection.find():
         documents.append(doc)
    
    # http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
    date_handler = lambda obj: (
                                obj.isoformat()
                                if isinstance(obj, datetime.datetime)
                                or isinstance(obj, datetime.date)
                                else str(obj)
                                )
    return json.dumps(documents, default=date_handler)


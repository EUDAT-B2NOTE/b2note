import os, re, datetime, collections
import requests
import logging

from rdflib.serializer import Serializer
from requests.auth import HTTPBasicAuth


stdlogger = logging.getLogger('b2note')


def httpPutRdfXmlFileContentToOpenVirtuoso( url=None, usr=None, pwd=None, files=None ):

    ''' HTTP PUT RDF/XML FILE CONTENT TO OPEN VIRTUOSO RDF-SINK'''
    out = None
    try:
        if url and usr and pwd and files:
            if isinstance(url, (str, unicode)) and isinstance(usr, (str, unicode)) and\
                isinstance(pwd, (str, unicode)) and isinstance(files, (str, unicode)):
                if len(url) > len('http'):
                    if url[:len('http')] == 'http':
                        headers = {'Content-Type': 'application/rdf+xml'}
                        r = requests.put(url, auth=HTTPBasicAuth(usr, pwd), headers=headers, data=files)
                        out = r
    except:
        print "httpPutRdfXmlFileContentToOpenVirtuoso function, Could not http PUT rdf/xml file content to Open Virtuoso rdf-sink."
        stdlogger.error("httpPutRdfXmlFileContentToOpenVirtuoso function, Could not http PUT rdf/xml file content to Open Virtuoso rdf-sink.")
        return False
    return out


def retrieve_annotation_jsonld_from_api():
    out = None
    paginate_over = 50

    try:
        ir = requests.get("https://b2note.bsc.es/annotations?max_results=1")
        #"_meta": {"max_results": 2, "total": 41, "page": 2}
        annL = []
        if ir and ir.json() and "_meta" in ir.json().keys():
            tt=ir.json()["_meta"]["total"]
            pp=min(tt, paginate_over)
            for pg in range(1,1+((tt+(pp-1))/pp)):
                #print tt, pp, 1+((tt+(pp-1))/pp), pg
                r = requests.get("https://b2note.bsc.es/annotations?max_results="+str(pp)+"+&page="+str(pg))
                if r and r.json():
                    if "schema:itemListElement" in r.json().keys() \
                    and isinstance(r.json()["schema:itemListElement"], list):
                        annL = annL + r.json()["schema:itemListElement"]
                    else:
                        print "retrieve_annotation_jsonld_from_api function, missing or unsuitable schema:itemListElement should be list."
                        stdlogger.error("retrieve_annotation_jsonld_from_api, missing or unsuitable schema:itemListElement should be list.")
                else:
                    print "retrieve_annotation_jsonld_from_api function, no jsonld data retrieved, page:" + str(pg) +"."
                    stdlogger.error("retrieve_annotation_jsonld_from_api, no jsonld data retrieved, page:" + str(pg) +".")

            out = annL
        else:
            print "retrieve_annotation_jsonld_from_api function, no jsonld data retrieved."
            stdlogger.error("retrieve_annotation_jsonld_from_api, no jsonld data retrieved.")
    except:
        print "retrieve_annotation_jsonld_from_api function, could not complete."
        stdlogger.error("retrieve_annotation_jsonld_from_api, could not complete.")
        return False
    return out


def addarobase_totypefieldname(o_in):
    o_out=None
    if isinstance(o_in, list):
        o_out = []
        for item in o_in:
            o_out.append(addarobase_totypefieldname(item))
    elif isinstance(o_in, dict):
        o_out={}
        for k in o_in.keys():
            if k=="type":
                o_out["@type"] = addarobase_totypefieldname( o_in[k] )
            else:
                o_out[k] = addarobase_totypefieldname( o_in[k] )
    else:
        o_out = o_in
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
        if type(o_in) is str or type(o_in) is unicode:
            o_out = str(o_in)
        elif isinstance(o_in, datetime.datetime) or isinstance(o_in, datetime.datetime):
            o_out = o_in.isoformat()
        elif type(o_in) is list or type(o_in) is set:
            o_out = []
            if len(o_in)==1 and readyQuerySetValuesForDumpAsJSONLD( o_in[0] ):
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
                    if m: newkey = "@{0}".format(m.group(1))
                    if newkey == "@id": newkey = "id"
                    o_out[newkey] = readyQuerySetValuesForDumpAsJSONLD( o_in[k] )
        else:
            print "readyQuerySetValuesForDumpAsJSONLD function, unhandled object type encountered: ", type(o_in)
            stdlogger.error("readyQuerySetValuesForDumpAsJSONLD function, unhandled object type encountered: " + type(o_in))
            pass
    except:
        o_out = None
        print "readyQuerySetValuesForDumpAsJSONLD function did not complete."
        stdlogger.error("readyQuerySetValuesForDumpAsJSONLD function did not complete.")
        pass
    return o_out



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
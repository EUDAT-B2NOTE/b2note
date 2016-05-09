#!/usr/bin/env python2.7
# encoding: utf-8

# abremaud@esciencefactory.com 20160204


from SPARQLWrapper import SPARQLWrapper, JSON
import urllib, urllib2, json


#http://stackoverflow.com/questions/17388213/python-string-similarity-with-probability
from difflib import SequenceMatcher
def stringSimilarity(a, b):

    return SequenceMatcher(None, a, b).ratio()


def get_json(url=None, apikey=None):
    out = None
    try:
        if url:
            if inputStringCheck(url):
                opener = urllib2.build_opener()
                if apikey:
                    if inputStringCheck(apikey):
                        opener.addheaders = [('Authorization', 'apikey token=' + apikey)]
                out = json.loads(opener.open(url).read())
    except:
        print "Could not perform get_json with:", url, apikey
    return out


def inputStringCheck( string, contains=None ):

    out = False

    try:

        if string:

            if isinstance(string, str):

                if len(string)>0:

                    if contains:

                        if inputStringCheck(contains):

                            if contains in string:

                                out = True

                    else:

                        out = True

    except:

        print "Could not check provided string."
        pass

    return out


def displayQueryResults( res ):

    try:

        if res:

            if type(res) is dict:

                if "head" in res.keys():

                    if type(res["head"]) is dict:

                        if "vars" in res["head"].keys():

                            # info_string = ""
                            #
                            # for item in res["head"]["vars"]:
                            #
                            #     info_string += item + "\t"
                            #
                            # if info_string != "": print info_string

                            if "results" in res.keys():

                                if type(res["results"]) is dict:

                                    if "bindings" in res["results"].keys():

                                        if type(res["results"]["bindings"]) is list:

                                            print "\n\n" + "#"*30 + "\n"

                                            for content in res["results"]["bindings"]:

                                                info_string = ""

                                                for item in res["head"]["vars"]:

                                                    if item in content.keys():

                                                        if 'value' in content[item].keys():

                                                            info_string += content[item]['value'] + "\t"

                                                if info_string != "": print info_string

                                            print "\n===>", len(res["results"]["bindings"]), "results retrieved."

                                            print "\n" + "#"*30 + "\n\n"

    except:

        print "SPARQL query on file was not successful."
        pass


def mergeQueryResults( res1, res2 ):

    out = None

    try:

        if res1 and res2:

            if type(res1) and type(res2) is dict:

                if "head" in res1.keys() and "head" in res2.keys():

                    if type(res1["head"]) and type(res2["head"]) is dict:

                        if "vars" in res1["head"].keys() and "vars" in res2["head"].keys():

                            if type(res1["head"]["vars"]) and type(res2["head"]["vars"]) is list:

                                res = res1

                                for item in res2["head"]["vars"]:

                                    if item not in res1["head"]["vars"]:

                                        res = None

                                if res:

                                    if "results" in res.keys() and "results" in res2.keys():

                                        if type(res["results"]) and type(res2["results"]) is dict:

                                            if "bindings" in res["results"].keys() and "bindings" in res2["results"].keys():

                                                if type(res["results"]["bindings"]) and type(res2["results"]["bindings"]) is list:

                                                    for content in res2["results"]["bindings"]:

                                                        res["results"]["bindings"].append( content )

                                                    out = res

    except:

        print "Could not merge query results."

    return out


def checkEndpointResponds( endpoint=None, from_uri=None, apikey=None ):

    out = False

    try:

        if endpoint:

            if inputStringCheck(endpoint):

                query = "ASK WHERE { ?s ?p ?o . }"

                if from_uri:

                    if inputStringCheck(from_uri):

                        query = query[:query.find("WHERE")] + """
                                FROM <""" + from_uri + """>
                                """ + query[query.find("WHERE"):]

                if apikey:

                    res = sparqlOneEndpoint( endpoint, query, apikey )

                else:

                    res = sparqlOneEndpoint( endpoint, query )

                if res:

                    if type(res) is dict:

                        if "boolean" in res.keys():

                            if type(res["boolean"]) is bool:

                                if res["boolean"]:

                                    out = True

    except:

        print "Could not check whether sparql endpoint responds."

    return out


def obtainPredicateCount( endpoint=None, from_uri=None, apikey=None, endpoint_type=None ):

    out = False

    try:

        if endpoint:

            if inputStringCheck(endpoint):

                res = None

                query = "SELECT (COUNT(DISTINCT ?p) AS ?np) WHERE {?s ?p ?o.}"

                if endpoint_type:

                    if isinstance(endpoint_type, (str, unicode)):

                        if endpoint_type=="endpoint_nwsw":

                            res = urllibOneEndpoint(endpoint, query, from_uri, apikey)

                if not res:

                    if from_uri: modifyQueryForSubgraph(query, from_uri)

                    if apikey:

                        res = sparqlOneEndpoint( endpoint, query, apikey )

                    else:

                        res = sparqlOneEndpoint( endpoint, query )

                if res:

                    if isinstance(res, dict):

                        if "results" in res.keys() and "bindings" in res["results"].keys():

                            if isinstance(res["results"]["bindings"], list):

                                if len(res["results"]["bindings"])>0:

                                    if isinstance(res["results"]["bindings"][0], dict):

                                        if "np" in res["results"]["bindings"][0].keys():

                                            if isinstance(res["results"]["bindings"][0]["np"], dict):

                                                if "value" in res["results"]["bindings"][0]["np"].keys():

                                                    out = int( res["results"]["bindings"][0]["np"]["value"] )

    except:

        print "Could not obtain number of different predicates in use."

    return out


def obtainClassCount( endpoint=None, from_uri=None, apikey=None ):

    out = False

    try:

        if endpoint:

            if inputStringCheck(endpoint):

                query = "SELECT DISTINCT ?s WHERE { ?s ?p ?o . }"

                if from_uri: modifyQueryForSubgraph( query, from_uri )

                res = None

                if apikey:

                    res = sparqlOneEndpoint( endpoint, query, apikey )

                else:

                    res = sparqlOneEndpoint( endpoint, query )

                if res:

                    if type(res) is dict:

                        if "results" in res.keys():

                            if type(res["results"]) is dict:

                                if "bindings" in res["results"].keys():

                                    if type(res["results"]["bindings"]) is list:

                                        out = len(res["results"]["bindings"])

    except:

        print "Could not obtain number of different classes in use."

    return out


def modifyQueryAddLimitAndOffset( query=None, limit=None, offset=None ):

    out = None

    try:

        if query:

            if type(query) is str:

                if limit:

                    if type(limit) is int:

                        query += "\nLIMIT " + str(limit)

                        if offset:

                            if type(offset) is int:

                                query += "\nOFFSET " + str(offset)

                        out = query

    except:

        print "Could not add limit and ofset to query."

    return out


def modifyQueryForSubgraph( query=None, subgraph_uri=None ):

    out = None

    try:

        if query and subgraph_uri:

            if inputStringCheck(query) and inputStringCheck(subgraph_uri):

                if "WHERE" in query:

                    out = query[:query.find("WHERE")] + "FROM <" + subgraph_uri + ">\n" + query[query.find("WHERE"):]

    except:

        print "Could not modify query by inserting subgraph URI to FROM statement."

    return out


def encodeQueryAsURL( endpoint=None, query=None, from_uri=None):

    out = None

    try:

        if endpoint and query:

            if isinstance(endpoint, (str, unicode)) and isinstance(query, (str, unicode)):

                out = endpoint + "?" + urllib.urlencode({"query": query, "format": "json"})

                if from_uri:

                    if isinstance(from_uri, (str, unicode)):

                        out = endpoint + "?" + urllib.urlencode({"default-graph-uri": from_uri, "query": query, "format": "json"})

    except:

        print "Could not encode query as url."

    return out


def urllibOneEndpoint( endpoint=None, query=None, from_uri=None, apikey=None ):

    out = None

    try:

        if endpoint and query:

            if isinstance(endpoint, (str, unicode)) and isinstance(query, (str, unicode)):

                q = encodeQueryAsURL( endpoint, query, from_uri )

                if apikey:

                    out = get_json( q, apikey )

                else:

                    out = get_json( q )

    except:

        print "Could not process get_json as sparql query."
        pass

    return out


def sparqlOneEndpoint( endpoint, query, apikey=None ):

    out = None

    try:

        sparql=SPARQLWrapper(endpoint)

        if apikey: sparql.addCustomParameter("apikey", apikey)

        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)

        sparql.setTimeout( 30 )

        #print "\n", "# " * 7, "\n", query, "\n", "# " * 7, "\n"

        out = sparql.query().convert()

    except:

        print "Could not process formulated query on indicated endpoint."
        pass

    return out
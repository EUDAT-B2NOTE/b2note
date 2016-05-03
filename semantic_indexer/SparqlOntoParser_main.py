#!/usr/bin/env python2.7
# encoding: utf-8

# abremaud@esciencefactory.com 20160204


from solr_writer import write_to_solr

from SparqlOntoParser_functions import csv2list, obtainPropertyIDs
from SparqlOntoParser_functions import sparqlGatherPropertySetvaluesFromAllClasses
from SparqlOntoParser_functions import apiGatherPropertySetValuesFromAllClasses


def sparqlontoparser_main():

    end_list = None
    voc_list = None
    propsofi = None

    try:

        end_list = csv2list( 'data/input_data/Endpoint2Voc.csv' )
        voc_list = csv2list( 'data/input_data/VocabularyLocation.csv' )
        propsofi = csv2list( 'data/input_data/PropertyHooks.csv' )

        if end_list and voc_list and propsofi:

            if isinstance(end_list, list) and isinstance(voc_list, list) and isinstance(propsofi, list):

                for end in end_list:

                    if isinstance(end, dict):

                        if "source_nick" in end.keys():

                            if isinstance(end["source_nick"], (str, unicode)):

                                if len(end["source_nick"])>0:

                                    if end["source_nick"][0] != "#":

                                        endpoint = None

                                        if "endpointORfilepath" in end.keys():

                                            if isinstance(end["endpointORfilepath"], (str, unicode)):

                                                if len(end["endpointORfilepath"])>0:

                                                    if end["endpointORfilepath"][0] != "#":

                                                        endpoint = end["endpointORfilepath"]

                                        if endpoint:

                                            source_type = None

                                            if "type" in end.keys():

                                                if isinstance(end["type"], (str, unicode)):

                                                    if len(end["type"])>0:

                                                        if end["type"][0] != "#":

                                                            source_type = end["type"]

                                            apikey = None

                                            if "apikey" in end.keys():

                                                if isinstance(end["apikey"], (str, unicode)):

                                                    if len(end["apikey"])>0:

                                                        if end["apikey"][0] != "#":

                                                            apikey = end["apikey"]

                                            if None in end.keys():

                                                v_list = None

                                                if isinstance(end[None], (str, unicode)):

                                                    if len(end[None])>0:

                                                        v_list = []
                                                        v_list.append( end[None] )

                                                elif isinstance(end[None], list):

                                                    v_list = end[None]

                                                if v_list:

                                                    for v in v_list:

                                                        if isinstance(v, (str, unicode)):

                                                            if len(v)>0:

                                                                if v[0] != "#":

                                                                    from_uri = None

                                                                    for voc in voc_list:

                                                                        if isinstance(voc, dict):

                                                                            if "vocab_acronym" in voc.keys() and "vocab_uri" in voc.keys():

                                                                                if isinstance(voc["vocab_acronym"], (str, unicode)) and isinstance(voc["vocab_uri"], (str, unicode)):

                                                                                    if len(voc["vocab_acronym"])>0 and len(voc["vocab_uri"])>0:

                                                                                        if voc["vocab_acronym"][0] != "#" and voc["vocab_uri"][0] != "#":

                                                                                            if v == voc["vocab_acronym"]:

                                                                                                from_uri = voc["vocab_uri"]

                                                                    pids = None

                                                                    print "\n\n", "# " * 15

                                                                    print "[" + source_type + "]", endpoint, "\t", from_uri, "\t", apikey

                                                                    pids = obtainPropertyIDs( propsofi, endpoint, from_uri, apikey, source_type )

                                                                    if pids:

                                                                        container = None

                                                                        if source_type and source_type == "api":
                                                                            # API based
                                                                            container = apiGatherPropertySetValuesFromAllClasses(from_uri, apikey, pids)
                                                                        else:
                                                                            # SPARQL based
                                                                            container = sparqlGatherPropertySetvaluesFromAllClasses(endpoint, pids, from_uri, apikey, source_type)

                                                                        if container:

                                                                            if isinstance(container, list):
                                                                                # num_item = min(2, len(container))
                                                                                # for item in range(num_item):
                                                                                #     print container[item]

                                                                                print "\n", len(container)

                                                                                write_to_solr(container, 'http://localhost:8983/solr/restest_032016/')

                                                                                print "\n", "# " * 15

    except:

        print "Could not proceed with sparqlontoparser_main execution."


sparqlontoparser_main()

# from SparqlOntoParser_functions import obtainPropertyIDs
#
# propsofi = csv2list('data/input_data/PropertyHooks.csv')
#
# endpoint = "http://202.45.139.84:10035/catalogs/fao/repositories/agrovoc"
# from_uri = None
# apikey   = None
#
# query = "SELECT (COUNT(DISTINCT ?oo) AS ?noo) WHERE {?s ?p ?oo.}"
#
# res = obtainPropertyIDs(propsofi, endpoint, from_uri, apikey, "endpoint")
#
# print type(res)


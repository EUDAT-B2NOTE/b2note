#!/usr/bin/env python2.7
# encoding: utf-8

# abremaud@esciencefactory.com 20160204


import os

from .solr_writer import write_to_solr

from .SparqlOntoParser_functions import csv2list, obtainPropertyIDs, reformatpidsForAPIuse
from .SparqlOntoParser_functions import sparqlGatherPropertySetvaluesFromAllClasses
from .SparqlOntoParser_functions import apiGatherPropertySetValuesFromAllClasses


def sparqlontoparser_main():

    end_list = None
    voc_list = None
    propsofi = None

    try:

        #http://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
        script_dir = os.path.dirname(__file__)

        end_list = csv2list( script_dir + '/data/input_data/Endpoint2Voc.csv' )
        voc_list = csv2list( script_dir + '/data/input_data/VocabularyLocation.csv' )
        propsofi = csv2list( script_dir + '/data/input_data/PropertyHooks.csv' )

        if end_list and voc_list and propsofi:

            if isinstance(end_list, list) and isinstance(voc_list, list) and isinstance(propsofi, list):

                for end in end_list:

                    if isinstance(end, dict):

                        if "source_nick" in list(end.keys()):

                            if isinstance(end["source_nick"], str):

                                if len(end["source_nick"])>0:

                                    if end["source_nick"][0] != "#":

                                        endpoint = None

                                        if "endpointORfilepath" in list(end.keys()):

                                            if isinstance(end["endpointORfilepath"], str):

                                                if len(end["endpointORfilepath"])>0:

                                                    if end["endpointORfilepath"][0] != "#":

                                                        endpoint = end["endpointORfilepath"]

                                        if endpoint:

                                            source_type = None

                                            if "type" in list(end.keys()):

                                                if isinstance(end["type"], str):

                                                    if len(end["type"])>0:

                                                        if end["type"][0] != "#":

                                                            source_type = end["type"]

                                            apikey = None

                                            if "apikey" in list(end.keys()):

                                                if isinstance(end["apikey"], str):

                                                    if len(end["apikey"])>0:

                                                        if end["apikey"][0] != "#":

                                                            apikey = end["apikey"]

                                            if None in list(end.keys()):

                                                v_list = None

                                                if isinstance(end[None], str):

                                                    if len(end[None])>0:

                                                        v_list = []
                                                        v_list.append( end[None] )

                                                elif isinstance(end[None], list):

                                                    v_list = end[None]

                                                if v_list:

                                                    for v in v_list:

                                                        if isinstance(v, str):

                                                            if len(v)>0:

                                                                if v[0] != "#":

                                                                    from_uri = None

                                                                    for voc in voc_list:

                                                                        if isinstance(voc, dict):

                                                                            if "vocab_acronym" in list(voc.keys()) and "vocab_uri" in list(voc.keys()):

                                                                                if isinstance(voc["vocab_acronym"], str) and isinstance(voc["vocab_uri"], str):

                                                                                    if len(voc["vocab_acronym"])>0 and len(voc["vocab_uri"])>0:

                                                                                        if voc["vocab_acronym"][0] != "#" and voc["vocab_uri"][0] != "#":

                                                                                            if v == voc["vocab_acronym"]:

                                                                                                from_uri = voc["vocab_uri"]

                                                                    pids = None

                                                                    print("\n\n", "# " * 15)

                                                                    print("[" + source_type + "]", endpoint, "\t", from_uri, "\t", apikey)

                                                                    pids = obtainPropertyIDs( propsofi, endpoint, from_uri, apikey, source_type )

                                                                    if pids:

                                                                        container = None

                                                                        if source_type and source_type == "api":
                                                                            # API based
                                                                            pids_swk_wmeta  = reformatpidsForAPIuse(pids, propsofi)

                                                                            container = apiGatherPropertySetValuesFromAllClasses(from_uri, apikey, pids_swk_wmeta)

                                                                    #     else:
                                                                    #         # SPARQL based
                                                                    #         container = sparqlGatherPropertySetvaluesFromAllClasses(endpoint, pids, from_uri, apikey, source_type)

                                                                        if container:

                                                                            if isinstance(container, list):
                                                                                # num_item = min(2, len(container))
                                                                                # for item in range(num_item):
                                                                                #     print container[item]

                                                                                print("\n", len(container))

                                                                                #write_to_solr(container, 'http://localhost:8983/solr/restest_032016/')
                                                                                #http://stackoverflow.com/questions/26197494/authenticating-connection-in-pysolr
                                                                                #http://superuser.com/questions/259481/reverse-scp-over-ssh-connection/259493#259493
                                                                                write_to_solr(container, 'https://b2note.bsc.es/solr/b2note_testing/')

                                                                                print("\n", "# " * 15)

    except:

        print("Could not proceed with sparqlontoparser_main execution.")


sparqlontoparser_main()


# http://stackoverflow.com/questions/7722508/how-to-delete-all-data-from-solr-and-hbase
# http://localhost:8983/solr/restest_032016/update?stream.body=<delete><query>*:*</query></delete>
# http://localhost:8983/solr/restest_032016/update?stream.body=<commit/>

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


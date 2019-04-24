#!/usr/bin/env python2.7
# encoding: utf-8

# abremaud@esciencefactory.com 20160204

import datetime, copy, rdflib, csv, json, time
from rdflib import Graph

from .SparqlOntoParser_supports import get_json
from .SparqlOntoParser_supports import inputStringCheck, checkEndpointResponds, stringSimilarity
from .SparqlOntoParser_supports import obtainPredicateCount, mergeQueryResults
from .SparqlOntoParser_supports import modifyQueryForSubgraph, modifyQueryAddLimitAndOffset
from .SparqlOntoParser_supports import sparqlOneEndpoint, urllibOneEndpoint



class OntologyClass(object):

    def __init__(self):
        self.labels             = []
        self.synonyms           = []
        self.direct_parents     = []
        self.ancestors          = []
        self.direct_children    = []
        self.descendants        = []
        self.uris               = []
        self.description        = []
        self.indexed_date       = ""
        self.text_auto          = "empty"
        # abremaud 20160427
        self.short_form         = ""    # not originally included
        self.ontology_iri       = ""    # not originally included
        self.ontology_name      = ""    # not originally included
        self.ontology_acronym   = ""    # not originally planned
        self.ontology_version   = ""    # not originally planned
        self.ontology_vdate     = ""    # not originally planned


    def create_text_auto_from_labels(self):
        #merge labels
        if self.labels:
            self.text_auto = ' '.join(self.labels)

    def create_short_form_from_uris(self):
        #retrieve character sequence following last slash character of a uri
        if self.uris:
            rev_url = self.uris[0][::-1]
            self.short_form = rev_url[:rev_url.find('/')][::-1]

    def api_ontology_metadata(self, apikey=None):
        try:
            if self.ontology_iri:
                if apikey:
                    j = get_json(str(self.ontology_iri), str(apikey))
                else:
                    j= get_json(str(self.ontology_iri))
                if isinstance(j, dict):
                    for k in ["name", "acronym"]:
                        if k in list(j.keys()) and isinstance(j[k], str):
                            if k=="name": self.ontology_name.append(j[k])
                            if k=="acronym": self.ontology_acronym.append(j[k])
        except:
            pass

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keysv=True, indent=4)


def fillOntoClassField(onto_class=None, fieldname=None, info=None):

    out = None

    try:

        if onto_class and fieldname and info:

            if isinstance(onto_class, OntologyClass):

                if isinstance(fieldname, str):

                    if fieldname in list(onto_class.__dict__.keys()):

                        if isinstance(onto_class.__dict__[fieldname], str):

                            if isinstance(info, str):

                                onto_class.__dict__[fieldname] = info

                            elif isinstance(info, list):

                                for item in info:

                                    onto_class = fillOntoClassField(onto_class, fieldname, item)

                        elif isinstance(onto_class.__dict__[fieldname], list):

                            if isinstance(info, str) and info not in onto_class.__dict__[fieldname]:

                                onto_class.__dict__[fieldname].append(info)

                            elif isinstance(info, list):

                                for item in info:

                                    onto_class = fillOntoClassField(onto_class, fieldname, item)

        out = onto_class

    except:

        "could not fill ontology class field with provided info."

    return out


def updateOntoClassFields(onto_class=None, r=None):

    out = None

    try:

        if onto_class and r:

            if isinstance(onto_class, OntologyClass) and isinstance(r, dict):

                for k in list(r.keys()):

                    if isinstance(k, str):

                        if r[k]:

                            if isinstance(r[k], dict):

                                if "value" in list(r[k].keys()):

                                    if isinstance(r[k]["value"], str):

                                        onto_class = fillOntoClassField(onto_class, k, r[k]["value"])

                onto_class.create_text_auto_from_labels()

                #set datetime
                date_now = datetime.datetime.today().strftime("%Y-%m-%dT00:00:00Z")
                onto_class.indexed_date = date_now

                out = onto_class

    except:

        print("Could not update ontology class fields.")

    return out


def buildOntoClassContainer(res):

    out = None

    try:

        if res:

            if isinstance(res, dict):

                if "results" in list(res.keys()):

                    if isinstance(res["results"], dict):

                        if "bindings" in list(res["results"].keys()):

                            if isinstance(res["results"]["bindings"], list):

                                container = []

                                classes_analysed = set()

                                counter = 0

                                for r in res["results"]["bindings"]:

                                    counter += 1

                                    if "uris" in list(r.keys()) and "value" in list(r["uris"].keys()) and isinstance(r["uris"]["value"], str):

                                        curr_class = None

                                        if r["uris"]["value"] in classes_analysed:

                                            for exist_class in container:

                                                if r["uris"]["value"] in exist_class.uris:

                                                    curr_class = exist_class
                                                    break

                                        if not curr_class:

                                            curr_class = OntologyClass()
                                            curr_class.uris.append( r["uris"]["value"] )
                                            curr_class.create_short_form_from_uris()

                                        if curr_class:

                                            curr_class = updateOntoClassFields(curr_class, r)

                                            if r["uris"]["value"] in classes_analysed:

                                                container = [exist_class for exist_class in container if r["uris"]["value"] not in exist_class.uris]

                                            container.append( curr_class )
                                            classes_analysed.add( r["uris"]["value"] )

                                out = [oc.__dict__ for oc in container]

    except:

        print("Could not build container of ontology classes.")

    return out


def jsonOrFollow(url=None, pids=None, apikey=None, binding=None, follow_keys_list=None):

    out = None

    try:

        if not binding: binding = {}

        o_meta = None

        if url:

            if isinstance(url, str):

                if not apikey:

                    o_meta = get_json(str(url))

                elif isinstance(apikey, str):

                    o_meta = get_json(str(url), apikey)

                elif isinstance(apikey, str):

                    o_meta = get_json(str(url), str(apikey))

        if o_meta and pids:

            if isinstance(o_meta, dict) and isinstance(pids, tuple):

                for p in pids:

                    if isinstance(p, dict):

                        for k in list(p.keys()):

                            if p[k] in list(o_meta.keys()):

                                if isinstance(o_meta[p[k]], str):

                                    binding[str(k)] = {'type': 'typed-literal', 'value': o_meta[p[k]]}

                                elif isinstance(o_meta[p[k]], list):

                                    for elit in o_meta[p[k]]:

                                        if isinstance(elit, str):

                                            if k not in list(binding.keys()):

                                                binding[str(k)] = []

                                            binding[str(k)].append({'type': 'typed-literal', 'value': elit})

                            elif follow_keys_list:

                                if isinstance(follow_keys_list, list):

                                    for item in follow_keys_list:

                                        binding = jsonOrFollow(url, pids, apikey, binding, item)

                                if isinstance(follow_keys_list, str):

                                    if "links" in list(o_meta.keys()) and isinstance(o_meta["links"], dict) and follow_keys_list in list(o_meta["links"].keys()):

                                        if isinstance(o_meta["links"][follow_keys_list], str):

                                            binding = jsonOrFollow(o_meta["links"][follow_keys_list], pids, apikey, binding)

                out = binding

    except:

        print("Could not json_or_follow.")

    return out


def addOntoMetadataToMockSparql(res=None, pids=None, apikey=None):

    out = None

    try:

        prev_onto_dict = {}

        if res:

            if isinstance(res, dict):

                if "results" in list(res.keys()):

                    if isinstance(res["results"], dict):

                        if "bindings" in list(res["results"].keys()):

                            if isinstance(res["results"]["bindings"], list):

                                for item in res["results"]["bindings"]:

                                    if isinstance(item, dict):

                                        if "ontology_iri" in list(item.keys()):

                                            if isinstance(item["ontology_iri"], dict):

                                                if "value" in list(item["ontology_iri"].keys()):

                                                    if isinstance(item["ontology_iri"]["value"], str):

                                                        binding = {}

                                                        if item["ontology_iri"]["value"] in list(prev_onto_dict.keys()):

                                                            binding = prev_onto_dict[item["ontology_iri"]["value"]]

                                                        else:

                                                            binding = jsonOrFollow(item["ontology_iri"]["value"], pids, apikey, None, "latest_submission")

                                                            if binding:

                                                                if isinstance(binding, dict):

                                                                    prev_onto_dict[item["ontology_iri"]["value"]] = binding

                                                        if binding:

                                                            if isinstance(binding, dict):

                                                                for k in list(binding.keys()):

                                                                    if isinstance(k, str) and "ontology_" in k:

                                                                        if "head" in list(res.keys()):

                                                                            if isinstance(res["head"], dict):

                                                                                if "vars" in list(res["head"].keys()):

                                                                                    if isinstance(res["head"]["vars"], list):

                                                                                        if k not in res["head"]["vars"]:

                                                                                            res["head"]["vars"].append(str(k))

                                                                        item[str(k)] = binding[k]

                                out = res

    except:

        print("Could not add ontology metadata info to mock sparql json.")

    return out


def fillMockSparqlResultObjectWithCollectionItemInfo(coll_item=None, pids=None, res=None):

    out = None

    try:

        if coll_item and pids and res:

            if isinstance(coll_item, dict) and isinstance(pids, tuple) and isinstance(res, dict):

                binding = {}

                for p in pids:

                    if isinstance(p, dict):

                        for k in list(p.keys()):

                            if k:

                                fld_ctnt = None

                                if p[k] in list(coll_item.keys()):

                                    fld_ctnt = coll_item[p[k]]

                                elif "links" in list(coll_item.keys()) and isinstance(coll_item["links"], dict) and p[k] in list(coll_item["links"].keys()):

                                    fld_ctnt = coll_item["links"][p[k]]

                                if fld_ctnt:

                                    if isinstance(fld_ctnt, str):

                                        if k not in res["head"]["vars"]: res["head"]["vars"].append(str(k))

                                        if k == "uris" or k == "ontology_iri":

                                            binding[str(k)] = {'type': 'uri', 'value': str(fld_ctnt)}

                                        else:

                                            binding[str(k)] = {'type': 'typed-literal', 'value': str(fld_ctnt)}

                        for k in list(p.keys()):

                            if k:

                                fld_ctnt = None

                                if p[k] in list(coll_item.keys()):

                                    fld_ctnt = coll_item[p[k]]

                                elif "links" in list(coll_item.keys()) and isinstance(coll_item["links"], dict) and \
                                                p[k] in list(coll_item["links"].keys()):

                                    fld_ctnt = coll_item["links"][p[k]]

                                if fld_ctnt:

                                    if isinstance(fld_ctnt, list):

                                        for item in fld_ctnt:

                                            if isinstance(item, str):

                                                if k not in res["head"]["vars"]: res["head"]["vars"].append(str(k))

                                                binding[str(k)] = {'type': 'typed-literal', 'value': str(item)}

                                                res["results"]["bindings"].append(copy.deepcopy(binding))

                if binding and binding not in res["results"]["bindings"]: res["results"]["bindings"].append(binding)

                out = res

    except:

        print("Could not fill mock SPARQL result object with collection item information.")

    return out


def makeMockSparqlResultFromAPIclassCollection(props, pids):

    out = None

    try:

        if props and pids:

            if isinstance(props, dict) and isinstance(pids, tuple):

                if "collection" in list(props.keys()):

                    if isinstance(props["collection"], list):

                        res = {'head': {'link': [], 'vars': []}, 'results': {'distinct': False, 'bindings': [], 'ordered': True}}

                        for coll_item in props["collection"]:

                            if isinstance(coll_item, dict) and isinstance(pids, tuple) and isinstance(res, dict):

                                res = fillMockSparqlResultObjectWithCollectionItemInfo( coll_item, pids, res )

                        out = res

    except:

        print("Could not make mock SPARQL result from API class collection.")

    return out


def apiGatherPropertySetValuesFromAllClasses(from_uri=None, apikey=None, pids=None):

    out = None

    try:

        if from_uri and apikey and pids:

            if isinstance(from_uri, str) and isinstance(apikey, str) and isinstance(pids, tuple):

                rpp = 1000

                props = None
                props = get_json( from_uri + "/classes?pagesize=" + str(rpp), apikey )

                if props and isinstance(props, dict):

                    container = []

                    if "pageCount" in list(props.keys()):

                        pageCount = props["pageCount"]

                        start = time.time()

                        for curr_page in range(pageCount):

                            props = None
                            props = get_json( from_uri + "/classes?pagesize=" + str(rpp) + "&page=" + str(curr_page+1), apikey )
                            res   = makeMockSparqlResultFromAPIclassCollection(props, pids)
                            res   = addOntoMetadataToMockSparql(res, pids, apikey)
                            page_container = None
                            page_container = buildOntoClassContainer(res)
                            if page_container: container += page_container

                            print("Processing page", str(curr_page+1) + "/" + str(pageCount), "using pageCount method.", \
                                len(container), "in", time.time()-start, "s")

                    elif "nextPage" in list(props.keys()):

                        nextPage = True

                        while nextPage:

                            #print "Processing page", nextPage, "using nextPage method."

                            nextPage = False
                            nextPage = props["nextPage"]
                            res      = makeMockSparqlResultFromAPIclassCollection(props, pids)
                            res      = addOntoMetadataToMockSparql(res, pids, apikey)
                            page_container = []
                            page_container = buildOntoClassContainer(res)
                            if page_container: container += page_container
                            props = None
                            if nextPage:
                                props = get_json( from_uri + "/classes?pagesize=" + str(rpp) + "&page=" + str(nextPage), apikey )

                    else:

                        res = makeMockSparqlResultFromAPIclassCollection(props, pids)
                        res = addOntoMetadataToMockSparql(res, pids, apikey)
                        container = buildOntoClassContainer(res)

                    out = container

    except:

        print("Could gather set of properties from all API classes.")

    return out


def repeatQueryInSmallerChunks(endpoint=None, pids=None, from_uri=None, apikey=None, endpoint_type=None):

    out = None

    try:

        if endpoint and pids:

            if isinstance(endpoint, str) and isinstance(pids, tuple):

                res_p       = None
                res_t       = dict()
                worksatall  = False
                pids_test   = tuple()
                pids_works  = tuple()

                nsws = None

                if endpoint_type:

                    if isinstance(endpoint_type, str):

                        if endpoint_type == "endpoint_nsws":

                            nsws = True

                for p in pids:

                    if isinstance(p, dict):

                        p_test      =   {}
                        p_works     =   {}
                        pids_test   +=  (p_test,)
                        pids_works  +=  (p_works,)

                        for k in list(p.keys()):

                            if isinstance(p[k], str):

                                p_test[k] = p[k]
                                query = makeQueryForPropertyValues( pids_test )

                                if from_uri and not nsws:

                                    if isinstance(from_uri, str):

                                        query = modifyQueryForSubgraph( query, from_uri )

                                query = modifyQueryAddLimitAndOffset(query, 1)
                                query = query[:query.find("LIMIT")] + "ORDER BY ?id\n" + query[query.find("LIMIT"):]

                                res_p = None

                                if nsws:

                                    res_p = urllibOneEndpoint( endpoint, query, from_uri, apikey )

                                else:

                                    res_p = sparqlOneEndpoint( endpoint, query, apikey )

                                if res_p:

                                    worksatall = True
                                    p_works[k] = p[k]

                                else:

                                    p_test = {z:p_works[z] for z in list(p_works.keys())}

                        if not worksatall: break

                if res_p: res_t = res_p

                if worksatall:

                    bind_empty  = 0
                    attempts    = 1
                    successes   = 1
                    offset      = 1
                    limit       = 2

                    while bind_empty<10 and successes>0 and successes>attempts/10:

                        attempts += 1
                        query = makeQueryForPropertyValues( pids_works )

                        if from_uri and not nsws:

                            if isinstance(from_uri, str):

                                    query = modifyQueryForSubgraph( query, from_uri )

                        query = modifyQueryAddLimitAndOffset(query, limit, offset)

                        query = query[:query.find("LIMIT")] + "ORDER BY ?id\n" + query[query.find("LIMIT"):]

                        try:

                            res_c = None

                            if nsws:

                                res_c = urllibOneEndpoint( endpoint, query, from_uri, apikey )

                            else:

                                res_c = sparqlOneEndpoint( endpoint, query, apikey )

                            if res_c:

                                successes += 1
                                offset = offset + limit

                                if isinstance(res_c, dict):

                                    if "results" in list(res_c.keys()):

                                        if isinstance(res_c["results"], dict):

                                            if "bindings" in list(res_c["results"].keys()):

                                                if isinstance(res_c["results"]["bindings"], list):

                                                    if len(res_c["results"]["bindings"]) > 0:

                                                        res_t       = mergeQueryResults(res_t, res_c)
                                                        bind_empty  = 0
                                                        limit       = limit * 2

                                                    else:

                                                        bind_empty += 1

                            else:

                                limit = max(1, int(limit/2))

                        except:

                            limit = max(1, int(limit/2))
                            pass

                if res_t: out = res_t

    except:

        print("Could not repeat query in smaller chunks.")

    return out


def sparqlGatherPropertySetvaluesFromAllClasses( endpoint=None, pids=None, from_uri=None, apikey=None, endpoint_type=None ):

    out = None

    try:

        if endpoint and pids:

            if isinstance( endpoint, str ) and isinstance( pids, tuple ):

                res = None

                query = makeQueryForPropertyValues(pids)

                if endpoint_type:

                    if isinstance(endpoint_type, str):

                        if endpoint_type == "endpoint_nsws":

                            res = urllibOneEndpoint(endpoint, query, from_uri, apikey)

                if not res:

                    if checkEndpointResponds( endpoint, from_uri, apikey ):

                        if from_uri:

                            if isinstance( from_uri, str ):

                                query = modifyQueryForSubgraph( query, from_uri )

                                res = sparqlOneEndpoint( endpoint, query, apikey )

                if not res: res = repeatQueryInSmallerChunks( endpoint, pids, from_uri, apikey, endpoint_type )

                out = buildOntoClassContainer( res )

    except:

        print("Could not gather set of properties from all sparql endpoint classes.")

    return out


def repeatPropQueryWithDecreasingLimit( endpoint=None, query=None, from_uri=None, apikey=None, endpoint_type=None ):

    out = None

    try:

        if endpoint and query:

            if inputStringCheck(endpoint) and inputStringCheck(query):

                res = None

                sws = None

                if endpoint_type:

                    if isinstance(endpoint_type, str):

                        if endpoint_type == "endpoint_nsws":

                            res = urllibOneEndpoint(endpoint, query, from_uri, apikey)

                if not res:

                    sws = checkEndpointResponds(endpoint, from_uri, apikey)

                    if sws:

                        if from_uri:

                            if inputStringCheck(from_uri):

                                query = modifyQueryForSubgraph( query, from_uri )

                        res = sparqlOneEndpoint( endpoint, query, apikey )

                #print res

                if not res:

                    pred_count = None

                    pred_count = obtainPredicateCount( endpoint, from_uri, apikey, endpoint_type )

                    if pred_count:

                        offset = 0

                        limit = max(1, int(pred_count/2))

                        while offset < pred_count and limit>0:

                            print("processing:", offset, "+", limit)

                            if limit < 1: limit = 1

                            if offset + limit > pred_count:

                                limit = pred_count - offset + 1

                            q = modifyQueryAddLimitAndOffset( query, limit, offset )

                            q = q[:q.find("LIMIT")] + "\nORDER BY ?oo\n" + q[q.find("LIMIT"):]

                            print(q)

                            r = None

                            if sws:

                                r = sparqlOneEndpoint( endpoint, q, apikey )

                            else:

                                r = urllibOneEndpoint( endpoint, q, from_uri, apikey )

                            if r:

                                if res:

                                    res = mergeQueryResults( res, r )

                                else:

                                    res = r

                                offset += limit

                            else:

                                if limit <= 1:

                                    break

                                limit = max(1, int(limit/2))

                out = res

    except:

        print("Could not repeat query with decreasing limit.")

    return out


def gatherPropIDsFromAPIendpoint( mandatory_prop_dict=None, optional_prop_dict=None, endpoint=None, from_uri=None, apikey=None ):

    out = None

    try:

        if endpoint and from_uri and apikey:

            if inputStringCheck(endpoint) and inputStringCheck(from_uri) and inputStringCheck(apikey):

                if endpoint.lower() in from_uri.lower():

                    # Get the available resources
                    props = get_json( from_uri+"/properties/", apikey )

                    res = {'head': {'link': [], 'vars': ['oo']},
                           'results': {'distinct': False, 'bindings': [], 'ordered': True}}

                    joined_prop_dict = mandatory_prop_dict

                    for k in list(optional_prop_dict.keys()):
                        if k not in list(joined_prop_dict.keys()):
                            joined_prop_dict[k] = optional_prop_dict[k]

                    for key, val in joined_prop_dict.items(): # from data input (i.e. parameters)

                        if inputStringCheck(key):

                            if key not in res["head"]["vars"]:

                                res["head"]["vars"].append( str(key) )

                            if inputStringCheck(val):

                                for prop in props: # from API

                                    if isinstance(prop, dict):

                                        if "label" in list(prop.keys()) and "id" in list(prop.keys()):

                                            if isinstance(prop["label"], str) and val.lower() in prop["label"].lower():

                                                res["results"]["bindings"].append(\
                                                    {'oo':{'type': 'literal', 'value': str(prop["label"])},\
                                                     str(key):{'type': 'uri', 'value': str(prop["id"])}})

                                            elif isinstance(prop["label"], list):

                                                for item in prop["label"]:

                                                    if isinstance(item, str) and val.lower() in item.lower():

                                                        res["results"]["bindings"].append(\
                                                            {'oo':{'type': 'literal', 'value': str(item)},\
                                                             str(key):{'type': 'uri', 'value': str(prop["id"])}})

                    out = res

    except:

        print("Could not gather property IDs from API endpoint:", from_uri)

    return out


def obtainPropertyIDs( propsofi=None, endpoint=None, from_uri=None, apikey=None, endpoint_type=None ):

    out = None

    try:

        # e.g. {'label': ['chamallow', 'pref-label', 'preferred term', 'moule a gauffre', 'editor preferred term', 'prophylaxie', 'bercail', 'nonobstant']}
        m_prop_dict = extractPropertiesOnRequiredStatus( propsofi, "mandatory" )
        # e.g. {'syn': ['salicorne', 'bachibouzouk', 'synonym', 'dezinguee', 'alternative term', 'cabale']}
        o_prop_dict = extractPropertiesOnRequiredStatus( propsofi,  "optional" )

        j=0

        # for keeping only the first item in the list of terms standing as value at dictionary key "None"
        # e.g. {'label': 'chamallow'}
        mandatory_prop_dict = { k:m_prop_dict[k][j] for k in list(m_prop_dict.keys()) if j<len(m_prop_dict[k]) }
        # e.g. {'syn': 'salicorne'}
        optional_prop_dict  = { k:o_prop_dict[k][j] for k in list(o_prop_dict.keys()) if j<len(o_prop_dict[k]) }


        # for being able to store best string match results between current query results and previous ones
        # we increase depth of dictionary entries by making these entries (sub-)dictionaries themselves.
        # e.g. {'label': {'target': 'chamallow'}}
        mandat_prop_dict = { k:{"target":mandatory_prop_dict[k]} for k in list(mandatory_prop_dict.keys()) }
        # e.g. {'syn': {'target': 'salicorne'}}
        option_prop_dict = { k:{"target":optional_prop_dict[k]} for k in list(optional_prop_dict.keys()) }

        max_hook_nb = max([ len(o_prop_dict[k]) for k in list(o_prop_dict.keys()) ])

        # Interrupt before end of term list in case that for each term an exact property label match has been found and thus its ID stored.
        while (j==0 or j<max_hook_nb) and (not allPropertyIDsIdentified( mandat_prop_dict ) or not allPropertyIDsIdentified( option_prop_dict )):

            #print query

            if endpoint:

                if inputStringCheck(endpoint):

                    # retrieving from API
                    if endpoint_type and inputStringCheck(endpoint_type) and endpoint_type=='api':

                        res = gatherPropIDsFromAPIendpoint( mandatory_prop_dict, optional_prop_dict, endpoint, from_uri, apikey )

                    # retrieving from SPARQL endpoint
                    else:

                        query = makeQueryForPropertyIDs( mandatory_prop_dict, optional_prop_dict )

                        if endpoint_type and inputStringCheck(endpoint_type) and endpoint_type=='endpoint_nsws':

                            res = repeatPropQueryWithDecreasingLimit( endpoint, query, from_uri, apikey, endpoint_type )

                        else:

                            res = repeatPropQueryWithDecreasingLimit( endpoint, query, from_uri, apikey )

                    if res:

                        mandat_prop_dict = updateDictWithQueryResults( mandat_prop_dict, res )

                        option_prop_dict = updateDictWithQueryResults( option_prop_dict, res )

            j += 1

            # print "\n", j
            #
            # print mandat_prop_dict
            #
            # print option_prop_dict, "\n"

            mandatory_prop_dict = { k:m_prop_dict[k][j] for k in list(m_prop_dict.keys()) if j<len(m_prop_dict[k]) }

            optional_prop_dict =  { k:o_prop_dict[k][j] for k in list(o_prop_dict.keys()) if j<len(o_prop_dict[k]) }

            for k in list(mandatory_prop_dict.keys()):

                if k in list(mandat_prop_dict.keys()):

                    mandat_prop_dict[k]["target"] = mandatory_prop_dict[k]

            for k in list(optional_prop_dict.keys()):

                if k in list(optional_prop_dict.keys()):

                    option_prop_dict[k]["target"] = optional_prop_dict[k]

        mandat_prop_dict = keepBestLabelsWithPerfectMatch( mandat_prop_dict )

        option_prop_dict = keepBestLabelsWithPerfectMatch( option_prop_dict )

        if mandat_prop_dict or option_prop_dict:

            out = ( mandat_prop_dict, option_prop_dict )

    except:

        print("Could not proceed with obtaining property IDs.")

    return out


def keepBestLabelsWithPerfectMatch( prop_dict ):

    out = None

    try:

        p_dict = {}

        for k in list(prop_dict.keys()):

            if prop_dict[k]:

                if type(prop_dict[k]) is dict:

                    if "ID" and "match" in list(prop_dict[k].keys()):

                        if prop_dict[k]["ID"] and prop_dict[k]["match"]:

                            if type(str(prop_dict[k]["ID"])) is str and type(prop_dict[k]["match"]) is float:

                                if prop_dict[k]["match"] == 1:

                                    p_dict[k] = prop_dict[k]["ID"]

        if p_dict != {}: out = p_dict

    except:

        print("Could not proceed with keeping prop_dict best_match_labels with perfect match.")

    return out


def updateDictWithQueryResults( prop_dict, query_res ):

    out = None

    try:

        if prop_dict and query_res:

            if type(prop_dict) is dict and type(query_res) is dict:

                if "head" in list(query_res.keys()):

                    if "vars" in query_res["head"]:

                        if "results" in list(query_res.keys()):

                            if "bindings" in query_res["results"]:

                                for content in query_res["results"]["bindings"]:

                                    for item in query_res["head"]["vars"]: # item = "oo", "label", "def" (sparql_var)

                                        if item in list(content.keys()):

                                            if 'value' in list(content[item].keys()):

                                                if item in list(prop_dict.keys()):

                                                    if type(prop_dict[item]) is dict:

                                                        if "ID" not in list(prop_dict[item].keys()):

                                                            if "oo" in list(content.keys()):

                                                                if 'value' in list(content["oo"].keys()) and "target" in list(prop_dict[item].keys()):

                                                                    prop_dict[item]["ID"] = content[item]['value']

                                                                    prop_dict[item]["best_match_label"] = content["oo"]['value']

                                                                    prop_dict[item]["match"] = stringSimilarity( content["oo"]['value'], prop_dict[item]["target"] )

                                                        elif "target" in list(prop_dict[item].keys()) and "match" in list(prop_dict[item].keys()) and "oo" in list(content.keys()):

                                                            if 'value' in list(content["oo"].keys()) and type(str(prop_dict[item]["target"])) is str and type(prop_dict[item]["match"]) is float:

                                                                if stringSimilarity( content["oo"]['value'], prop_dict[item]["target"] ) > prop_dict[item]["match"]:

                                                                    prop_dict[item]["ID"] = content[item]['value']

                                                                    prop_dict[item]["best_match_label"] = content["oo"]['value']

                                                                    prop_dict[item]["match"] = stringSimilarity( content["oo"]['value'], prop_dict[item]["target"] )

                                out = prop_dict

    except:

        print("Could not update dictionary with query results.")

    return out


def allPropertyIDsIdentified( prop_dict ):

    out = None

    allIDs = True

    try:

        if prop_dict:

            if type(prop_dict) is dict:

                for item in list(prop_dict.keys()):

                    if "ID" in list(prop_dict[item].keys()) and "match" in list(prop_dict[item].keys()):

                        if type(str(prop_dict[item]["ID"])) is str and type(prop_dict[item]["match"]) is float:

                            if prop_dict[item]["match"] < 1:

                                allIDs = False
                                break

                        else:

                            allIDs = False

                    else:

                        allIDs = False

                    out = allIDs

    except:

        print("Could not proceed with checking that all properties were identified.")

    return out


def switchKeysSparql2OntoClass(pids, propsofi):

    out = None

    try:

        if pids and propsofi:

            if isinstance(pids, tuple) and isinstance(propsofi, list):

                new_pids = tuple()

                for p in pids:

                    if isinstance(p, dict):

                        switched = {}

                        for key in list(p.keys()):

                            if key and isinstance(key, str):

                                for prop in propsofi:

                                    if isinstance(prop, dict):

                                        if "output_name" and "sparql_var" in list(prop.keys()):

                                            if isinstance(prop["sparql_var"], str) and isinstance(prop["output_name"], str):

                                                if prop["sparql_var"] == key:

                                                    switched[prop["output_name"]] = key
                                                    break

                        if switched:

                            new_pids += (switched,)

                        else:

                            new_pids += (p,)

                out = new_pids

    except:

        print("Could not switch pids dict keys from sparql to onto_class attribute field name.")

    return out


def extractPropertiesOnRequiredStatus( propsofi=None, keyword=None ):

    out = None

    try:

        if propsofi and keyword:

            if type(propsofi) is list and type(keyword) is str:

                out = {}

                for prop in propsofi:

                    if "required_status" in list(prop.keys()):

                        if prop["required_status"] == keyword:

                            if "sparql_var" in list(prop.keys()):

                                if None in list(prop.keys()):

                                    for hook_str in prop[None]:

                                        if prop["sparql_var"] in list(out.keys()):

                                            out[prop["sparql_var"]].append(hook_str)

                                        else:

                                            out[prop["sparql_var"]] = [hook_str]

    except:

        print("Could not extract properties based on keyword:", keyword)

    return out


def reformatpidsForAPIuse(pids=None, propsofi=None):

    out = None

    try:

        if pids and propsofi:

            if isinstance(propsofi, list) and isinstance(pids, tuple):

                meta_pids   = None

                meta_pids   = extractPropertiesOnRequiredStatus(propsofi, "automatic")

                meta_pids   = switchKeysSparql2OntoClass((meta_pids,), propsofi)

                if meta_pids and isinstance(meta_pids, tuple) and len(meta_pids)==1:

                    meta_pids = meta_pids[0]

                else:

                    meta_pids = None

                pids_out    = None

                pids_out    = switchKeysSparql2OntoClass(pids, propsofi)

                if meta_pids and pids_out:

                    if isinstance(meta_pids, dict) and isinstance(pids_out, tuple):

                        for k in list(meta_pids.keys()):

                            if isinstance(k, str) and isinstance(meta_pids[k], str):

                                if k and meta_pids[k]:

                                    replaced = False

                                    for p in pids_out:

                                        if isinstance( p, dict ):

                                            if k in list(p.keys()):

                                                p[k] = str(meta_pids[k])
                                                replaced = True
                                                break

                                    if not replaced:

                                        if len(pids_out)>0:

                                            if isinstance( pids_out[1], dict ):

                                                pids_out[1][k] = str(meta_pids[k])

                                        else:

                                            pids_out += ({k:str(meta_pids[k])},)

                if pids_out: out = pids_out

    except:

        print("Could not reformat pids structure for API use.")

    return out


def makeQueryForPropertyIDs( mandatory_prop_dict=None, optional_prop_dict=None ):

    out = None

    try:

        query  = "SELECT DISTINCT ?oo"

        if mandatory_prop_dict:

            if type(mandatory_prop_dict) is dict:

                for m in list(mandatory_prop_dict.keys()):

                    if inputStringCheck( m ) and inputStringCheck(mandatory_prop_dict[m]):

                        query += " ?" + m

        if optional_prop_dict:

            if type(optional_prop_dict) is dict:

                for o in list(optional_prop_dict.keys()):

                    if inputStringCheck( o ) and inputStringCheck(optional_prop_dict[o]):

                        query += " ?" + o

        query += "\nWHERE { \n"

        allButFirst = False

        if mandatory_prop_dict:

            if type(mandatory_prop_dict) is dict:

                for m in list(mandatory_prop_dict.keys()):

                    if inputStringCheck( m ) and inputStringCheck( mandatory_prop_dict[m] ):

                        if allButFirst:

                            query += "UNION\n"

                        else:

                            allButFirst = True

                        query += " {\n"
                        query += "  ?s ?" + m + " ?o .\n"
                        query += "  ?" + m + " ?pp ?oo .\n"
                        #query += "  FILTER(CONTAINS(LCASE(str(?oo)), LCASE('" + mandatory_prop_dict[m] + "')))\n"
                        # abremaud@esciencefactory.com, 20160209
                        # Problem:
                        #  Query using REGEX not optimally efficient, orders of magnitude heavier burden
                        #  on sparql engine server side compared to sparql native expressions such as CONTAINS.
                        # Sources:
                        #  http://stackoverflow.com/questions/12353537/sparql-exact-match-regex
                        #  http://www.cray.com/blog/dont-use-hammer-screw-nail-alternatives-regex-sparql/
                        #
                        # abremaud@esciencefactory.com, 20160310
                        # Back to original less performance oriented design due to Ontobee endpoint handling neither
                        #  CONTAINS nor LCASE functionalities.
                        query += "  FILTER REGEX(str(?oo), '" + mandatory_prop_dict[m] + "', 'i')\n"
                        query += " }\n"

                        # abremaud@esciencefactory.com, 20160212
                        # Could maybe catch predicates on perfect match to last portion of uri character sequence.
                        # query += "UNION\n"
                        # query += " {\n"
                        # query += "  ?s ?" + m + " ?o .\n"
                        # query += "  ?" + m + " ?pp ?oo .\n"
                        # query += "  FILTER(STREND(LCASE(str(?" + m + ")), LCASE('" + mandatory_prop_dict[m] + "')))\n"
                        # query += " }\n"

        if optional_prop_dict:

            if type(optional_prop_dict) is dict:

                for o in list(optional_prop_dict.keys()):

                    if inputStringCheck( o ) and inputStringCheck( optional_prop_dict[o] ):

                        if allButFirst:

                            query += "UNION\n"

                        else:

                            allButFirst = True

                        query += " {\n"
                        query += "  ?s ?" + o + " ?o .\n"
                        query += "  ?" + o + " ?pp ?oo .\n"
                        #query += "  FILTER(CONTAINS(LCASE(str(?oo)), LCASE('" + optional_prop_dict[o] + "')))\n"
                        # abremaud@esciencefactory.com, 20160209
                        # See above for an explanation.
                        query += "  FILTER REGEX(str(?oo), '" + optional_prop_dict[o] + "', 'i')\n"
                        query += " }\n"

        query += "}"

        out = query

    except:

        print("Could not write down sparql query for property IDs.")

    return out


def makeQueryForPropertyValues( pids = None ):

    out = None

    try:

        query  = "SELECT DISTINCT ?id"

        if pids:

            if isinstance(pids, tuple) and len(pids)>0:

                for p in pids:

                    if isinstance(p, dict):

                        for k in list(p.keys()):

                            if inputStringCheck( str(k) ):

                                query += " ?" + str(k)

        query += "\nWHERE { \n"

        if pids:

            if isinstance(pids, tuple) and len(pids)>0:

                p = pids[0]

                if isinstance(p, dict):

                    for k in list(p.keys()):

                        if inputStringCheck( str(k) ) and inputStringCheck( str(p[k]) ):

                            query += " ?id <" + str(p[k]) +"> ?" + str(k) + " .\n"

            if isinstance(pids, tuple) and len(pids)>1:

                p = pids[1]

                if isinstance(p, dict):

                    for k in list(p.keys()):

                        if inputStringCheck( str(k) ) and inputStringCheck( str(p[k]) ):

                            query += " OPTIONAL{ ?id <" + str(p[k]) +"> ?" + str(k) + " . }\n"

        query += "}"

        out = query

    except:

        print("Could not write down sparql query for property values.")

    return out


def sparqlLocalFile( filepath, query ):

    out = None
    g = Graph()

    try:

        g.parse( filepath, format=filepath[::-1][:filepath[::-1].find(".")][::-1] )

        try:

            out = g.query(query).serialize(format="json")
            out = json.loads(out)

        except:

            print("Could not process formulated query on indicated file.")
            pass

    except:

        print("Could not parse indicated file:", filepath)
        pass

    return out


def csv2list( filepath ):

    out = None

    try:

        with open( filepath, 'rb' ) as csvfile:
            temp = csv.DictReader( csvfile, fieldnames=None, restkey=None, restval='', dialect='excel', delimiter=';' )
            out = []
            for row in temp:
                out.append( row )

    except:

        print("Could not load CSV file:", filepath)
        pass

    return out
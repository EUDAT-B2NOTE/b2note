__author__ = 'malone'

import pysolr


def write_to_solr(data, solr_location):
    #Setup a Solr instance. The timeout is optional.
    #this is hard coded but shouldn't be
    solr = pysolr.Solr(solr_location, timeout=60)

    # How you'd index data.
    solr.add(data)
    print "data added to solr"

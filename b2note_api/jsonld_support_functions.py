import re, datetime, collections
import logging

stdlogger = logging.getLogger('b2note')


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
import re, datetime


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
            print "readyQuerySetValuesForDumpAsJSONLD function, unhandled object type encountered:", type(o_in)
            pass
    except:
        o_out = None
        print "readyQuerySetValuesForDumpAsJSONLD function did not complete."
        pass
    return o_out

import xlrd
import os, sparql, re, sys
from sparql import SparqlException
from SPARQLWrapper import *
#SPARQLWrapper, JSON, XML, N3, RDF, SPARQLWrapperException

from topia.termextract import tag, extract
import codecs
from .models import Ontologies

from b2note import settings


def query_text(text, ontology):
    output = [ ]
    tagger = tag.Tagger()
    tagger.initialize()
    extractor = extract.TermExtractor(tagger)
    if (len(text) < 500):
        extractor.filter = extract.permissiveFilter
    terms = sorted(extractor(text))
    print len(terms)
    o = Ontologies.objects.get(name=ontology)
    i = 0
    search = u'' 
    while (i<len(terms)):
        j = 0;
	while (j<5 and i+j < len(terms)):
#            print terms[i+j][0]
            word = re.sub('[\@\[\]\|\?\~\*\:\;\'\!\"\(\)\-\/\_\,\.\$\%\&\d+]', '', terms[i+j][0]).lstrip()
            word = encode(word)
            j=j+1;
            if word != "" and len(word) > 2 and not re.search("object", word):
                if (j != 1):
                    search = search + "|"
                search = search+ "^"+ word+"| "+word+" |"+word+"$"
            
        i = i + j
        if(len(search)>0):
            if (search[0] == "|"):
                search = search[1:]
# lets construct the query depending on the Ontology
            try:
                q = "PREFIX "+ o.prefix + " SELECT DISTINCT ?Concept ?prefLabel WHERE { ?Concept ?x "+o.concept+" .  { ?Concept "+o.label+" ?prefLabel . FILTER (regex(str(?prefLabel), '("+search+")', 'i'))  }}"
#                q = "SELECT distinct ?s WHERE { ?s ?p ?o.  filter bif:contains(?o, '"+search+"') } limit 15 offset 0"
                print q
#                result = sparql.query('http://vocabs.lter-europe.net/PoolParty/sparql/EnvThes',q,36000)
#            result = sparql.query('http://sparql.bioontology.org/sparql/',q,36000)
                if(o.api == "sparqlWRAPPER"):
                    api_key = 'cbb1700d-bc7d-496a-a253-a868285412e0'
                    sparqlW = SPARQLWrapper(o.endpoint)
                    sparqlW.addCustomParameter("apikey",api_key)
	            sparqlW.setQuery(q)
                    sparqlW.setReturnFormat(JSON)
                    results = sparqlW.query().convert()
                    for result in results["results"]["bindings"]:
		        output.append([result["Concept"]["value"],result["prefLabel"]["value"]])
                elif(o.api == "sparql"):
                    result = sparql.query(o.endpoint,q,36000)
                    for row in result:
                      #print 'row:', row
                        values = sparql.unpack_row(row)
                        output.append([values[0],values[1],terms[0][0]])

            except SparqlException:
                try:
                    print "sparqlException q = ", q
                except UnicodeEncodeError:
                    print "UnicodeError"
            except UnicodeDecodeError:
                print "UnicodeDecodeError"
            except: 
                print "Unexpected error"
        search = ''
    return output


def readxls(file):
    text = ''
    workbook = xlrd.open_workbook(file)
    worksheets = workbook.sheet_names()
    for worksheet_name in worksheets:
        worksheet = workbook.sheet_by_name(worksheet_name)
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1
        curr_row = -1
        while curr_row < num_rows:
            curr_row += 1
            row = worksheet.row(curr_row)
            #print 'Row:', curr_row
            curr_cell = -1
            while curr_cell < num_cells:
                curr_cell += 1
                # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                cell_type = worksheet.cell_type(curr_row, curr_cell)
                cell_value = worksheet.cell_value(curr_row, curr_cell)
                if cell_type == 1:
                    text = text + cell_value
                #print '	', cell_type, ':', cell_value
    return text

def readpdf(file):
    input=file
    output= os.path.join(settings.MEDIA_ROOT,"out.txt")
    os.system(("pdftotext %s %s") %( input , output))
    file = codecs.open( output  , mode='r' , encoding="utf-8")
    text = file.read().encode("ascii", "ignore")
    os.system(("rm -f %s") %(output))
    return text

def encode(text):
    """
    For printing unicode characters to the console.
    """
    return text.encode('utf-8')

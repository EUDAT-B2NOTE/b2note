import xlrd
import sparql, re
from sparql import SparqlException
from topia.termextract import tag, extract


def query_text(text):
    output = [ ]
    tagger = tag.Tagger()
    tagger.initialize()
    extractor = extract.TermExtractor(tagger)
    #extractor.filter = extract.permissiveFilter
    terms = sorted(extractor(text))

    for term in terms:
        word = re.sub('[\|\~\*\:\;\'\!\"\(\)\-\/\_\,\.\$\%\&\d+]', '', term[0]).lstrip()
        #print word
        if word != "" and len(word) > 2 and not re.search("object", word):
            q = "PREFIX skos:<http://www.w3.org/2004/02/skos/core#> SELECT DISTINCT ?Concept ?prefLabel WHERE { ?Concept ?x skos:Concept .  { ?Concept skos:prefLabel ?prefLabel . FILTER (regex(str(?prefLabel), '"+ "(^"+ word+"| "+word+" |"+word+"$)', 'i'))  }}"
#            print q
            try:
                result = sparql.query('http://vocabs.lter-europe.net/PoolParty/sparql/EnvThes',q,36000)
                for row in result:
                    #print 'row:', row
                    values = sparql.unpack_row(row)
                    output.append([values[0],values[1],term])
            except SparqlException:
                print "sparqlException q = ", q
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

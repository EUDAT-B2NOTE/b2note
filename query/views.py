from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.forms.forms import NON_FIELD_ERRORS
from b2note import settings 

from .forms import DocumentForm, OntologyForm
from .models import Document
from .convert import * 

import os, sys, re, codecs

# Create your views here.
def index(request):
    documents = Document()
    form = DocumentForm()
    ont = OntologyForm()
    return render_to_response(
        'query/index.html',
        {'documents': documents, 'form': form, 'ont': ont},
        context_instance=RequestContext(request)
    )

#    return render(request, 'query/index.html')


def query_vocab(request):
    text = request.POST.get('text_parse', '')
    ontology = request.POST.get('ontology')
    return render(request, 'query/query_vocab.html', {'text': query_text(text,ontology)})

def query_file(request):
    output = [ ]
    text = [ ]
    error = 0
    ontology = request.POST.get('ontology')
    print ontology
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()
            filepath = os.path.join(settings.MEDIA_ROOT, newdoc.docfile.name)
            try:
                if newdoc.extension() == '.txt' or newdoc.extension() == '':
	    	    file = codecs.open( filepath  , mode='r' , encoding="utf-8")
            	    text = file.read().encode("ascii", "ignore")
                elif newdoc.extension() == '.xls':
                    text = readxls(filepath) 
                elif newdoc.extension() == '.pdf':
                    text = readpdf(filepath)
                else:
                    error_list = form.error_class(['File Format Not recognized'])
                    form._errors[NON_FIELD_ERRORS] = error_list
                    error = 1
            except UnicodeDecodeError:
                error_list = form.error_class(['Unicode/format error'])
                form._errors[NON_FIELD_ERRORS] = error_list
                error = 1

            if error == 0:
                return render(request, 'query/query_vocab.html', {'text': query_text(text, ontology)})
            else:
                documents=Document()
                return render_to_response(
                       'query/index.html',
                       {'documents': documents, 'form': form},
                       context_instance=RequestContext(request))


            #return render(request, 'query/query_vocab.html', {'text': file.read()})
            #return HttpResponseRedirect(reverse('query.list'))
    else:
        form = DocumentForm()

    documents = Document.objects.all()
    return render_to_response(
        'query/index.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )

#def query_text(text):
#    output = [ ]
#    tagger = tag.Tagger()
#    tagger.initialize()
#    extractor = extract.TermExtractor(tagger)
#    #extractor.filter = extract.permissiveFilter
#    terms = sorted(extractor(text))
#    for term in terms:
##	print term[0] 
#        word = re.sub('[\|\~\*\:\;\'\!\"\(\)\-\/\_\,\.\$\%\&\d+]', '', term[0]).lstrip()
#        if word != "" and len(word) > 2 and not re.search("object", word):
##            print word
#            q = "PREFIX skos:<http://www.w3.org/2004/02/skos/core#> SELECT DISTINCT ?Concept ?prefLabel WHERE { ?Concept ?x skos:Concept .  { ?Concept skos:prefLabel ?prefLabel . FILTER (regex(str(?prefLabel), '"+ "(^"+ word+"| "+word+" |"+word+"$)', 'i'))  }}"
##            print q
#            try:
#                result = sparql.query('http://vocabs.lter-europe.net/PoolParty/sparql/EnvThes',q,36000)
#                for row in result:
#                    #print 'row:', row
#                    values = sparql.unpack_row(row)
#                    output.append([values[0],values[1],term])
#            except SparqlException:
#                print "sparqlException"
#    return output
#
#

#	file = request.POST.get('datafile', '')
#	return render(request, 'query/query_file.html', {'text': file})

#class IndexView(generic.ListView):
#	template_name = 'query/index.html'
#    return render(template_name)

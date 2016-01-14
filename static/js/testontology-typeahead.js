/**
 * Created by malone on 15/09/15.
 */

/**
 * Note change the url of the solr server to point to the approriate service
 */

$(document).ready( function() {
  var ontologies = new Bloodhound( {
	datumTokenizer: Bloodhound.tokenizers.whitespace,
	queryTokenizer: Bloodhound.tokenizers.whitespace,
	limit: 5,
	remote: {
		url: "http://opseudat03.bsc.es:8983/solr/b2note_index/select?q=%QUERY&wt=json&indent=true",
//		url: 'http://b2note.bsc.es/static/fonts/a.json',
		wildcard: '%QUERY',
		filter: function(ontologies) {
			return $.map(ontologies.response.docs, function(ontology) {
				console.log("in")
				return { label: ontology.labels };
			});
		}
	}
  });
  
  ontologies.initialize();

  console.log(ontologies);

  $('.form-control').typeahead(null, {
  	name: 'ontologies',
	displayKey: 'label',
	minLength: 1,
	source: ontologies.ttAdapter(),
	templates: {
		suggestion: Handlebars.compile("<p style='padding:6px;'>{{label}}</p>"),
		empty: [
			'<div class="empty-message">',
		        'unable to find any result',
		        '</div>'
		].join('\n'),
		footer: Handlebars.compile("<b> Searched for '{{query}}'")
	}
  });
});

/*$(document).ready( function() {

    // constructs the suggestion engine
    var engine = new Bloodhound({
        datumTokenizer: function (datum) {
            return Bloodhound.tokenizers.whitespace(datum.title);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: 'http://opseudat03.bsc.es:8983/solr/b2note_index/select?q=%QUERY&wt=json&indent=true',
            wildcard: '%QUERY',
            filter: function (data) {
                return $.map(data.response.docs, function (suggestionSet) {
                    return{
                        label : suggestionSet.labels,
//                        ontology_name : suggestionSet.ontology_name,
//                        short_form : suggestionSet.short_form
                    };
                });
            }
        }

    });

    engine.initialize();

    $('#id_q').typeahead({
            hint: true,
            highlight: true,
            minLength: 1,
        },
        {
            name: 'engine',
	    display: 'label',

            source: engine.ttAdapter(),
            //source: engine


            templates: {
                empty: [
                    '<div class="empty-message">',
                    ' -No results-',
                    '</div>'
                ].join('\n'),
                suggestion: Handlebars.compile('<p class="Typeahead-input tt-input">{{label}}</p>') // +  '  {{short_form}}   #{{ontology_name}}</p>')
            },
            engine: Handlebars
        });


});*/

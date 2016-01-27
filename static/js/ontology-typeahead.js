/**
 * Created by malone on 15/09/15.
 *
 * Modified by prodenas on 19/01/16
 *
 */

$(document).ready( function() {

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
                        ontology_name : suggestionSet.ontology_name,
                        short_form : suggestionSet.short_form,
			json_document: suggestionSet
                    };
                });
            }
        }

    });

    // iniializes the engina
    engine.initialize();

    // gets the subject selected to provide the subject_tofeed field
    var elem = document.getElementById("subject");
    var subject = "";
    if (elem) {
    	subject = elem.getElementsByTagName("a")[0].innerHTML;
    }

    // selects the html element where the suggestion takes places
    $('#id_q').typeahead({
            hint: true,
            highlight: true,
            minLength: 1,
        },
        {
            name: 'engine',
	    display: 'label',

            source: engine.ttAdapter(),

            templates: {
                empty: [
                    '<div class="empty-message">',
                    ' -No results-',
                    '</div>'
                ].join('\n'),
                suggestion: Handlebars.compile('<p class="Typeahead-input tt-input">{{label}}</p>' + '  {{short_form}}   #{{ontology_name}}</p>')
            },
            engine: Handlebars
	// defines the event 'onclick'
        }).on('typeahead:selected', function(evt, data) {
	     /* pablo.rodenas@bsc.es, 19012016
	      *
	      * Problem: AJAX post method alone does not redirect to Django page.
	      *
	      * JS: http://stackoverflow.com/questions/29137910/redirecting-after-ajax-post-in-django
	      *
	      * (otherwise in Django): http://stackoverflow.com/questions/2140568/django-view-does-not-redirect-when-request-by-jquery-post
	      *
	      * Code source: https://github.com/mgalante/jquery.redirect
	      *
              */
            $.redirect('create_annotation',
	    	    {
		    	ontology_json: JSON.stringify(data.json_document),
		    	subject_tofeed: subject
		    });
    });
});

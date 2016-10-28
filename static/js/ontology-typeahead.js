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
            // What may be a relevant size of class subset for the user to select from VS. transaction size x user population?
            url: window.location.protocol + '//b2note.bsc.es/solr/b2note_index/select?q="%QUERY"&wt=json&indent=true&rows=1000',
            wildcard: '%QUERY',
            filter: function (data) {
                return $.map(data.response.docs, function (suggestionSet) {
                    return{
                        label : suggestionSet.labels,
                        ontology_acronym : suggestionSet.ontology_acronym,
                        short_form : suggestionSet.short_form,
			            json_document: suggestionSet
                    };
                });
            }
        }

    });

    // initializes the engine
    engine.initialize();

    // gets the subject selected to provide the subject_tofeed field
    var elem = document.getElementById("section_subject");
    var subject = "";
    var db_id = "";
    if (elem) {
    	subject = elem.getElementsByTagName("a")[0].innerHTML;
    } else {
        // abremaud@esciencefactory.com, 20160922
        // Handling typeahead from edit_annotation page
        if (document.getElementById("db_id")) {
            db_id = document.getElementById("db_id").value;
        }
    }
    // abremaud@esciencefactory.com, 20160129
    // gets the pid selected to provide the pid_tofeed field
    elem = document.getElementById("section_subject");
    var pid = "test";
    if (elem) {
    	pid = elem.getElementsByTagName("a")[1].innerHTML;
    }

    //$.ajaxSetup({data: {csrfmiddlewaretoken: '{{ csrf_token }}' },});

    // selects the html element where the suggestion takes places
    //$('#id_q').typeahead({
    $('[id^="id_q"]').typeahead({
            hint: true,
            highlight: true,
            minLength: 1,
        },
        {
            name: 'engine',
	        display: function(data) {
                return data.label + '  (' + data.ontology_acronym + ':' + data.short_form + ')';
            },

            source: engine.ttAdapter(),

            // Fix from: https://github.com/twitter/typeahead.js/issues/1232
            limit: Infinity,

            templates: {
                empty: [
                    '<div class="empty-message">',
                    ' -No results-',
                    '</div>'
                ].join('\n'),
                suggestion: Handlebars.compile('<p class="Typeahead-input tt-input">{{label}}' + ' ({{short_form}})</p>')
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


            //if (document.getElementById("section_subject")) {
            if (document.getElementById("semantic")) {

                $('#ontology_json').val( JSON.stringify(data.json_document) )

            } else {

                $('#'+this.parentElement.parentElement.querySelector('[id^="ontology_json"]').name).val( JSON.stringify(data.json_document) )

            }

//              abremaud 20161025, stop creating anntation upon simply selecting one entry,
//              instead selection label is output to the typeahead text-box while full information json
//              gets outputed to a hiden input for being POSTED upon user hitting submit...
//                $.redirect('create_annotation',
//                    {
//                    ontology_json: JSON.stringify(data.json_document),
//                    subject_tofeed: subject,
//                    pid_tofeed: pid,
//                    // abremaud@esciencefactory.com, 20160926
//                    // retrieve Django csrf token from html hidden input element
//                    csrfmiddlewaretoken: this.parentElement.previousElementSibling.value,
//                });

//            } else {
//                if (db_id != "") {
//                    $.redirect('edit_annotation',
//                        {
//                        ontology_json: JSON.stringify(data.json_document),
//                        db_id: db_id,
//                        // abremaud@esciencefactory.com, 20160926
//                        // retrieve Django csrf token from html hidden input element
//                        csrfmiddlewaretoken: this.parentElement.parentElement.firstChild.nextSibling.value,
//                    });
//                } else {
//                    $.redirect('search_annotation',
//                        {
//                        // abremaud@esciencefactory.com, 20160928
//                        // search annotations on keyword
//                        ontology_json: JSON.stringify(data.json_document),
//                        csrfmiddlewaretoken: this.form.firstChild.nextSibling.value,
//                    });
//                }
//            };
    });
});
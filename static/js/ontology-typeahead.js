/**
 * Created by malone on 15/09/15.
 *
 * Modified by prodenas on 19/01/16
 *
 */

$(document).ready( function() {

    var agglomerateOnLabel = function(input){
        labL = []
        newL = []
        for (k=0;k<input.length;k++){

            s = input[k].labels;
            s = s.replace(/([a-z])([A-Z])/g, '$1 $2');
            s = s.replace(/[_.:]/g, ' ');
            s = s.toLowerCase();
            s = s.replace(/^./, function(str){ return str.toUpperCase(); });

            if (labL.indexOf(s)<0) {
                sf = null;
                if (typeof input[k]['short_form'] !== 'undefined') {
                    sf = ' ' + input[k]['short_form'].slice(input[k]['short_form'].search(/[#/]/g)+1);
                }
                aggl = {
                    label: s,
                    extra: ' (' + input[k]['ontology_acronym'] + sf + ')',
                    count: null,
                    json_document: [input[k]],
                }
                aggl['norm(labels)'] = input[k]['norm(labels)'];
                newL.push( aggl );
                labL.push(s);
            } else {
                idx = labL.indexOf(s);
                if (newL[idx].label == s){
                    newL[idx].json_document.push( input[k] );
                    newL[idx].extra = null;
                    if (newL[idx].count == null) {
                        newL[idx].count = 2;
                    } else {
                        newL[idx].count = newL[idx].count+1; //newL[idx].json_document.length;
                    }
                }
            }
        }
        return newL
    };

    // constructs the suggestion engine
    var engine = new Bloodhound({
        datumTokenizer: function (datum) {
            return Bloodhound.tokenizers.whitespace(datum.label);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        sufficient: 201,
        prefetch: {
            url: '../static/files/sample.json',
            //cache: false,
            filter: function(response) {
                //console.log("THIS WORKS HERE TOO")
                //console.log(response)
                aggl_data = agglomerateOnLabel( response );
                return $.map(aggl_data, function(item) {
                    return {
                        label: item.label,
                        extra: item.extra,
                        count: item.count,
                        json_document: item.json_document
                    }
                });
            }
        },
        identify : function(item) {
            //console.log('identify GETS CALLED ');
            return item.label; //+ item.ontology_acronym + item.short_form;
        },
        sorter: function(a, b) {
            //console.log('sorter GETS CALLED ');
            if (typeof a.label !== 'undefined') {
                    //get input text
                var InputString =  $('[id^="id_q"]').val();

                    //move exact matches to top
                if(InputString==a.label){ return -1;}
                if(InputString==b.label){return 1;}

                    //close match without case matching
                if(InputString.toLowerCase() == a.label.toLowerCase()){ return -1;}
                if(InputString.toLowerCase() == b.label.toLowerCase()){return 1;}

                    //Single token or multiple
                if ( a["norm(labels)"] == 1 ){
                        //decreasing value of Lucene/Solr label norm metric
                    if (a.label.split(/[^A-Za-z0-9]/).length<b.label.split(/[^A-Za-z0-9]/).length) {
                        return -1
                    } else {
                            //input string is label string prefix
                        if( a.label.toLowerCase().indexOf(InputString.toLowerCase()) == 0 ){
                            if( b.label.toLowerCase().indexOf(InputString.toLowerCase()) !== 0 ){ return -1; }
                        } else {
                            if( b.label.toLowerCase().indexOf(InputString.toLowerCase()) == 0 ){ return 1; }
                        }
                            //increasing string length
                        if (a.label.length < b.label.length) {
                            return -1;
                        } else {
                            if (a.label.length > b.label.length) {
                                return 1;
                            } else {
                                //relegate containing digit or capital letter
                                if (/\d/.test(a.label)) { return 1 }
                                if (/\d/.test(b.label)) { return -1 }

                                if ((a.label.length>1) && (a.label.slice(1,a.label.length) !== a.label.slice(1,a.label.length).toLowerCase() )) {
                                    return 1
                                }
                                if ((b.label.length>1) && (b.label.slice(1,b.label.length) !== b.label.slice(1,b.label.length).toLowerCase() )) {
                                    return -1
                                }

                                //alphabetical order
                                return a.label.localeCompare(b.label);
                            }
                        }
                    }
                } else {
                        //input string is label string prefix
                    if( a.label.toLowerCase().indexOf(InputString.toLowerCase()) == 0 ){ return -1 }
                    if( b.label.toLowerCase().indexOf(InputString.toLowerCase()) == 0 ){ return 1 }
                        //input string contained in label string
                    if( a.label.toLowerCase().indexOf(InputString.toLowerCase())!== -1 ){ return -1 }
                    if( b.label.toLowerCase().indexOf(InputString.toLowerCase())!== -1 ){ return 1 }

                    if (a.label.split(/[^A-Za-z0-9]/).length > b.label.split(/[^A-Za-z0-9]/).length) { return -1 }
                    if (a.label.split(/[^A-Za-z0-9]/).length < b.label.split(/[^A-Za-z0-9]/).length) { return 1 }

                    if (a["norm(labels)"]>b["norm(labels)"]) { return -1 }
                    if (a["norm(labels)"]<b["norm(labels)"]) { return 1 }
                    //return a.label.localeCompare(b.label);
                }
            } else {
                return -1;
            }
        },
        remote: {
            // What may be a relevant size of class subset for the user to select from VS. transaction size x user population?
            /*url: window.location.protocol + '//b2note.bsc.es/solr/b2note_index/select?q=labels:%QUERY&wt=json&indent=true&rows=1000',*/
            /*url: window.location.protocol + '//b2note.bsc.es/solr/cleanup_test/select',*/
            url: 'https://b2note.bsc.es/solr/cleanup_test/select',
            /*url: window.location.protocol + '//b2note.bsc.es/solr/b2note_index/select',*/
            /* 20161109, abremaud@escienceafactory.com
                Boosting exact match on term label from Solr.
                http://stackoverflow.com/questions/37712129/how-to-use-typeahead-wildcard */
            /*wildcard: '%QUERY',*/
            /*rateLimitBy: 'debounce',*/
            /*rateLimitWait: 1400,*/
            prepare: function(query, settings) {
                if ((query.length<=4) && (query.split(/[^A-Za-z0-9]/).length<=1)) {
                    //console.log("Less than four letters single word input")
                    settings.url += '?q=((labels:/' + query +'.*/)';
                } else {
                    //console.log("More than four letters or mutliple words input")
                    settings.url += '?q=((labels:"' + query +'"^100%20OR%20labels:' + query +'*^20%20OR%20text_auto:/' + query +'.*/^10%20OR%20labels:*' + query + '*)';
                }
                settings.url += '%20AND%20NOT%20(labels:/Error[0-9].*/))'
                if (query.split(/[^A-Za-z0-9]/).length<=1) {
                    //alert("single-word");
                    settings.url += '&sort=norm(labels) desc';
                }
                settings.url += '&fl=labels,uris,ontology_acronym,short_form,synonyms,norm(labels)&wt=json&indent=true&rows=1000';
                return settings;
            },
            filter: function (data) {
                qstr = ""
                if (data.responseHeader.params.q){
                    beg = data.responseHeader.params.q.indexOf(':/');
                    fin = data.responseHeader.params.q.indexOf('.*');
                    qstr = data.responseHeader.params.q.substring(beg+2,fin);
                }

                aggl_data = agglomerateOnLabel(data.response.docs);
                //console.log(typeof data.response.docs + " " + typeof aggl_data)
                truncated_data = engine.sorter( aggl_data );

                //truncated_data = engine.sorter(data.response.docs);
                trunc_n = 1000;
                if ((qstr.length<=4) && (qstr.split(/[^A-Za-z0-9]/).length<=1)) {
                    trunc_n = 100;
                }
                if (truncated_data.length>trunc_n) {
                    truncated_data = truncated_data.slice(0,trunc_n);
                }
                //console.log('Matches (n): '+ data.response.numFound + ', Solr response time (ms): ' + data.responseHeader.QTime + ', Display: ' + truncated_data.length)
                return $.map(truncated_data, function (suggestionSet) {
                //return $.map(engine.sorter(data.response.docs), function (suggestionSet) {
                //return $.map(data.response.docs, function (suggestionSet) {
                    return{
                        label: suggestionSet.label,
                        extra: suggestionSet.extra,
                        count: suggestionSet.count,
                        json_document: suggestionSet.json_document
                    };
                });
            }
        }
    });

    // initializes the engine
    engine.clearPrefetchCache();
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
	            //console.log("TEST")
                hint_msg = data.label;
                if (data.extra !== null) {
                    hint_msg = hint_msg + ' ' + data.extra;
                } else if (data.count !== null) {
                    hint_msg = hint_msg + ' ['+data.count+' classes]';
                }
                return hint_msg;
            },

            source: engine.ttAdapter(),

            // Fix from: https://github.com/twitter/typeahead.js/issues/1232
            limit: Infinity,

            templates: {
                pending: '<div class="pending-message" style="font-size:12px;color:#cccccc;">Suggestions incoming...</div>',
                empty: [
                    '<div class="empty-message">',
                    ' -No results-',
                    '</div>'
                ].join('\n'),
                footer: '<div class="pending-message" style="font-size:12px;color:#cccccc;">More suggestions incoming...</div>',
                suggestion: Handlebars.compile('<p class="Typeahead-input tt-input">{{label}}' + ' <span style="font-size:12px;">{{extra}}</span>' + '{{#if count}}<span class="badge" style="background:grey;width:auto;font-size:11px;padding:4px;padding-top:2px;padding-bottom:2px;">{{count}}</span>{{/if}}</p>')
            },
            engine: Handlebars
        }).on('typeahead:asyncrequest', function(data) {
            // https://github.com/twitter/typeahead.js/issues/166
            $('.pending-message').show();
        }).on('typeahead:asynccancel typeahead:asyncreceive', function() {
            $('.pending-message').hide();
        }).on('typeahead:selected', function(evt, data) {
    	 // defines the event 'onclick'
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



/**
 * Helper function which returns the higher value of the document height.
 * @param {Object} doc 
 * @return {Number} height
 */
function getDocHeight(doc) {
    doc = doc || document;
    // stackoverflow.com/questions/1145850/
    var body = doc.body, html = doc.documentElement;
    var height = Math.max( body.scrollHeight, body.offsetHeight, 
        html.clientHeight, html.scrollHeight, html.offsetHeight );
    return height;
}

/**
 * Defines the height of the iframe in the onload event.
 * @param {String} subject
 * @return None
 */
function load_iframe(subject){
	var iframe = window.parent.document.getElementById("b2note_iframe");
	var doc = iframe.contentDocument? iframe.contentDocument: 
        iframe.contentWindow.document;
	iframe.style.visibility = 'hidden';
	iframe.style.height = "10px"; // reset to minimal height ...
	// IE opt. for bing/msn needs a bit added or scrollbar appears
	iframe.style.height = getDocHeight( doc ) + 4 + "px";
	iframe.style.visibility = 'visible';
	iframe.subject_tofeed=subject;
}

/**
 * Shows the iframe.
 * @return None
 */
function show_iframe() {
	window.parent.document.getElementById('b2note_iframe').style.visibility = "visible";
	window.parent.document.getElementById('b2note_iframe').style.width = "350px";
	window.parent.document.getElementById('b2note_iframe').style.border = "2px solid gray";
}

// http://stackoverflow.com/questions/6754935/how-to-close-an-iframe-within-iframe-itself
/**
 * Hides the iframe.
 * @return None
 */
function hide_iframe() {
	window.parent.document.getElementById('b2note_iframe').style.width = "0px";
	window.parent.document.getElementById('b2note_iframe').style.border = "0px";
	window.parent.document.getElementById('b2note_iframe').style.visibility = "hidden";
}

/**
 * Get the free text when creating a annotation
 * 
 */
function get_free_text() {
    var text = document.getElementById("free-text").value;
    var elem = document.getElementById("section_subject");
    var subject = "";
    if (elem) {
        subject = elem.getElementsByTagName("a")[0].innerHTML;
    }
    // abremaud@esciencefactory.com, 20160129
    // gets the pid selected to provide the pid_tofeed field
    var pid = "test";
    if (elem) {
        pid = elem.getElementsByTagName("a")[1].innerHTML;
    }

    if (document.getElementById("section_subject")) {
        $.redirect('create_annotation',
            {
               free_text: text,
               subject_tofeed: subject,
               pid_tofeed: pid,
               // abremaud@esciencefactory.com, 20160926
               // retrieve Django csrf token from html hidden input element
               csrfmiddlewaretoken: document.getElementById('free-text').parentElement.firstChild.nextSibling.value,
            });
    }
}
/*
* Give a different css class to the button corresponding to the file we're currently annotating.
*
*/
$(document).ready( function() {
    if(document.getElementById('button1')) {
        document.getElementById('button1').classList.add('activated');
        last_id = 'button1'
        var reply_click = function(){
            if (last_id){
                document.getElementById(last_id).classList.remove('activated');
            }
            document.getElementById(this.id).classList.add('activated');
            last_id = this.id
        }
        n = 1
        id = 'button'+ n
        while (document.getElementById(id)){
            document.getElementById(id).onclick = reply_click;
            n = n + 1;
            id = 'button' + n;
        }
    }
});

/*
* Add a refresh button to captchas
* https://stackoverflow.com/questions/18972515/how-to-create-ajax-refresh-for-django-simple-captcha
*/
$(function() {
    // Add refresh button after field (this can be done in the template as well)
    /*
    $('img.captcha').after(
            $('<br><a href="#void" id="captcha-refresh-button" class="captcha-refresh">Refresh</a>')
    );
    */

    // Click-handler for the refresh-link
    $('.captcha-refresh').click(function(){
        var $form = $(this).parents('form');
        var url = location.protocol + "//" + window.location.hostname + ":"
                  + location.port + "/captcha/refresh/";

        // Make the AJAX-call
        $.getJSON(url, {}, function(json) {
            $form.find('input[name="captcha_0"]').val(json.key);
            $form.find('img.captcha').attr('src', json.image_url);
        });

        return false;
    });
});

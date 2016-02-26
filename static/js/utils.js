

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

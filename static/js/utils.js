

// Defines the height of the iframe in the onload event
function load_iframe(subject){
	elem = document.getElementById("b2note_iframe");
	elem.style.height = (elem.contentWindow.document.body.scrollHeight) + 'px';
	elem.subject_tofeed=subject;
}

function show_iframe() {
	window.parent.document.getElementById('b2note_iframe').style.visibility="visible";
}

// http://stackoverflow.com/questions/6754935/how-to-close-an-iframe-within-iframe-itself
function hide_iframe() {
	window.parent.document.getElementById('b2note_iframe').style.visibility="hidden";
}

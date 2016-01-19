

$( document ).ready( function () {
	$( ".delAnnotation" ).on( 'click', function ( event ) {
		console.log("DELETE ANNOTATION");
		event.preventDefault();
		
		var row = $(this).closest("tr");        // Finds the closest row <tr> 
	    	var tds = row.find("td:nth-child(2)"); // Finds the 2nd <td> element
		console.log(tds);
		$.post( "interface_main", { iri : tds }, function ( json ) {

		} );
	} );
} );

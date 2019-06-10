import * as jsonld from 'jsonld';
//import {Readable} from 'stream'
//import {Parser} from '@rdfjs/parser-jsonld'

export class Download {

  constructor() {
    this.content = "[{ }]";
    this.contenttypes = ["All annotations about the file", "All my annotations"];
    this.contenttype = this.contenttypes[0];
  }

  activate() {
    this.showcontent = false;
  }

  downloadAllMyAnnotations() {
    this.contenttype = this.contenttypes[0];
    this.showcontent = true;
    //TODO do api call to get content
    this.content = `
  [
  {
    "@context": "https://b2note.bsc.es/jsonld_context_b2note_20161027.jsonld", 
    "id": "https://b2note.bsc.es/annotations/5b92a7a3af03423b8b27ed8f", 
    "type": "Annotation", 
    "target": {
      "id": "http://hdl.handle.net/0000/92183b2573c344bc8cfe53516c255534", 
      "type": "SpecificResource", 
      "source": "https://trng-b2share.eudat.eu/api/files/afa302cd-4f46-499e-a09e-b502d233e45d/01-explore-patient-table.ipynb"
    }, 
    "body": {
      "type": "Composite", 
      "purpose": "tagging", 
      "items": [
        {
          "type": "SpecificResource", 
          "source": "http://purl.obolibrary.org/obo/WBbt_0004385"
        }, 
        {
          "type": "SpecificResource", 
          "source": "http://edamontology.org/format_1476"
        }, 
        {
          "type": "TextualBody", 
          "value": "PDB"
        }
      ]
    }, 
    "motivation": "tagging", 
    "creator": {
      "type": "Person", 
      "nickname": "tomaskulhanek"
    }, 
    "generator": {
      "type": "Software", 
      "homepage": "https://b2note.bsc.es", 
      "name": "B2Note v1.0"
    }, 
    "created": "2018-09-07T06:30:27.394000", 
    "generated": "2018-09-07T16:30:27.436000"
  }
  ]`;
    this.createJson();
    this.createRdf();
  }

  downloadAnnotationsAboutFile() {
    this.contenttype = this.contenttypes[1];
    this.showcontent = true;
    //TODO do api call to get content
    this.content = `
  [
  {
    "@context": "https://b2note.bsc.es/jsonld_context_b2note_20161027.jsonld", 
    "id": "https://b2note.bsc.es/annotations/5b92a7a3af03423b8b27ed8f", 
    "type": "Annotation", 
    "target": "http://hdl.handle.net/0000/92183b2573c344bc8cfe53516c255534", 
    "body": "http://purl.obolibrary.org/obo/WBbt_0004385",
    "motivation": "tagging", 
    "creator": {
      "type": "Person", 
      "nickname": "tomaskulhanek"
    }, 
    "generator": {
      "type": "Software", 
      "homepage": "https://b2note.bsc.es", 
      "name": "B2Note v1.0"
    }, 
    "created": "2018-09-07T06:30:27.394000", 
    "generated": "2018-09-07T16:30:27.436000"
  }
  ]`
    this.createJson();
    this.createRdf();
  }

  createJson() {
    let data = new Blob([this.content], {type: 'application/json'});
    this.jsonurl = window.URL.createObjectURL(data);
  }

  /* @rdfjs/json-ld-parser - seems to produce error (Parser is not constructor
  TypeError: _rdfjs_parser_jsonld__WEBPACK_IMPORTED_MODULE_1__.ParserJsonld is not a constructor
  createRdf() {

    // create JSON-LD parser instance
    this.rdf = "";
    //let mydebugparser = Parser;
    let parserJsonld = new Parser()
    let input = new Readable({
      read: () => {
        input.push(this.content)
        input.push(null)
      }
    })

    let output = parserJsonld.import(input)

    output.on('data', quad => {
      this.rdf = quad.toString()
    });
    let datardf = new Blob([this.rdf], {type: 'application/rdf+xml'});
    this.rdfurl = window.URL.createObjectURL(data);


  }*/

  createRdf(){
// serialize a document to N-Quads (RDF)
    this.rdf="";
    let doc = JSON.parse(this.content);
    jsonld.toRDF(doc, {format: 'application/nquads'}, (err, nquads) => {
      this.rdf+=nquads;// nquads is a string of N-Quads
      console.log('got nquads',nquads,err)
      let data = new Blob([this.rdf], {type: 'application/nquads'});
      this.rdfurl = window.URL.createObjectURL(data);
    });


  }
}

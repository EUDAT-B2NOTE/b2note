/**
 * implements Download page and it's functionality
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import * as jsonld from 'jsonld';
import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Download {

  constructor(api) {
    this.api=api;
    this.rawcontent = "[{ }]";
    this.content=[]
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
    this.api.getAllMyAnnotations()
      .then(data => {
        this.content = data._items;
        this.rawcontent = JSON.stringify(this.content,null,4);
        this.createJson();
        this.createRdf();
      });

  }

  downloadAnnotationsAboutFile() {
    this.contenttype = this.contenttypes[1];
    this.showcontent = true;
    //TODO do api call to get content
    this.api.getAllAnnotations()
      .then(data => {
        this.content = data._items;
        this.rawcontent = JSON.stringify(this.content,null,4);
        this.createJson();
        this.createRdf();
      });  }

  createJson() {
    //let rawcontent = JSON.stringify(this.content)
    let data = new Blob([this.rawcontent], {type: 'application/json'});
    this.jsonurl = window.URL.createObjectURL(data);
  }

  //TODO implement RDF/XML conversion - jsonld seems to support only RDF/NQuads
  createRdf(){
// serialize a document to N-Quads (RDF)
    this.rdf="";
    let doc = this.content;
    jsonld.toRDF(doc, {format: 'application/nquads'}, (err, nquads) => {
      this.rdf+=nquads;// nquads is a string of N-Quads
      console.log('got nquads',nquads,err)
      let data = new Blob([this.rdf], {type: 'application/nquads'});
      this.rdfurl = window.URL.createObjectURL(data);
    });


  }
}

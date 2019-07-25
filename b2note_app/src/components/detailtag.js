/**
 * Detail information about annotation tag, including browsable list of classes and details of classes used in annotation
 * The details of classes are obtained from SOLR index.
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';
import {bindable} from 'aurelia-framework';
import {EventAggregator} from 'aurelia-event-aggregator';
import {Taginfo,Updateall,Updatefile} from "./messages";

@inject(AnnotationApi, EventAggregator)
export class Detailtag {
  @bindable id;

  constructor(api, ea) {
    this.api = api;
    this.ea = ea;
    this.showtaginfo = false;
    this.classes = [{}]
    this.class = {}
    //this.hasfocus = false;
  }

  attached() {
    this.showtaginfo = false;
    this.s1 = this.ea.subscribe(Taginfo, msg => this.changeTagInfo(msg.taginfo));
  }

  detached() {
    this.s1.dispose();
  }

  changeTagInfo(taginfo) {
    //
    if (taginfo.domid === this.id) { //taginfo is addressed to this instance
      //visualize
      if (taginfo.mode === 'show') {
        console.log('Detailtag.changeTagInfo() taginfo.body', taginfo.body);
        this.taginfo = taginfo;
        this.tagtitle = this.taginfo.body.value;
        this.showtaginfo = true;
        let ontologies = [];
        //get the detail information about ontologies used in the annotation body.items
        if (this.taginfo.body.items && (this.taginfo.body.items.length > 0)) {
          //collect just ontologies reffered
          for (let item of this.taginfo.body.items) {
            if (item.source && (item.source.length > 0)) ontologies.push(item.source)
          }
          //get the detail information from SOLR index
          this.api.getOntologies(ontologies)
            .then(data => {
              console.log('changetaginfo() data:', data);
              //result may contain repeated uris - SOLR index has duplicates
              //deduplicate
              let oset = new Set();
              let oaggr = []
              for (let doc of data.response.docs) {
                if (!oset.has(doc.uris)) {
                  oset.add(doc.uris)
                  oaggr.push(doc);
                }
              }
              console.log('changetaginfo() oaggr:', oaggr);
              //now oaggr contains information about ontologies
              //return oaggr;
              if (oaggr.length > 0) {
                this.classes = oaggr;
                this.class = oaggr[0];
                this.class.isfocused = true;
                this.classindex = 1;
                this.classlength = oaggr.length;
              }
              //scroll into view
              this.detailtagref.scrollIntoView()
            })
        }
        //this.tagtitle=taginfo.tagvalue;
      } else if (taginfo.mode === 'edit') {
        this.taginfo = taginfo;
        this.showtaginfo=true;
        this.tagtitle = this.taginfo.body.value;
        //set default mode - tag, then check whether keyword or comment
        this.active='tab1';
        if (this.taginfo.body.purpose === 'tagging'){
          if (this.taginfo.body.type === "TextualBody") this.active = 'tab2'; //Keyword
          else this.active='tab1';//Semantic
        } else if(this.taginfo.body.purpose ==='commenting') this.active='tab3'; //Comment

        this.annotationsemantic=this.annotationkeyword=this.annotationcomment=''; //
      } else if (taginfo.mode === 'remove'){
        this.taginfo=taginfo;
        this.showtaginfo=true;
        this.tagtitle = this.taginfo.body.value;
      }
    }
  }

  switch(myclass) {
    if (this.class.isfocused) this.class.isfocused=false;
    this.class = myclass;
    this.classindex=this.classes.indexOf(this.class)+1;
    this.class.isfocused=true;
    //this.classindex=this.classes.indexOf(this.class);
  }
  switchprev(){
    if (this.class.isfocused) this.class.isfocused=false;
    let myindex= this.classes.indexOf(this.class);
    if (myindex>0) {this.class=this.classes[myindex-1];this.classindex=myindex}
    this.class.isfocused=true;
  }
  switchnext(){
    if (this.class.isfocused) this.class.isfocused=false;
    let myindex= this.classes.indexOf(this.class)+1;
    if (myindex<this.classes.length) {this.classindex=myindex+1;this.class=this.classes[myindex];}
    this.class.isfocused=true;
  }

  deleteAnnotation(){
    this.api.deleteAnnotation(this.taginfo)
      .then(response=>{
        console.log('deleteAnnotation() then response',response)
        this.taginfo.mode="ackremove";
        if (response.ok) this.tagtitle="Annotation was deleted. ";
        else this.tagtitle="Error occured during deletion. HTTP status:"+response.status+" text:"+response.statusText;
        this.api.incAllAnnotationsSemantic();
        this.api.incAllAnnotationsKeyword();
        this.api.incAllAnnotationsComment();
      })
      .catch(response=>{
        console.log('deleteAnnotation() catch response',response)
        this.tagtitle="Error occured during deletion. HTTP status:"+response.status+" text:"+response.statusText;
        this.taginfo.mode="ackremove"
      })
  }

  cancelDeleteAnnotation(){
    this.showtaginfo=false;
  }

  ok(){
    this.showtaginfo=false;
    this.taginfo.mode="";
    if (this.id==='my') this.ea.publish(new Updateall(this.taginfo));
    else this.ea.publish(new Updatefile(this.taginfo));
  }

  createSemantic(){
    let annotation=Object.assign({},this.taginfo);
    //remove properties added by VM
    delete annotation.mode;
    delete annotation.domid;
    delete annotation.target.items;
    delete annotation.body;
    //delete annotation.body.value;
    let anvalue = this.api.getAnnotationItems(this.annotationsemantic);
    annotation.body= {
          'type': 'Composite',
          'purpose': 'tagging',
          'items': anvalue
        }
    this.putAnnotation(annotation);
    this.api.incAllAnnotationsSemantic();
  }
  createKeyword(){
    let annotation=Object.assign({},this.taginfo);
    //remove properties added by VM
    delete annotation.mode;
    delete annotation.domid;
    delete annotation.target.items;
    delete annotation.body;
    //delete annotation.body.value;
    //let anvalue = this.api.getAnnotationItems(this.annotationsemantic);
    annotation.body= {
            'type': 'TextualBody',
            'value': this.annotationkeyword,
            'purpose': "tagging"
          }
    this.putAnnotation(annotation);
    this.api.incAllAnnotationsKeyword();
  }

  createComment(){
  let annotation=Object.assign({},this.taginfo);
    //remove properties added by VM
    delete annotation.mode;
    delete annotation.domid;
    delete annotation.target.items;
    delete annotation.body;
    //delete annotation.body.value;
    //let anvalue = this.api.getAnnotationItems(this.annotationsemantic);
    annotation.body={
            'type': 'TextualBody',
            'value': anvalue,
            'purpose': "commenting"
          }
    this.putAnnotation(annotation);
    this.api.incAllAnnotationsComment();

  }

  putAnnotation(annotation) {
    this.api.putAnnotation(annotation)
      .then(data => {
        //this.anid = data._id;
        //this.showform = false; this.showack=true;
        //this.annotation = data;
        this.annotationtext = JSON.stringify(data, null, 2);
        this.taginfo.mode="ackmodify";
        this.tagtitle="Annotation was modified. ";
        //this.ea.publish(new Updateall(this.annotation));
        //this.ea.publish(new Updatefile(this.annotation));
      })
      .catch(error => {
        alert('Error while creating annotation. It was not created\n\nHTTP status:' + error.status + '\nHTTP status text:' + error.statusText);
      })
  }


  //TODO -refactor - copy of home.js getsuggestions
    getSuggestions(value) {
        return this.api.getOntologySuggestions(value)
          .then(data =>{
            return data;
          })
    }

}

/**
 * Detail information about annotation tag
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
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
        console.log('detailtag mode edit tag:',taginfo)
        this.taginfo = taginfo;
        this.showtaginfo=true;
        this.tagtitle = this.taginfo.body.value;
        this.active = this.taginfo.body.purpose === 'tagging' ? 'tab1' : 'tab3'; //Semantic or Comment
        if (this.taginfo.body.type == "TextualValue") this.active = 'tab2'; //Keyword
        this.annotationsemantic=this.annotationkeyword=this.annotationcomment=''; //
      } else if (taginfo.mode === 'remove'){
        console.log('detailtag mode remove tag:',taginfo);
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

  }
  createKeyword(){

  }
  createComment(){

  }

}

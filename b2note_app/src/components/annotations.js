/**
 * Annotattion component with accordion to show overview about existing annotations
 * @todo render table with annotation numbers
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {AnnotationApi} from '../components/annotationapi';
import {EventAggregator} from 'aurelia-event-aggregator';
import {inject} from 'aurelia-framework';
import {Taginfo} from "./messages";

@inject(AnnotationApi,EventAggregator)
export class Annotations {
  constructor(api,ea) {
    this.api=api;
    this.ea=ea;
    this.showall = false;
    this.showfile = false;
    this.file = {};
    this.file.semantic=[];
    this.file.keyword=[];
    this.file.comment=[];
    this.file.tags=this.file.semantic;//reference
    this.my = {};
    this.my.semantic=[];
    this.my.keyword=[];
    this.my.comment=[];
    this.my.tags=this.my.semantic;//reference
    this.showmydetail=false;
    this.showfiledetail=false;

  }

  switchAll() {
    this.showall = !this.showall;
    if (this.showfile) this.showfile=false;
    //if (this.my.semantic.length==0) {
      this.api.getAllMyAnnotationsSemantic()
        .then(data=>{
          this.my.semantic=data._items;
        })
    //}
    //if (this.my.keyword.length==0) {
      this.api.getAllMyAnnotationsKeyword()
        .then(data=>{
          this.my.keyword=data._items;
        })
    //}
    //if (this.my.comment.length==0) {
      this.api.getAllMyAnnotationsComment()
        .then(data=>{
          this.my.comment=data._items;
        })
    //}
  }

  switchFile() {
    this.showfile = !this.showfile;
    if (this.showall) this.showall=false;
    //if (this.file.semantic.length==0) {
      this.api.getAllAnnotationsFileSemantic()
        .then(data=>{
          this.file.semantic=data._items;
        })
    //}
    //if (this.file.keyword.length==0) {
      this.api.getAllAnnotationsFileKeyword()
        .then(data=>{
          this.file.keyword=data._items;
        })
    //}
    //if (this.file.comment.length==0) {
      this.api.getAllAnnotationsFileComment()
        .then(data=>{
          this.file.comment=data._items;
        })
    //}
  }

  //sets values of tags through array to find TextualValue and set it
  setvalue(tags){
    for (let tag of tags) {
      if (tag.body.items && tag.body.items.length>0) tag.body.value=tag.body.items[tag.body.items.length-1].value
      else
        if (tag.body.source) tag.body.value=tag.body.source;

    }
    console.log('Annotations, tags',tags)
  }

  showMySemantic(){
    this.showmydetail=true;
    this.showmytitle="Semantic"
    this.my.tags=this.my.semantic;
    this.setvalue(this.my.tags)
  }
  showMyKeyword(){
    this.showmydetail=true;
    this.showmytitle="Free-text keyword"
    this.my.tags=this.my.keyword;
  }
  showMyComment(){
    this.showmydetail=true;
    this.showmytitle="Comment"
    this.my.tags=this.my.comment;
  }
  showFileSemantic(){
    this.showfiledetail=true;
    this.showfiletitle="Semantic"
    this.file.tags=this.file.semantic;
    this.setvalue(this.file.tags)
  }
  showFileKeyword(){
    this.showfiledetail=true;
    this.showfiletitle="Free-text keyword"
    this.file.tags=this.file.keyword;
  }
  showFileComment(){
    this.showfiledetail=true;
    this.showfiletitle="Comment"
    this.file.tags=this.file.comment;
  }

  showdetail(tag,domid){
    let taginfo = tag;
    taginfo.domid=domid;
    taginfo.mode='show';
    this.ea.publish(new Taginfo(taginfo));
  }
  edittag(tag,domid){
    let taginfo = tag;
    taginfo.domid=domid;
    taginfo.mode='edit';
    this.ea.publish(new Taginfo(taginfo));

  }
  removetag(tag,domid){
    let taginfo = tag;
    taginfo.domid=domid;
    taginfo.mode='remove';
    this.ea.publish(new Taginfo(taginfo));
  }

}

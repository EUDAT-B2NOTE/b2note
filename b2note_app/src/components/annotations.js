/**
 * Annotattion component with accordion to show overview about existing annotations
 * @todo render table with annotation numbers
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Annotations {
  constructor(api) {
    this.api=api;
    this.showall = false;
    this.showfile = false;
    this.file = {};
    this.file.semantic=[];
    this.file.keyword=[];
    this.file.comment=[];
    this.my = {};
    this.my.semantic=[];
    this.my.keyword=[];
    this.my.comment=[];

  }

  switchAll() {
    this.showall = !this.showall;
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
}

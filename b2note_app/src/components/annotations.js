/**
 * Annotation component with accordion to show overview about existing annotations
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import {AnnotationApi} from '../components/annotationapi';
import {EventAggregator} from 'aurelia-event-aggregator';
import {inject} from 'aurelia-framework';
import {Taginfo, Updateall, Updatefile} from "./messages";

@inject(AnnotationApi, EventAggregator)
export class Annotations {
  constructor(api, ea) {
    this.api = api;
    this.ea = ea;
    this.showall = false;
    this.showfile = false;
    this.file = {};
    this.file.semantic = [];
    this.file.keyword = [];
    this.file.comment = [];
    this.file.tags = this.file.semantic;//reference
    this.my = {};
    this.my.semantic = [];
    this.my.keyword = [];
    this.my.comment = [];
    this.my.tags = this.my.semantic;//reference
    this.showmydetail = false;
    this.showfiledetail = false;
  }

  /**
   * subscribe to notification about changes in annotations
   */
  attached() {
    this.s1 = this.ea.subscribe(Updateall, msg => this.updateAll());
    this.s2 = this.ea.subscribe(Updatefile, msg => this.updateFile());
  }

  detached() {
    this.s2.dispose();
    this.s1.dispose();
  }

  /**
   * switch view to All My Annotation
   */
  switchAll() {
    this.showall = !this.showall;
    if (this.showfile) this.showfile = false;
    this.updateAll();
  }

  updateAll() {
    this.showmydetail = false;
    if (this.showall) {
      this.api.getAllMyAnnotationsSemantic()
        .then(data => {
          this.my.semantic = data._items;
        })
      this.api.getAllMyAnnotationsKeyword()
        .then(data => {
          this.my.keyword = data._items;
        })
      this.api.getAllMyAnnotationsComment()
        .then(data => {
          this.my.comment = data._items;
        })
    }
  }

  /**
   * Switch view to 'Annotation about this file'
   */
  switchFile() {
    this.showfile = !this.showfile;
    if (this.showall) this.showall = false;
    this.updateFile();
  }

  updateFile() {
    this.showfiledetail = false;
    if (this.showfile) {
      this.api.getAllAnnotationsFileSemantic()
        .then(data => {
          this.file.semantic = data._items;
        })
      this.api.getAllAnnotationsFileKeyword()
        .then(data => {
          this.file.keyword = data._items;
        })
      this.api.getAllAnnotationsFileComment()
        .then(data => {
          this.file.comment = data._items;
        })
    }

  }

  /**
   * sets values of tags through array to find TextualValue (last item) and set it
   * @param tags
   */
  setvalue(tags) {
    for (let tag of tags) {
      if (tag.body.items && tag.body.items.length > 0) tag.body.value = tag.body.items[tag.body.items.length - 1].value
      else if (tag.body.source) tag.body.value = tag.body.source;
    }
    console.log('Annotations, tags', tags)
  }


  /**
   * Aggregates annotation tags per the body value, multiple targets per the body are in target.items array
   * @param tags
   * @returns {Array}
   */
  aggregatePerBody(tags) {
    let tagset = {} // set of body values
    let newtags = []
    for (let tag of tags) {
      this.checkAnnotationV1V2(tag)
      //add body value
      if (!tag.body.hasOwnProperty('value')) { // set body value from body.items[last] - or from body.source
        if (tag.body.items && tag.body.items.length > 0) tag.body.value = tag.body.items[tag.body.items.length - 1].value
        else if (tag.body.source) tag.body.value = tag.body.source;
      }
      if (tagset.hasOwnProperty(tag.body.value)) {
        //adds target to existing
        //console.log('aggregatePerBody() adding target to existing body [body.value,target, index-tagset[body.value])',tag.body.value,tag.target,tagset);
        newtags[tagset[tag.body.value]].target.items.push(tag.target)
      } else {
        //creates newtag
        let index = newtags.push(tag) - 1;
        tagset[tag.body.value] = index;
        //console.log('aggregatePerBody() creating target to existing body [body.value,target, index-tagset[body.value])',tag.body.value,tag.target,tagset);
        newtags[tagset[tag.body.value]].target.items = [];
        newtags[tagset[tag.body.value]].target.items.push(tag.target)
      }
    }
    return newtags;
  }

  repair(tags) {
    let newtags = []
    for (let tag of tags) {
      this.checkAnnotationV1V2(tag);
      newtags.push(tag)
    }
    return newtags;
  }

  clean(myObj) {
    Object.keys(myObj).forEach((key) => (myObj[key] == null) && delete myObj[key]);
  }

  flatten(tag, prop) {
    if (Array.isArray(tag[prop])) {
      //copy first element of array
      let mb = tag[prop].slice();
      let myObj = mb[0];
      //clean the element from null values
      Object.keys(myObj).forEach((key) => (myObj[key] == null) && delete myObj[key]);
      //replace array with cleaned obj
      tag[prop] = myObj;
      //show warning if more elements are in array
      if (mb.length > 1) console.log("Annotations.checkAnnotationV1V2() warning: more " + prop + " per annotations. tag,mb:", tag, mb)
    }
  }


  checkAnnotationV1V2(tag) {
    //BI-39 workaround, set body record from body[0] - body[0] from b2note v1.0
    this.flatten(tag,"body")
    this.flatten(tag,"target")
    this.flatten(tag,"motivation")
    this.flatten(tag,"generator")
    this.flatten(tag,"creator")
    if (!tag.target.hasOwnProperty('id') && tag.target.hasOwnProperty('jsonld_id')) tag.target.id = tag.target.jsonld_id
  }

  showMySemantic() {
    this.showmydetail = true;
    this.showmytitle = "Semantic"
    this.my.tags = this.aggregatePerBody(this.my.semantic);
  }

  showMyKeyword() {
    this.showmydetail = true;
    this.showmytitle = "Free-text keyword"
    this.my.tags = this.aggregatePerBody(this.my.keyword);
  }

  showMyComment() {
    this.showmydetail = true;
    this.showmytitle = "Comment"
    this.my.tags = this.repair(this.my.comment);
  }

  showFileSemantic() {
    this.showfiledetail = true;
    this.showfiletitle = "Semantic"
    this.file.tags = this.aggregatePerBody(this.file.semantic);

  }

  showFileKeyword() {
    this.showfiledetail = true;
    this.showfiletitle = "Free-text keyword"
    this.file.tags = this.aggregatePerBody(this.file.keyword);
  }

  showFileComment() {
    this.showfiledetail = true;
    this.showfiletitle = "Comment"
    this.file.tags = this.repair(this.file.comment);
  }

  showdetail(tag, domid) {
    let taginfo = tag;
    taginfo.domid = domid;
    taginfo.mode = 'show';
    this.ea.publish(new Taginfo(taginfo));
  }

  edittag(tag, domid) {
    let taginfo = tag;
    taginfo.domid = domid;
    taginfo.mode = 'edit';
    this.ea.publish(new Taginfo(taginfo));

  }

  removetag(tag, domid) {
    let taginfo = tag;
    taginfo.domid = domid;
    taginfo.mode = 'remove';
    this.ea.publish(new Taginfo(taginfo));
  }

}

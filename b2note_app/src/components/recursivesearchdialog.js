/**
 * Recursive Search Dialog - variant for UX to construct search query
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */
import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Recursivesearchdialog {
  constructor(api) {
    this.tabs = [
      {id: 'semantic', label: 'Semantic annotation'},
      {id: 'keyword', label: 'Free-text keywords'},
      {id: 'comment', label: 'Comment           '}
    ];
    this.active = 'semantic';
    this.annotationsemantic = '';
    this.annotationkeyword = '';
    this.annotationcomment = '';
    this.api = api;
    this.child = false;
    this.logic = 'AND';
  }

  switchtab(tabid) {
    this.active = tabid;
    return true;
  }

  createSemantic() {
    console.log('create semantic:', this.annotationsemantic)
  }

  createKeyword() {
    console.log('create keyword:', this.annotationkeyword)

  }

  createComment() {
    console.log('create semantic:', this.annotationcomment)
  }

  search() {
    console.log('search', this.active);
    let queryitem = this.getQueryitem();
    //if the last item is not empty or is explicitly set to 'comment' type then add it to query items
    if ((queryitem.value !== '') || (queryitem.type == 'comment'))
      this.api.pushQueryitem(queryitem);
    this.api.searchQuery();
  }

  getQueryitem() {
    this.searchvalue = this.active === 'semantic' ? this.annotationsemantic :
      (this.active === 'keyword' ? this.annotationkeyword : '');
    this.searchtype = this.active;
    //create queryitem record with logic operator, type and value from dialog
    return {logic: this.logic, type: this.searchtype, value: this.searchvalue}

  }

  modify() {
    let queryitem = this.getQueryitem();
    this.api.modifyQueryitem(this.index, queryitem);
  }

  createChild() {
    console.log('creating child');


    let queryitem = this.getQueryitem();

    this.index = this.api.pushQueryitem(queryitem) ;

    this.child = true;
  }

  deleteChild() {
    console.log('deleting child');
    this.api.deleteQueryitem(this.index);
    this.child = false;
  }

}

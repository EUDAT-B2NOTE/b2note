import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Arraysearchdialog {
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
    this.query=[];
    this.logic='AND';
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

  //TODO refactor to use api.query instead of this.query
  search(){
    console.log('search',this.active);
    //based on active tab show return appropriate value
    this.searchvalue = this.active === 'semantic'? this.annotationsemantic:
      (this.active === 'keyword'? this.annotationkeyword: '');
    this.searchtype = this.active;
    let queryitem = {logic:this.query.length === 0?'':this.logic, type:this.searchtype,value:this.searchvalue}
    if (queryitem.value!=='') this.query.push(queryitem);

    this.api.searchQuery(this.query);
  }

  createChild(){
    //determine the query value based on current tab
    this.searchvalue = this.active === 'semantic'? this.annotationsemantic:
    (this.active === 'keyword'? this.annotationkeyword: '');
    this.searchtype = this.active;
    //create queryitem record with logic operator, type and value from dialog
    let queryitem = {logic:this.query.length === 0?'':this.logic, type:this.searchtype,value:this.searchvalue}
    this.query.push(queryitem);
    //reset dialog values
    this.active='semantic';
    this.annotationsemantic=this.annotationkeyword=this.annotationcomment='';
    console.log('creating child');
    this.child = this.query.length > 0;
  }

  deleteChild(){
    console.log('deleting child');
    let queryitem = this.query.pop()
    this.active = queryitem.type;
    console.log('deleteChild(), active: queryitem:',this.active,queryitem.logic,queryitem.type,queryitem.value)
    this.annotationsemantic=this.annotationkeyword=this.annotationcomment='';
    if (this.active==='semantic') this.annotationsemantic=queryitem.value;
    if (this.active==='keyword') this.annotationkeyword=queryitem.value;
    this.child = this.query.length > 0;
  }

}

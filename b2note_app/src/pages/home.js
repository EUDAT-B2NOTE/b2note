/**
 * implements Home page - Creation of annotation and browsing annotation details
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import {AnnotationApi} from '../components/annotationapi';
import {EventAggregator} from 'aurelia-event-aggregator';
import {inject} from 'aurelia-framework';
import {Updateall,Updatefile} from '../components/messages';


@inject(AnnotationApi,EventAggregator)
export class Home {
/*  private tabs:Tab[];
  private active:string;
  annotationsemantic:string;
  annotationkeyword:string;
  annotationcomment:string
  anid:string;
  showform:boolean
  showack:boolean
  showfirstlogin:boolean;
  manualtarget:boolean;
  userinfo;
  enablecreate:boolean;
  private annotation: any;
  private annotationtext: string;
*/

  constructor(api,ea) {
    this.api = api;
    this.ea=ea;
    this.tabs = [
      {id: 'tab1', label: 'Semantic annotation'},
      {id: 'tab2', label: 'Free-text keywords'},
      {id: 'tab3', label: 'Comment           '}
    ];
    this.active = 'tab1';
    this.annotationsemantic = '';
    this.annotationkeyword = '';
    this.annotationcomment = '';
    this.anid = '';
    this.showform = true; this.showack=false; this.showfirstlogin=false;this.confirmkeyword=false;
    this._availableItems = ["strychnine","glycine","strasdf","glcsdf"];//items;
    this.selectedItem = null;
    this.selectedItems = [];// [items[Math.floor(Math.random() * 1000)], items[Math.floor(Math.random() * 1000)]];
    this.keywordterms=0;
    //console.log('Home()')
  }
  
  attached() {
    //console.log('Home.attached()')
    this.api.homeattached=true;
    //this.manualtarget = this.api.getManualTarget();
    this.api.getUserInfo()
      .then(data => {
        //this.api.userinfo = data
        this.enablecreate = this.api.userinfo.id.length>0;
      })
      .catch(error => { //do nothing or alert
        })
    ;
  }

  activate(params, routeConfig, navigationInstruction){
    //parses params in url in form http://localhost/b2note/#/b2note_home/id=https:/someurl/sdf&source=http://someurl&type=SpecificResource
    if (params.target) {
      console.log('home activate()',params.target)
      let kv = params.target.split('&');
      for (let kvitem of kv) {
        let keyvalue = kvitem.split('=');
        if (keyvalue[0]==='id') this.api.target.id=keyvalue[1];
        if (keyvalue[0]==='source') this.api.target.source=keyvalue[1];
        if (keyvalue[0]==='type') this.api.target.type=keyvalue[1];
       // console.log('api target',this.api.target);
      }
    } else {
      //no params = send message to potential window opener - listener in login.js which closes the popup
      if (window.opener) window.opener.postMessage('b2note home opened', "*");
    }

  }

  switchtab(tabid) {
    this.active = tabid;
    return true;
  }

  createSemantic() {
    console.log('create semantic:', this.annotationsemantic);
    let anvalue = this.api.getAnnotationItems(this.annotationsemantic);
    //  let userinfo = data;
      let datetime = new Date();
      let annotation = {
        '@context': 'http://www.w3.org/ns/anno/jsonld',
        'id': '',
        'type': 'Annotation',
        'body': {
          'type': 'Composite',
          'purpose': 'tagging',
          'items': anvalue
        },
        'target': {
          'id': this.api.target.id,
          'type': this.api.target.type,
          'source': this.api.target.source
        },
        'motivation': 'tagging',
        'creator': {
          'id':this.api.userinfo.id,
          'type': 'Person',
          'nickname': this.api.userinfo.pseudo
        },
        'generator': {
          'type': 'Software',
          'homepage': window.location.protocol+'//'+window.location.host+window.location.pathname,
          'name': 'B2Note v2.0'
        },
        'created': datetime.toISOString(),
        'generated': datetime.toISOString()
      };
      this.postAnnotation(annotation);
      this.api.incAllAnnotationsSemantic();

  }

  postAnnotation(annotation) {
    this.api.postAnnotation(annotation)
      .then(data => {
        this.anid = data._id;
        this.showform = false; this.showack=true;
        this.annotation = data;
        this.annotationtext = JSON.stringify(data, null, 2);
        this.ea.publish(new Updateall(this.annotation));
        this.ea.publish(new Updatefile(this.annotation));
        //return data;
      })
      .catch(error => {
        alert('Error while creating annotation. It was not created\n\nHTTP status:' + error.status + '\nHTTP status text:' + error.statusText);
      })
  }

  closeackn() {
    this.showform = true; this.showack=false; this.showfirstlogin=false;
  }
  closeprofile() {
    this.closeackn();
  }

  showfirstloginfn(){
    this.showform = false; this.showack=false; this.showfirstlogin=true;
  }

  createKeyword() {
    console.log('create keyword:', this.annotationkeyword);
    let anvalue = this.annotationkeyword;
        let datetime = new Date();
        let annotation = {
          '@context': 'http://www.w3.org/ns/anno/jsonld',
          'id': '',
          'type': 'Annotation',
          'body': {
            'type': 'TextualBody',
            'value': anvalue,
            'purpose': "tagging"
          },
          'target': {
            'id': this.api.target.id,
            'type': this.api.target.type,
            'source': this.api.target.source
          },
          'motivation': 'tagging',
          'creator': {
            'id':this.api.userinfo.id,
            'type': 'Person',
            'nickname': this.api.userinfo.pseudo
          },
          'generator': {
            'type': 'Software',
            'homepage': window.location.protocol+'//'+window.location.host+window.location.pathname,
            'name': 'B2Note v2.0'
          },
          'created': datetime.toISOString(),
          'generated': datetime.toISOString()
        };
        this.postAnnotation(annotation)
        this.api.incAllAnnotationsKeyword()
  }

  createComment() {
    console.log('create semantic:', this.annotationcomment)
    let anvalue = this.annotationcomment;
        let datetime = new Date();
        let annotation = {
          '@context': 'http://www.w3.org/ns/anno/jsonld',
          'id': '',
          'type': 'Annotation',
          'body': {
            'type': 'TextualBody',
            'value': anvalue,
            'purpose': "commenting"
          },
          'target': {
            'id': this.api.target.id,
            'type': this.api.target.type,
            'source': this.api.target.source
          },
          'motivation': 'commenting',
          'creator': {
            'id':this.api.userinfo.id,
            'type': 'Person',
            'nickname': this.api.userinfo.pseudo
          },
          'generator': {
            'type': 'Software',
            'homepage': window.location.protocol+'//'+window.location.host+window.location.pathname,
            'name': 'B2Note v2.0'
          },
          'created': datetime.toISOString(),
          'generated': datetime.toISOString()
        };
        this.postAnnotation(annotation)
        this.api.incAllAnnotationsComment();
  }

  getSuggestions(value) {
        return this.api.getOntologySuggestions(value,4000)
          .then(data =>{
            return data;
          })
          .catch(error =>{
            return []
    })
    }

  checkKeyword(){
    //check whether keyword exist as semantic tag, if not createKeyword()
    // if yes display dialog 'Semantic' change the display to semantic and copy the value,
    // 'Keyword' will create keyword
    // 'Cancel' returns back to home
    this.getSuggestions(this.annotationkeyword)
      .then(suggestions =>{
        this.keywordterms=suggestions.length;
        if (this.keywordterms==0) {
          this.createKeyword()
        } else {
          this.confirmkeyword=true;
          this.suggestions=suggestions;
        }
       })
  }

  async switchSemantic(){
    this.annotationsemantic=this.annotationkeyword;
    this.active='tab1';
    this.confirmkeyword=false;
    //set the suggestions to autocomplete component;
    //console.log('switchsemantic() goodautocomplete ref',this.goodautocomplete)
    //wait 500 ms in order the view is back in semantic so the autocomplete dialog can be shown.
    await sleep(500);
    //console.log('seting suggestions',this.goodautocomplete)
    this.goodautocomplete.setSuggestions(this.suggestions);
  }
  switchCancel(){
    this.annotationkeyword=this.annotationsemantic='';
    this.active='tab1';
    this.confirmkeyword=false;
  }


}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * implements Home page - Creation of annotation
 * @todo implement target id and target source as parameters from URL
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Home {

  constructor(api) {
    this.api = api;
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
    this.showform = true; this.showack=false; this.showfirstlogin=false;
  }

  attached() {
    this.manualtarget = this.api.getManualTarget();
    this.api.getUserInfo()
      .then(data => {
        this.userinfo = data
        this.enablecreate = this.userinfo.id.length>0;
      })
      .catch(error => { //do nothing or alert
        })
    ;
  }

  activate(params, routeConfig, navigationInstruction){
    //parses params in url in form #b2note_home/id=https:/someurl/sdf&source=http://someurl&type=SpecificResource
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
    }

  }

  switchtab(tabid) {
    this.active = tabid;
    return true;
  }

  createSemantic() {
    console.log('create semantic:', this.annotationsemantic);
    let anvalue = this.annotationsemantic;

    //  let userinfo = data;
      let datetime = new Date();
      let annotation = {
        '@context': 'http://www.w3/org/ns/anno/jsonld',
        'id': '',
        'type': 'Annotation',
        'body': {
          'type': 'SpecificResource',
          'source': anvalue,
          'purpose': 'tagging'
        },
        'target': {
          'id': this.api.target.id,
          'type': this.api.target.type,
          'source': this.api.target.source
        },
        'motivation': 'tagging',
        'creator': {
          'id':this.userinfo.id,
          'type': 'Person',
          'nickname': this.userinfo.pseudo
        },
        'generator': {
          'type': 'Software',
          'homepage': window.location,
          'name': 'B2Note v2.0'
        },
        'created': datetime.toISOString(),
        'generated': datetime.toISOString()
      };
      this.postAnnotation(annotation);

  }

  postAnnotation(annotation) {
    this.api.postAnnotation(annotation)
      .then(data => {
        this.anid = data._id;
        this.showform = false; this.showack=true;
        this.annotation = data;
        this.annotationtext = JSON.stringify(data, null, 2);
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
    //TODO send userprofile data to backend to store
    //this.showform = true; this.showack=false; this.showfirstlogin=false;
  }

  showfirstlogin(){
    this.showform = false; this.showack=false; this.showfirstlogin=true;
  }

  createKeyword() {
    console.log('create keyword:', this.annotationkeyword)
    let anvalue = this.annotationkeyword;
        let datetime = new Date();
        let annotation = {
          '@context': 'http://www.w3/org/ns/anno/jsonld',
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
            'id':this.userinfo.id,
            'type': 'Person',
            'nickname': this.userinfo.pseudo
          },
          'generator': {
            'type': 'Software',
            'homepage': window.location,
            'name': 'B2Note v2.0'
          },
          'created': datetime.toISOString(),
          'generated': datetime.toISOString()
        };
        this.postAnnotation(annotation);


  }

  createComment() {
    console.log('create semantic:', this.annotationcomment)
    let anvalue = this.annotationkeyword;
        let datetime = new Date();
        let annotation = {
          '@context': 'http://www.w3/org/ns/anno/jsonld',
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
            'id':this.userinfo.id,
            'type': 'Person',
            'nickname': this.userinfo.pseudo
          },
          'generator': {
            'type': 'Software',
            'homepage': window.location,
            'name': 'B2Note v2.0'
          },
          'created': datetime.toISOString(),
          'generated': datetime.toISOString()
        };
        this.postAnnotation(annotation);
  }
}

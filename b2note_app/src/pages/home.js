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
    this.target = {}
    this.target.id = 'http://hdl.handle.net/11304/3e69a758-dbea-46cb-b9a1-2b2974531c19';
    this.target.source = 'https://b2share.eudat.eu/api/files/b381828e-59de-4323-b636-7600a6b04bf2/acqu3s';
    this.target.type = 'SpecificResource';
    this.anid = '';
    this.showform = true;
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
          'id': this.target.id,
          'type': this.target.type,
          'source': this.target.source
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
        this.showform = false;
        this.annotation = data;
        this.annotationtext = JSON.stringify(data, null, 2);
      })
      .catch(error => {
        alert('Error while creating annotation. It was not created\n\nHTTP status:' + error.status + '\nHTTP status text:' + error.statusText);
      })
  }

  closeackn() {
    this.showform = true;
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
            'id': this.target.id,
            'type': this.target.type,
            'source': this.target.source
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
            'id': this.target.id,
            'type': this.target.type,
            'source': this.target.source
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

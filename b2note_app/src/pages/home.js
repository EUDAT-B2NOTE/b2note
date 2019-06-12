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
    this.anid='';
  }

  attached() {
//  console.log('Home.attached()',this.manualtarget);
    this.manualtarget = this.api.getManualTarget();
  }

  switchtab(tabid) {
    this.active = tabid;
    return true;
  }

  createSemantic() {
    console.log('create semantic:', this.annotationsemantic);
    let anvalue= this.annotationsemantic;
    let userinfo = this.api.getUserInfo();
    let datetime = new Date();
    let annotation = {
      '@context': 'http://www.w3/org/ns/anno/jsonld',
      'id': '',
      'type': 'Annotation',
      'body': {
        'type': 'SpecificResource',
        'source': anvalue,
      },
      'target':{
        'id':this.target.id,
        'type':this.target.type,
        'source':this.target.source
      },
      'motivation':'tagging',
      'creator':{
        'type':'Person',
        'nickname':userinfo.pseudo
      },
      'generator':{
        'type':'Software',
        'homepage':window.location,
        'name':'B2Note v2.0'
      },
      'created': datetime.toISOString(),
      'generated':datetime.toISOString()
    }
    this.api.postAnnotation(annotation)
      .then(data =>{
        this.anid = data._id;
      })
  }

  createKeyword() {
    console.log('create keyword:', this.annotationkeyword)

  }

  createComment() {
    console.log('create semantic:', this.annotationcomment)

  }
}

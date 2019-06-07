import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)

export class Search {
  constructor(api){
    this.api=api;
  }
  attached(){
    this.newSearch();
  }

  newSearch(){
    this.api.deleteQueryitem(0); //delete query in api
  }

}

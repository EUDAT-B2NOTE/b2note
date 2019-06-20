import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Login{
constructor(api){
  this.allowgoogle=false;
  this.api=api;
}

attached(){
  this.allowgoogle=this.api.allowgoogle;
}

}

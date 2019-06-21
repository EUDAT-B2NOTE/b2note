/**
 * implements login page - redirect to b2access and optional google endpoints
 * in backend api
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

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

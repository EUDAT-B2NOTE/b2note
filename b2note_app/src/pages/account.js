import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Account {
  constructor(api) {
    this.api = api;
  }

  attached() {
    this.userinfo = this.api.getUserInfo();
    this.b2noteapiurl = this.api.getApiUrl();
    this.manualtarget = this.api.getManualTarget();
  }

  submitB2noteapiurl() {
    this.api.setApiUrl(this.b2noteapiurl);
  }

  submitManualtarget() {
    console.log('submitmanualtarget()',this.manualtarget)
    this.api.setManualTarget(this.manualtarget);
  }

}

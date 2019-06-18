import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Account {
  constructor(api) {
    this.api = api;
  }

  attached() {
    this.api.getUserInfo()
      .then(data =>{this.userinfo = data});
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

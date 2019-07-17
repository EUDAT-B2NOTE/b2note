/**
 * Account page component during activation it retrieves user info
 * it allows some custom settings
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Account {
  constructor(api) {
    this.api = api;
  }

  activate() {
    this.api.getUserInfo()
      .then(data =>{
        this.userinfo = data
        console.log('account() userinfo:',this.userinfo)
      });
//    this.b2noteapiurl = this.api.getApiUrl();
//    this.manualtarget = this.api.getManualTarget();
  }


}

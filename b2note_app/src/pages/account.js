/**
 * Account page component during activation it retrieves user info
 * it allows some custom settings
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
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
      });
  }
}

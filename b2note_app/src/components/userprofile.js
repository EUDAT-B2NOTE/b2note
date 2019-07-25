/**
 * Component to show search dialog
 *
 * based on settings shows selected dialog
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import {bindable} from 'aurelia-framework';
import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Userprofile{
@bindable userinfo;
  constructor(api){
    this.edit=false;
    this.api=api;
  }
  enableEdit(){
    //console.log('edit up',this.userinfo)
    this.edit=true;
    if (!this.userinfo.experience) this.userinfo.experience='beginner'
  }
  saveEdit(){
    this.edit=false;
    this.api.saveUserProfile(this.userinfo)
      .catch(error=>{
        alert('Error while updating user profile. \n\nHTTP status:' + error.status + '\nHTTP status text:' + error.statusText);
      })


  }
}

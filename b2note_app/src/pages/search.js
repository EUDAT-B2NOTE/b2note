/**
 * Component to show search dialog
 *
 * based on settings shows selected dialog
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */
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

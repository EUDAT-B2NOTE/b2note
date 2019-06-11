import {AnnotationApi} from './annotationapi';
import {inject} from 'aurelia-framework';
import {Arraysearchdialog} from "./arraysearchdialog";

@inject(AnnotationApi)
export class Dropdownsearchdialog extends Arraysearchdialog {
  constructor(api) {
    super(api);
  }
}

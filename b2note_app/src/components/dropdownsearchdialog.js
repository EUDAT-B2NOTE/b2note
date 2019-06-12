import {AnnotationApi} from './annotationapi';
import {inject} from 'aurelia-framework';
import {customElement} from 'aurelia-templating';
import {Arraysearchdialog} from "./arraysearchdialog";

@inject(AnnotationApi)
@customElement()
export class Dropdownsearchdialog extends Arraysearchdialog {
  constructor(api) {
    super(api);
  }
}

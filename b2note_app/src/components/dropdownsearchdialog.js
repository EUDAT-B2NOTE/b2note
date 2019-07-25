/**
 * Dropdown Search Dialog component to render array like dialog to specify search query
 * with dropdown instead of tabs
 *
 * search query operators are interpretted as follows
 * e.g.: A and B or C and D =>  (A and (B or (C and D)))
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

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

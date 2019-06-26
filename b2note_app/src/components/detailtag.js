/**
 * Detail information about annotation tag
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';
import {bindable} from 'aurelia-framework';
import {EventAggregator} from 'aurelia-event-aggregator';
import {Taginfo} from "./messages";

@inject(AnnotationApi,EventAggregator)
export class Detailtag {
  @bindable id;
  constructor(api,ea){
    this.api = api;
    this.ea = ea;
    this.showtaginfo=false;
  }

  attached() {
    this.showtaginfo=false;
    this.s1 = this.ea.subscribe(Taginfo, msg => this.changeTagInfo(msg.taginfo));
  }

  detached() {
    this.s1.dispose();
  }

  changeTagInfo(taginfo){
    if (taginfo.domid === this.id){ //taginfo is addressed to this instance
      //visualize
      //console.log('Detailtag.changeTagInfo()',taginfo);
      this.taginfo = taginfo;
      this.tagtitle = this.taginfo.body.value;
      this.showtaginfo=true;
      //this.tagtitle=taginfo.tagvalue;
    }
  }


}

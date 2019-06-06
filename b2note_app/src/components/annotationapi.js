import {Userinfo} from './messages';

import {EventAggregator} from 'aurelia-event-aggregator';
import {HttpClient} from 'aurelia-fetch-client';
import {inject} from 'aurelia-framework';

@inject(EventAggregator, HttpClient)
export class AnnotationApi {
  constructor(ea,client){
    this.username = "Guest"
    this.client=client;
    this.ea=ea;
}
  getUserName() {
    //TODO fake username
    this.username = "Tomas Kulhanek "+ Math.random().toString(36).substring(7);
    let userinfo = {username:this.username, userid:Math.random().toString(36).substring(7)}
    this.ea.publish(new Userinfo(userinfo))
    return this.username;
  }
}

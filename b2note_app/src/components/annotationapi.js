import {Userinfo} from './messages';

import {EventAggregator} from 'aurelia-event-aggregator';
import {HttpClient} from 'aurelia-fetch-client';
import {inject} from 'aurelia-framework';

@inject(EventAggregator, HttpClient)
export class AnnotationApi {
  constructor(ea,client){
    this.username = "Guest";
    this.client=client;
    this.ea=ea;
    this.query = []
    this.manualtarget=false;
    this.apiurl='/api';
}
  getUserName() {
    //TODO fake username
    this.username = "Tomas Kulhanek "+ Math.random().toString(36).substring(7);
    let userinfo = {username:this.username, userid:Math.random().toString(36).substring(7)}
    this.ea.publish(new Userinfo(userinfo))
    return this.username;
  }

  getUserInfo(){
    return {
      pseudo: "Guest",
      email: "N/A",
      firstname: "Guest",
      lastname: "",
      experience: "beginner",
      jobtitle: "Annotator",
      org: "Academia",
      country: "International"
    }
  }

  //push = add new item
  pushQueryitem(item){
    if (this.query.length===0) {item.logic=''} // remove logic from first item - logic is binary operator
    return this.query.push(item)-1;
  }

  //modify item at index
  modifyQueryitem(index,item){
    this.query[index] = item;
  }
  //delete all from index
  deleteQueryitem(index){
    while (index<this.query.length) {
      this.query.pop()
    }
  }

  searchQuery(query){
    //query is defined - then use it, otherwise use the query constructed from push.. modify... delete.. methods above
    console.log('searchQuery',query,this.query);
    if (query) this.query=query;
    for (let i=0;i<this.query.length;i++){
      console.log(this.query[i].logic+' '+this.query[i].type+' '+this.query[i].value);
    }
  }

  setApiUrl(url){
    this.apiurl=url;
  }
  getApiUrl(){
    return this.apiurl;
  }

  setManualTarget(mt){
    console.log('AnnotationApi.setmanualtarget()',mt)
    this.manualtarget=mt;
  }
  getManualTarget(){
    console.log('AnnotationApi.getmanualtarget()',this.manualtarget)
    return this.manualtarget;
  }
}

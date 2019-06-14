import {Userinfo} from './messages';

import {EventAggregator} from 'aurelia-event-aggregator';
import {HttpClient,json} from 'aurelia-fetch-client';
import {inject} from 'aurelia-framework';

@inject(EventAggregator, HttpClient)
export class AnnotationApi {
  constructor(ea,client){
    this.username = "Guest";
    this.client=client;
    this.ea=ea;
    this.query = []
    this.manualtarget=true;
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
  //returns the index in list where it was pushed.
  pushQueryitem(item){
    // remove binary,leave unary NOT logic operator from first item
    if ((this.query.length===0) && (item.logic!=='NOT')) item.logic='';
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
    //console.log('searchQuery',query,this.query);
    if (query) this.query=query;
    let apiquery = this.createApiQuery();
    return this.client.fetch(this.apiurl+'/annotations?where='+JSON.stringify(apiquery))
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json()
        else throw response
      })
      .then(data =>{
        console.log('searchAnnotation() data',data);
        return data
      })
      .catch(error =>{
        console.log('searchAnnotation() error',error);
        throw error;
      })
  }


  createApiQuery(){
    return this.createQueryRecord(this.query)
  }

  createQueryRecord(myquery){
    if (myquery.length>0){
      let query=myquery.slice();
      if (query.length==1) return this.createQueryitem(query[0])
      //console.log('createQueryRecord ',query)
      let first = query.shift();
      //console.log('createQueryRecord shift',first);
      //console.log('createQueryRecord query',query)
      let q;
      if (query[0].logic.match(/AND*/)) q={'$and':[this.createQueryitem(first),this.createQueryRecord(query)]};
      if (query[0].logic.match(/OR*/)) q={'$or':[this.createQueryitem(first),this.createQueryRecord(query)]};
      return q;
    }
    else return {};
    /*this.anquery={}
    if (query.length>0) {
      this.anquery = createQueryitem(query[0])
      for (let i = 1; i < query.length; i++) {
        //console.log(this.query[i].logic+' '+this.query[i].type+' '+this.query[i].value);
        addQueryitem(query.logic, createQueryitem(query))
      }
    }*/
  }

  /*
    value==qitem - {'value':'qitem'}
    NOT value == qitem = {'value':{$ne:'qitem'}
    AND value=q1 AND value==q2 - {'value':'q1','value':'q1' } or {$and:[{'value':'q1'},{'value':'q2'}]}
    OR value=q1 OR value==q2 - {$or:[{'value':'q1'},{'value':'q2'}]}
   */



  createQueryitem(qi){
    if (qi.type ==='comment')
      return {'body.purpose':'commenting'};
    else if (qi.type === 'semantic')
      //TODO check if synonyms - then add keyword with the same value???
    {
      //console.log('createQueryitem()',qi)
      if (qi.logic.match(/.*NOT/)) return {'body.type': 'SpecificResource', 'body.source': {'$ne': qi.value}};
      else return {'body.type': 'SpecificResource', 'body.source': qi.value}
    }
    else //keyword
    {
      //console.log('createQueryitem()',qi)
      //console.log('createQueryitem logic ()',qi.logic)
      if (qi.logic.match(/.*NOT/)) return {'body.type': 'TextualValue', 'body.value': {'$ne': qi.value}};
      return {'body.type': 'TextualValue', 'body.value': qi.value}
    }

    //{"body.value":"protein2"}
  }

  setApiUrl(url){
    this.apiurl=url;
  }
  getApiUrl(){
    return this.apiurl;
  }

  setManualTarget(mt){
  //  console.log('AnnotationApi.setmanualtarget()',mt)
    this.manualtarget=mt;
  }
  getManualTarget(){
  //  console.log('AnnotationApi.getmanualtarget()',this.manualtarget)
    return this.manualtarget;
  }

  postAnnotation(an){
    return this.client.fetch(
      this.apiurl+'/annotations',
      {
        method:"POST",
        body:json(an)
      })
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json()
        else throw response
      })
      .then(data =>{
        console.log('postAnnotation() data',data);
        return data
      })
      .catch(error =>{
        console.log('postAnnotation() error',error);
        throw error;
      })
  }
}

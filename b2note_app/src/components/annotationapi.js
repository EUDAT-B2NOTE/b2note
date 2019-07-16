/**
 * AnnotationApi component to serve AnnotationApi and shared properties and functionalities
 *
 * in order to share properties, it's instance should be injected as singleton by aurelia-framework
 * using e.g.:
 *
 *   @inject(AnnotationApi)
 *   export class Myclass {
 *      constructor(api) {
 *        this.api = api
 *      }
 *      mymethod(){
 *          //now AnnotationApi methods can be called or shared properties can be retrieved
 *          this.api.getUserInfo()
 *      }
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {Userinfo} from './messages';
import {EventAggregator} from 'aurelia-event-aggregator';
import {HttpClient, json} from 'aurelia-fetch-client';
import {inject} from 'aurelia-framework';

@inject(EventAggregator, HttpClient)
export class AnnotationApi {

  constructor(ea, client) {

    this.client = client;
    if (this.client.configure) {
      this.client.configure(config => {
        config
          .rejectErrorResponses()
          .withDefaults({
            credentials: 'same-origin',
            /*            headers: {

                          'Accept': 'application/json',
                          'Content-Type': 'application/json'
                        }*/
          })
      });
    }
    this.headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    this.ea = ea;
    this.userinfo = {};
    this.query = [];
    this.manualtarget = true;
    this.apiurl = window.location.protocol + '//' + window.location.host + '/api';
    this.annotationsurl = this.apiurl + '/annotations';
    this.userinfourl = this.apiurl + '/userinfo';
    this.ontologyurl = 'https://b2note.bsc.es/solr/b2note_index';
    //this.solrurl='https://b2note.bsc.es/solr/b2note_index/select?q=((labels:/stry.*/) AND NOT (labels:/Error[0-9].*/))&sort=norm(labels) desc&fl=labels,uris,ontology_acronym,short_form,synonyms,norm(labels)&wt=json&indent=true&rows=1000';
    //enhance the pagination up to EVE limit - see b2note_settings.py for pagination limit to make it bigger
    this.maxresult = 8192;
    this.allowgoogle = false;
    this.searchdialog = 'dropdown'//,'array','recursive'
    //this.target = {id:'',source:''}
    this.target = {}
    this.target.id = '';
    this.target.source = '';
    this.target.type = 'SpecificResource';
    this.lastsuggest = {}; //associative array of suggestion containing ontologies
  }

  isLoggedIn() {
    let that = this;
    if (this.userinfo.id) return new Promise(function (resolve, reject) {
      resolve(that.userinfo.id.length > 0)
    })
    else {
      return this.getUserInfo()
        .then(ui => {
          return (ui.id) && (ui.id.length > 0);
        })

    }
  }

  /**
   * fetch user info from api/userinfo endpoint and returns parsed data structure from json response
   * throws exception in case of error
   * @returns {Q.Promise<any> | promise.Promise<T | never> | promise.Promise<T | never> | * | undefined | Promise<T | never>}
   */
  getUserInfo() {
    let that = this;
    if (this.userinfo.id) return new Promise(function (resolve, reject) {
      resolve(that.userinfo)
    })
    else
      return this.client.fetch(this.userinfourl)
        .then(response => {
          //console.log(response);
          if (response.ok) return response.json();
          else throw response
        })
        .then(data => {
          if (!data.pseudo) data.pseudo = data.name;
          data.firstname = data.given_name;
          data.lastname = data.family_name;
          /*TODO fill experience,jobtitle,org and country
          data.experience= "beginner",
          data.jobtitle="Annotator",
          data.org="Academia",
          data.country="International"*/
          console.log('userinfo', data);
          this.userinfo = data;
          this.ea.publish(new Userinfo(data));
          return data
        })
        .catch(error => {
          console.log('userinfo error:', this.userinfourl, error);
          throw error;
        })
    /*{"id":"101486217992397526303",
    "email":"tmkulhanek@gmail.com",
    "verified_email":true,
    "name":      "Tomas Kulhanek",
    "given_name":"Tomas",
    "family_name":"Kulhanek","picture":"https://lh6.googleusercontent.com/-TxFomtJl7d0/AAAAAAAAAAI/AAAAAAAAAAA/ACHi3reEWif0mbxIXUPgZAG32waifi03fQ/mo/photo.jpg","locale":"en"}

    {
    pseudo: "Guest",
    email: "N/A",
    firstname: "Guest",
    lastname: "",
    experience: "beginner",
    jobtitle: "Annotator",
    org: "Academia",
    country: "International"
  }*/
  }

  //push = add new item
  //returns the index in list where it was pushed.
  pushQueryitem(item) {
    // remove binary,leave unary NOT logic operator from first item
    if ((this.query.length === 0) && (item.logic !== 'NOT')) item.logic = '';
    return this.query.push(item) - 1;
  }

  //modify item at index
  modifyQueryitem(index, item) {
    this.query[index] = item;
  }

  //delete all from index
  deleteQueryitem(index) {
    while (index < this.query.length) {
      this.query.pop()
    }
  }

  searchQuery(query) {
    //query is defined - then use it, otherwise use the query constructed from push.. modify... delete.. methods above
    //console.log('searchQuery',query,this.query);
    if (query) this.query = query;
    let apiquery = this.createApiQuery();
    return this.client.fetch(this.apiurl + '/annotations?where=' + JSON.stringify(apiquery))
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json();
        else throw response
      })
      .then(data => {
        console.log('searchAnnotation() data', data);
        return data
      })
      .catch(error => {
        console.log('searchAnnotation() error', error);
        throw error;
      })
  }


  createApiQuery() {
    return this.createQueryRecord(this.query)
  }

  createQueryRecord(myquery) {
    if (myquery.length > 0) {
      let query = myquery.slice();
      if (query.length == 1) return this.createQueryitem(query[0])
      //console.log('createQueryRecord ',query)
      let first = query.shift();
      //console.log('createQueryRecord shift',first);
      //console.log('createQueryRecord query',query)
      let q;
      if (query[0].logic.match(/AND*/)) q = {'$and': [this.createQueryitem(first), this.createQueryRecord(query)]};
      if (query[0].logic.match(/OR*/)) q = {'$or': [this.createQueryitem(first), this.createQueryRecord(query)]};
      return q;
    } else return {};
  }

  /*
    value==qitem - {'value':'qitem'}
    NOT value == qitem = {'value':{$ne:'qitem'}
    AND value=q1 AND value==q2 - {'value':'q1','value':'q1' } or {$and:[{'value':'q1'},{'value':'q2'}]}
    OR value=q1 OR value==q2 - {$or:[{'value':'q1'},{'value':'q2'}]}
   */


  createQueryitem(qi) {
    if (qi.type === 'comment')
      return {'body.purpose': 'commenting'};
    else if (qi.type === 'semantic')
    //TODO check if synonyms - then add keyword with the same value???
    {
      //console.log('createQueryitem()',qi)
      if (qi.logic.match(/.*NOT/)) return {'body.type': 'SpecificResource', 'body.source': {'$ne': qi.value}};
      else return {'body.type': 'SpecificResource', 'body.source': qi.value}
    } else //keyword
    {
      //console.log('createQueryitem()',qi)
      //console.log('createQueryitem logic ()',qi.logic)
      if (qi.logic.match(/.*NOT/)) return {'body.type': 'TextualValue', 'body.value': {'$ne': qi.value}};
      return {'body.type': 'TextualValue', 'body.value': qi.value}
    }

    //{"body.value":"protein2"}
  }

  setApiUrl(url) {
    this.apiurl = url;
  }

  getApiUrl() {
    return this.apiurl;
  }

  setManualTarget(mt) {
    //  console.log('AnnotationApi.setmanualtarget()',mt)
    this.manualtarget = mt;
  }

  getManualTarget() {
    //  console.log('AnnotationApi.getmanualtarget()',this.manualtarget)
    return this.manualtarget;
  }

  postAnnotation(an) {
    return this.client.fetch(
      this.annotationsurl,
      {
        method: "POST",
        headers: {'Authorization': 'Bearer ' + this.userinfo.token},
        body: json(an)
      })
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {
        //console.log('postAnnotation() data', data);
        return data
      })
      .catch(error => {
        console.log('postAnnotation() error', error);
        throw error;
      })
  }

  getAllAnnotations() {
    return this.client.fetch(this.annotationsurl + "?max_results=" + this.maxresult)
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {
        //console.log('postAnnotation() data', data);
        return data
      })
      .catch(error => {
        console.log('getAnnotation() error', error);
        throw error;
      })

  }

  getAllAnnotationsFileSemantic() {
    return this.getAllAnnotationsAboutThisFile('"$and":[{"body.purpose":"tagging"},{"$or":[{"body.type":"Composite"},{"body.type":"SpecificResource"}]}]')
  }

  //https://b2note.bsc.es/api/annotations?where={"$and":[{"body.purpose":"tagging"},{"body.type":"TextualBody"}]}
  getAllAnnotationsFileKeyword() {
    return this.getAllAnnotationsAboutThisFile('"$and":[{"body.purpose":"tagging"},{"body.type":"TextualBody"}]')
  }

  getAllAnnotationsFileComment() {
    return this.getAllAnnotationsAboutThisFile('"body.purpose":"commenting"')
  }


  getAllAnnotationsAboutThisFile(filter = "") {
    let myfilter = '?where={"target.id":"' + this.target.id + '"' + (filter.length > 0 ? ',' + filter + '}' : '}');
    return this.client.fetch(this.annotationsurl + myfilter + '&max_results=' + this.maxresult)
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {
        //console.log('postAnnotation() data', data);
        return data
      })
      .catch(error => {
        console.log('getAnnotation() error', error);
        throw error;
      })

  }

  //https://b2note.bsc.es/api/annotations?where={"$and":[{"body.purpose":"tagging"},{"$or":[{"body.type":"SpecificResource"},{"body.type":"Composite"}]}]}
  getAllMyAnnotationsSemantic() {
    return this.getAllMyAnnotations('"$and":[{"body.purpose":"tagging"},{"$or":[{"body.type":"SpecificResource"},{"body.type":"Composite"}]}]')
  }

  //https://b2note.bsc.es/api/annotations?where={"$and":[{"body.purpose":"tagging"},{"body.type":"TextualBody"}]}
  getAllMyAnnotationsKeyword() {
    return this.getAllMyAnnotations('"$and":[{"body.purpose":"tagging"},{"body.type":"TextualBody"}]')
  }

  getAllMyAnnotationsComment() {
    return this.getAllMyAnnotations('"body.purpose":"commenting"')
  }

  //http://localhost/api/annotations?where={"creator.id":"1527d37f-c884-43d4-b7fc-cfa87062d827","$and":[{"body.purpose":"tagging"},{"$or":[{"body.type":"SpecificResource"},{"body.type":"Composite"}]}]}};

  getAllMyAnnotations(filter = "") {
    return this.getUserInfo()
      .then(ui => {
        let userinfo = ui;
        let myfilter = '?where={"creator.id":"' + ui.id + '"' + (filter.length > 0 ? ',' + filter + '}' : '}'); //this will append filter query if it is not empty
        console.log('getallmyannotations', filter, myfilter);
        return this.client.fetch(this.annotationsurl + myfilter + '&max_results=' + this.maxresult)
          .then(response => {
            //console.log(response);
            if (response.ok) return response.json()
            else throw response
          })
          .then(data => {
            //console.log('postAnnotation() data', data);
            return data
          })
          .catch(error => {
            console.log('getAnnotation() error', error);
            throw error;
          })

      });
  }

  getOntologies(uris) {
    let query = '("' + uris[0];
    for (let i = 1; i < uris.length; i++) {
      query += '" OR "' + uris[i];
    }
    query += '")';
    query = query.replace(/#/g,'%23');
    console.log('getOntologies query:',query)
    return this.client.fetch(this.ontologyurl + '/select?q=uris:' + query + '&rows=100&wt=json', {headers: {}})
      .then(response => {
        //console.log(response);
        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {
        //console.log('postAnnotation() data', data);
        return data
      })
      .catch(error => {
        console.log('getOntologies() error', error);
        throw error;
      })
  }

  /*** send API request to SOLR returns array of string in form 'name (count)'
   *   stores internally ontologies returned which is then used by subsequent call of getAnnotationItems()
   */

  getOntologySuggestions(prefix){
    //this.solrurl='https://b2note.bsc.es/solr/b2note_index/select?q=((labels:/stry.*/) AND NOT (labels:/Error[0-9].*/))&sort=norm(labels) desc&fl=labels,uris,ontology_acronym,short_form,synonyms,norm(labels)&wt=json&indent=true&rows=1000';
    let queryurl=this.ontologyurl+'/select?q=((labels:/'+prefix+'.*/) AND NOT (labels:/Error[0-9].*/))&sort=norm(labels) desc&fl=labels,uris,ontology_acronym,short_form,synonyms,norm(labels)&wt=json&indent=true&rows=1000';
    return this.client.fetch(queryurl, {headers:{}})
      .then(response =>{
        if (response.ok) return response.json();
        else throw response
      })
      .then (data =>{
        //aggregate per labels
        let suggclasses ={}
        for (let ont of data.response.docs) {
          //console.log('ontology class',ont);
          if (suggclasses.hasOwnProperty(ont.labels)){
            suggclasses[ont.labels].count++;
            suggclasses[ont.labels].str=suggclasses[ont.labels].name+' ('+suggclasses[ont.labels].count+')';
            suggclasses[ont.labels].ontologies.push(ont);
          } else {
            suggclasses[ont.labels]={}
            suggclasses[ont.labels].name=ont.labels;
            suggclasses[ont.labels].count=1;
            suggclasses[ont.labels].str=ont.labels+' (1)';
            suggclasses[ont.labels].ontologies=[]
            suggclasses[ont.labels].ontologies.push(ont);
          }
        }
        //create array of string representation which is returned
        let suggclassesstring =[];
        //sort keys by number of classes
        let keys = Object.keys(suggclasses);
        let keyssorted = keys.sort(function(a,b){return suggclasses[b].count - suggclasses[a].count});
        //store lastsuggest as 'associative array'
        this.lastsuggest={}
        //create string repr. in form 'name (count)'
        for (let key of keyssorted){
          suggclassesstring.push(suggclasses[key].str);
          this.lastsuggest[suggclasses[key].str]={}
          this.lastsuggest[suggclasses[key].str].name=key;
          this.lastsuggest[suggclasses[key].str].ontologies=suggclasses[key].ontologies; //store lastsuggest ontologies associated by suggestion
        }
        return suggclassesstring;
      })
      .catch(error=>{
        console.log('getOntologySuggestion() error',error);
        throw error
      })
  }

  /***
   * constructs items struct as W3C data annotation model from ontologies already stored during previous getOntologySuggestions
   */
  getAnnotationItems(key){
    let items= []
    for (let ont of this.lastsuggest[key].ontologies) {
      let item={type:'SpecificResource',source:ont.uris}
      items.push(item)
    }
    items.push({type:'TextualBody',value:this.lastsuggest[key].name})
    return items;
  }

}

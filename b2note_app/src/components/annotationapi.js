/**
 * AnnotationApi class to serve client calls of backend api and share features and properties
 * in order to share properties, it's instance must be injected as singleton by aurelia-framework
 * using e.g.:
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
 * @since v2.0
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
    this.userprofileurl = this.apiurl+'/userprofile';
    this.ontologyurl = 'https://b2note.bsc.es/solr/b2note_index';
    //enhance the pagination up to EVE limit - see b2note_settings.py for pagination limit to make it bigger
    this.maxresult = 8192;
    this.allowgoogle = false;
    this.searchdialog = 'dropdown'//,'array','recursive'
    this.target = {}
    this.target.id = '';
    this.target.source = '';
    this.target.type = 'SpecificResource';
    this.lastsuggest = {}; //associative array of suggestion containing ontologies
    this.afs=this.afk=this.afc=0; //indeces for cache purpose - increment when some change appears
    this.router=undefined;//router
    this.homeattached=false;//workaround for webcomponent routing
  }

  /**
   * Checks whether userinfo is set or tries to get it - user is logged
   * @returns {(Q.Promise<any> | promise.Promise<T | never>)|Promise<any>}
   */
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
          if (!data.firstname) data.firstname = data.given_name;
          if (!data.lastname) data.lastname = data.family_name;
          /*TODO fill experience,jobtitle,org and country
          data.experience= "beginner",
          data.jobtitle="Annotator",
          data.org="Academia",
          data.country="International"*/
          //console.log('userinfo', data);
          this.userinfo = data;
          this.ea.publish(new Userinfo(data));
          return data
        })
        .catch(error => {
          console.log('userinfo error:', this.userinfourl, error);
          throw error;
        })
  }

  /**
   * Pushes (adds to the end) new item into constructed query
   * @param item
   * @returns {number} index of item in query array
   */
  pushQueryitem(item) {
    // remove binary,leave unary NOT logic operator from first item
    if ((this.query.length === 0) && (item.logic !== 'NOT')) item.logic = '';
    return this.query.push(item) - 1;
  }

  /**
   * Modifies item on specified index
   * @param index
   * @param item
   */
  modifyQueryitem(index, item) {
    this.query[index] = item;
  }

  /**
   * Deletes all items from specified index to the end
   * @param index
   */
  deleteQueryitem(index) {
    while (index < this.query.length) {
      this.query.pop()
    }
  }

  /**
   * Query API using the query - if undefined, then use cosntructed query from previous calls of [push/modify/delete]QueryItem()
   * @param query
   * @returns {*}
   */
  searchQuery(query) {
    //query is defined - then use it, otherwise use the query constructed from push.. modify... delete.. methods above
    console.log('searchQuery',query,this.query);
    if (query) this.query = query;
    let apiquery = this.createApiQuery();
    return this.client.fetch(this.apiurl + '/annotations?where=' + apiquery)
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

  /**
   * translates constructed query to EVE API query
   * @returns {*|{}}
   */
  createApiQuery() {
    return this.createQueryRecord(this.query)
  }

  /**
   * Translates myquery into API query
   * @param myquery
   * @returns {({$and: *[]}|{$or: *[]})|{}|{"body.purpose"}|{"body.source", "body.type"}|{"body.value", "body.type"}}
   */
  createQueryRecord(myquery) {
    if (myquery.length > 0) {
      let query = myquery.slice();
      if (query.length == 1) return this.createQueryitem(query[0])
      //console.log('createQueryRecord ',query)
      let first = query.shift();
      //console.log('createQueryRecord shift',first);
      //console.log('createQueryRecord query',query)
      let q;
      if (query[0].logic.match(/AND*/)) q = '{"$and": ['+this.createQueryitem(first)+', '+this.createQueryRecord(query)+']}';
      if (query[0].logic.match(/OR*/)) q = '{"$or": ['+this.createQueryitem(first)+', '+this.createQueryRecord(query)+']}';
      return q;
    } else return {};
  }

  /**
   * Translates single query item to API query item as follows:
    - value==qitem - {'value':'qitem'}
    - NOT value == qitem = {'value':{$ne:'qitem'}
    - AND value=q1 AND value==q2 - {'value':'q1','value':'q1' } or {$and:[{'value':'q1'},{'value':'q2'}]}
    - OR value=q1 OR value==q2 - {$or:[{'value':'q1'},{'value':'q2'}]}
   * @param qi
   * @returns {{"body.purpose": string}|{"body.value": {$ne: *}, "body.type": string}|{"body.source": *, "body.type": string}|{"body.value": *, "body.type": string}|{"body.source": {$ne: *}, "body.type": string}}
   */
  createQueryitem(qi) {
    console.log('createQueryItem qi:',qi);
    if (qi.type === 'comment')
      return '{"body.purpose": "commenting"}';
    else if (qi.type === 'semantic')
    //TODO check if synonyms - then add keyword with the same value???
    {
      //semvalue - is textualbody value stored in annotation records - next to specific tags - thus searching the textualvalue among 'SpecificResources'

      let semvalue=this.lastsuggest[qi.value] ? this.lastsuggest[qi.value].name : qi.value; //if previous suggestion exists for qi.value - then use it
      console.log("createQueryitem() semvalue,qi.value,lastsuggest[]",semvalue,qi.value,this.lastsuggest[qi.value])
      if (qi.logic.match(/.*NOT/)) return '{"body.purpose": "tagging","body.items":{"$elemMatch":{"value":{"$ne":"'+semvalue+'"}}}}'
      else return '{"body.purpose": "tagging","body.items":{"$elemMatch":{"value":"'+semvalue+'"}}}'
    } else //keyword
    {
      if (qi.logic.match(/.*NOT/)) return '{"body.purpose": "tagging","body.type":"TextualBody","body.value":{"$ne":"'+qi.value+'"}}'
      return '{"body.purpose": "tagging","body.type":"TextualBody","body.value":"'+qi.value+'"}'
    }
  }

  /**
   * Sends POST request to create annotation in DB
   *
   * @param an annotation conforming W3C annotation data model - validation is made by DB
   * @returns {Promise} with  response data deserialized from json - annotation with created _id and id
   */
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

  /**
   * Sends DELETE request to delete annotation from DB
   *
   * @param an Annotation - _id and _etag properties are mandatory to delete annotation
   * @returns {Promise} with response data deserialized from json
   */
  deleteAnnotation(an) {
    return this.client.fetch(
      this.annotationsurl+'/'+an._id,
      {
        method: "DELETE",
        headers: {'Authorization': 'Bearer ' + this.userinfo.token,'If-Match':an._etag},
        //body: json(an)
      })
      .then(response => {
        //console.log(response);
        if (response.ok) return response
        else throw response
      })
      .catch(error => {
        console.log('deleteAnnotation() error', error);
        throw error;
      })
  }
  /**
   * Sends PUT request to update annotation in DB
   *
   * @param an - Annotation - _id and _etag properties are mandatory to update annotation
   * @returns {} Promise with  response data deserialized from json
   */
  putAnnotation(an) {
    return this.client.fetch(
      this.annotationsurl+'/'+an._id,
      {
        method: "PUT",
        headers: {'Authorization': 'Bearer ' + this.userinfo.token,'If-Match':an._etag},
        body: json(an)
      })
      .then(response => {
        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {
        return data
      })
      .catch(error => {
        console.log('putAnnotation() error', error);
        throw error;
      })
  }

  /**
   * Sends PUT request to update userprofile in DB
   *
   * @param up - User Profile - id and _etag properties are mandatory to update user profile
   * @returns {} Promise with  response data deserialized from json
   */
  putUserprofile(up) {
    return this.client.fetch(
      this.userprofileurl+'/'+up._id,
      {
        method: "PUT",
        headers: {'Authorization': 'Bearer ' + this.userinfo.token,'If-Match':up._etag},
        body: json(up)
      })
      .then(response => {
        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {
        return data
      })
      .catch(error => {
        console.log('putUserprofile() error', error);
        throw error;
      })
  }
  /**
   * Sends POST request to create user profile in DB
   *
   * @param up user profile
   * @returns {Promise} with response data deserialized from json - user profile with created id and _etag
   */
  postUserprofile(up) {
    return this.client.fetch(
      this.userprofileurl,
      {
        method: "POST",
        headers: {'Authorization': 'Bearer ' + this.userinfo.token},
        body: json(up)
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
        console.log('postUserprofile() error', error);
        throw error;
      })
  }

  /**
   * gets all annotations using API call
   * @returns {*}
   */
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

  /**
   * gets all annotations whose 'purpose' is set to 'tagging' or is 'Composite' and contains 'SpecificResource' type
   * @returns {*}
   */
  getAllAnnotationsFileSemantic() {
    return this.getAllAnnotationsAboutThisFile('"$and":[{"body.purpose":"tagging"},{"$or":[{"body.type":"Composite"},{"body.type":"SpecificResource"}]}]',this.afs)
  }
  //internal, call this to increment 'afs' index when number of semantic annotation is expected to change
  incAllAnnotationsSemantic(){
    this.afs++;
  }

  /**
   * gets all annotations whose 'purpose' is 'tagging' and 'type' is 'TextualBody'
   * @returns {*}
   */
  getAllAnnotationsFileKeyword() {
    return this.getAllAnnotationsAboutThisFile('"$and":[{"body.purpose":"tagging"},{"body.type":"TextualBody"}]',this.afk)
  }

  //internal, call this to increment 'afk' index when number of keyword annotation is expected to change
  incAllAnnotationsKeyword(){
    this.afk++;
  }

  /**
   * gets all annotation whose 'purpose' is 'commenting'
   * @returns {*}
   */
  getAllAnnotationsFileComment() {
    return this.getAllAnnotationsAboutThisFile('"body.purpose":"commenting"',this.afc)
  }

  //internal, call this to increment 'afs' index when number of comment annotation is expected to change
  incAllAnnotationsComment(){
    this.afc++;
  }

  /**
   * Gets all annotation about this file, with the defined filter in EVE API format, customq used to force browser API call when change is expected
   * @param filter
   * @param customq
   * @returns {*}
   */
  getAllAnnotationsAboutThisFile(filter = "",customq=0) {
    let myfilter = '?where={"target.id":"' + this.target.id + '"' + (filter.length > 0 ? ',' + filter + '}' : '}')+(customq>0?'&customq='+customq:'');
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

  /**
   * gets users annotations whose 'purpose' is set to 'tagging' or is 'Composite' and contains 'SpecificResource' type
   * @returns {*}
   */

  getAllMyAnnotationsSemantic() {
    return this.getAllMyAnnotations('"$and":[{"body.purpose":"tagging"},{"$or":[{"body.type":"SpecificResource"},{"body.type":"Composite"}]}]',this.afs)
  }

  /**
   * gets users annotations whose 'purpose' is 'tagging' and 'type' is 'TextualBody'
   * @returns {*}
   */
  getAllMyAnnotationsKeyword() {
    return this.getAllMyAnnotations('"$and":[{"body.purpose":"tagging"},{"body.type":"TextualBody"}]',this.afk)
  }

  /**
   * gets all annotation whose 'purpose' is 'commenting'
   * @returns {*}
   */
  getAllMyAnnotationsComment() {
    return this.getAllMyAnnotations('"body.purpose":"commenting"',this.afc)
  }


  /**
   * Gets all annotation of user, with the defined filter in EVE API format, customq used to force browser API call when change is expected
   * @param filter
   * @param customq
   * @returns {*}
   */
  getAllMyAnnotations(filter = "",customq=0) {
    return this.getUserInfo()
      .then(ui => {
        let userinfo = ui;
        let myfilter = '?where={"creator.id":"' + ui.id + '"' + (filter.length > 0 ? ',' + filter + '}' : '}')+(customq>0?'&customq='+customq:''); //this will append filter query if it is not empty
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

  /**
   * gets ontologies from SOLR index conforming uris.
   * @param uris - array of string, at least one uri should be specified
   * @returns {*}
   */
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

        if (response.ok) return response.json()
        else throw response
      })
      .then(data => {

        return data
      })
      .catch(error => {
        console.log('getOntologies() error', error);
        throw error;
      })
  }

  /**
   *  send API request to SOLR returns array of string in form 'name (count)'
   *  stores internally ontologies returned which is then used by subsequent call of getAnnotationItems()
   * @param prefix
   * @returns {*}
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

  /**
   * constructs items struct as W3C data annotation model from ontologies already stored during previous getOntologySuggestions
   * @param key
   * @returns {Array}
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

  /**
   * creates or updates user profile stored via API POST or PUT request
   * @param up
   * @returns {Promise<any | never>|*}
   */
  saveUserProfile(up){
    this.userinfo=up;
    if (up.hasOwnProperty('_etag') && up.hasOwnProperty('_id'))
      return this.putUserprofile(up);
    else
      return this.postUserprofile(up)
        .then(data=>{
          this.userinfo._id = data._id;
          this.userinfo._etag = data._etag;
          return data;
    })
  }
}

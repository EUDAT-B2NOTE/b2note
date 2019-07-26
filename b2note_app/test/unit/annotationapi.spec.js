import {EventAggregator} from 'aurelia-event-aggregator';
import {HttpClient} from 'aurelia-fetch-client';

jest.mock('aurelia-event-aggregator', () => ({
  EventAggregator: {
    publish: jest.fn()
  },
  HttpClient: {
    publish: jest.fn()
  }
}));

import {AnnotationApi} from '../../src/components/annotationapi';

describe('Annotation Component', () => {
  let api;
  beforeEach(() => {
    api = new AnnotationApi(EventAggregator,HttpClient);
  });
  test('constructor is defined', () => {
    expect(api.constructor).toBeDefined();
  });
  test('push modify delete query record', () =>{
    expect(api.pushQueryitem({logic:'',type:'semantic',value:'alkaloid'})).toBe(0);
    expect(api.pushQueryitem({logic:'AND',type:'keyword',value:'strychnine'})).toBe(1);
    expect(api.pushQueryitem({logic:'OR',type:'semantic',value:'amino acid'})).toBe(2);
    expect(api.pushQueryitem({logic:'AND',type:'keyword',value:'glycine'})).toBe(3);
    api.deleteQueryitem(3);
    expect(api.pushQueryitem({logic:'AND',type:'semantic',value:'glycine'})).toBe(3);
    api.deleteQueryitem(2); //delete everything up to 2-nd
    expect(api.pushQueryitem({logic:'OR',type:'semantic',value:'amino acid'})).toBe(2);
    expect(api.pushQueryitem({logic:'AND',type:'keyword',value:'glycine'})).toBe(3);
    api.modifyQueryitem(1,{logic:'AND',type:'semantic',value:'strychnine'});
  });

  test('search creating query record',() =>{
    let q1 = api.createQueryitem({logic:"",type:'semantic',value:'alkaloid'});
    expect(q1).toBe("{\"body.purpose\": \"tagging\",\"body.items\":{\"$elemMatch\":{\"value\":\"alkaloid\"}}}");
    let q2 = api.createQueryitem({logic:'AND',type:'keyword',value:'strychnine'});
    expect(q2).toBe("{\"body.purpose\": \"tagging\",\"body.type\":\"TextualBody\",\"body.value\":\"strychnine\"}");


    expect(api.pushQueryitem({logic:"",type:'semantic',value:'alkaloid'})).toBe(0);
    expect(api.pushQueryitem({logic:'AND',type:'keyword',value:'strychnine'})).toBe(1);
    expect(api.query.length).toBe(2);

    let q3 = api.createQueryRecord(api.query);
    expect(q3).toBe("{\"$and\": [{\"body.purpose\": \"tagging\",\"body.items\":{\"$elemMatch\":{\"value\":\"alkaloid\"}}}, {\"body.purpose\": \"tagging\",\"body.type\":\"TextualBody\",\"body.value\":\"strychnine\"}]}");
    expect(api.pushQueryitem({logic:'OR',type:'keyword',value:'glycine'})).toBe(2);
    let q4 = api.createQueryRecord(api.query);
    expect(q4).toBe("{\"$and\": [{\"body.purpose\": \"tagging\",\"body.items\":{\"$elemMatch\":{\"value\":\"alkaloid\"}}}, {\"$or\": [{\"body.purpose\": \"tagging\",\"body.type\":\"TextualBody\",\"body.value\":\"strychnine\"}, {\"body.purpose\": \"tagging\",\"body.type\":\"TextualBody\",\"body.value\":\"glycine\"}]}]}");

  });

});

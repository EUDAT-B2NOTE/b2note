import "isomorphic-fetch"; //required if tested component use fetch api
import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Search Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/search'))
      .inView("<search></search>")

  });

  afterEach(() => component.dispose());

  it('should render Search', done => {
    component.create(bootstrap).then(() => {
        const nameElement = document.getElementsByTagName('h3')[0];
        expect(nameElement.innerHTML).toBe('Search')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

  it('should have input tag', done =>{
    component.create(bootstrap).then(()=> {
      const inputElement = document.getElementsByTagName('input');
      expect(inputElement.length).toBeGreaterThan(0)
      done();
    }).catch(e => {
      fail(e);
      done();
    });
  })
  it('should have modify and search button', done =>{
    component.create(bootstrap).then(()=> {
      let inputElement = document.getElementsByTagName('button')[0];
      expect(inputElement.innerHTML).toContain('Modify')
      inputElement = document.getElementsByTagName('button')[4];
      expect(inputElement.innerHTML).toContain('Search')
      done();
    }).catch(e => {
      fail(e);
      done();
    });
  })

});

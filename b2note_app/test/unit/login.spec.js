import "isomorphic-fetch";  //required if tested component use fetch api
import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Login Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/login'))
      .inView("<login></login>")

  });

  afterEach(() => component.dispose());

  it('should render login or logout button', done => {
    component.create(bootstrap).then(() => {
        let element = document.getElementsByTagName('a')[0];
        //console.log('login test',nameElement);
        expect(element.innerHTML).toContain('Login')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

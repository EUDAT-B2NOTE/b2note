import "isomorphic-fetch";  //required if tested component use fetch api
import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Logout Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/logout'))
      .inView("<logout></logout>")

  });

  afterEach(() => component.dispose());

  it('should render logout button', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('a')[0];
        expect(nameElement.innerHTML).toContain('Logout')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

import "isomorphic-fetch";  //required if tested component use fetch api
import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Account Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/account'))
      .inView("<account></account>")

  });

  afterEach(() => component.dispose());

  it('should render table', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('table')[0];
        expect(nameElement.innerHTML).toContain('Annotator pseudonym');
        nameElement = document.getElementsByTagName('table')[1];
        expect(nameElement.innerHTML).toContain('B2NOTE backend server endpoint:');
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

  it('should render settings and account info', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('h3')[0];
        expect(nameElement.innerHTML).toContain('User account')
 nameElement = document.getElementsByTagName('h3')[1];
        expect(nameElement.innerHTML).toContain('Setting')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

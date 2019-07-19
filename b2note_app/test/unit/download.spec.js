import "isomorphic-fetch";  //required if tested component use fetch api
import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Download Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/download'))
      .inView("<download></download>")

  });

  afterEach(() => component.dispose());

  it('should render download buttons', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('button')[0];
        expect(nameElement.innerHTML).toContain('All my');
        nameElement = document.getElementsByTagName('button')[1];
        expect(nameElement.innerHTML).toContain('All annotations');
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

  it('should render json and rdf references', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('a')[0];
        expect(nameElement.innerHTML).toContain('JSON')
 nameElement = document.getElementsByTagName('a')[1];
        expect(nameElement.innerHTML).toContain('RDF')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

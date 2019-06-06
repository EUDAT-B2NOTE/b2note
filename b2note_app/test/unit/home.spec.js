import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Home Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/home'))
      .inView("<home></home>")

  });

  afterEach(() => component.dispose());

  it('should render Home', done => {
    component.create(bootstrap).then(() => {
        const nameElement = document.getElementsByTagName('a')[0];
        expect(nameElement.innerHTML).toBe('Semantic tag');
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

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
        const nameElement = document.getElementsByTagName('h1')[0];
        console.log('document:',document.getElementsByTagName('body')[0].innerHTML);
        expect(nameElement.innerHTML).toBe('Home')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

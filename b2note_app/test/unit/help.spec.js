import {bootstrap} from 'aurelia-bootstrapper';
import {StageComponent} from 'aurelia-testing';
import {PLATFORM} from 'aurelia-pal';

describe('Stage Help Component', () => {
  let component;

  beforeEach(() => {
    component = StageComponent
      .withResources(PLATFORM.moduleName('pages/help'))
      .inView("<help></help>")

  });

  afterEach(() => component.dispose());

  it('should render help, login page, registration and main page sections', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('h3')[0];
        expect(nameElement.innerHTML).toContain('Help')
        nameElement = document.getElementsByTagName('h4')[0];
        expect(nameElement.innerHTML).toContain('Login page')
      nameElement = document.getElementsByTagName('h4')[1];
        expect(nameElement.innerHTML).toContain('Registration')
      nameElement = document.getElementsByTagName('h4')[2];
        expect(nameElement.innerHTML).toContain('Main page')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

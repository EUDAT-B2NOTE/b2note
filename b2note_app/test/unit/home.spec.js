import "isomorphic-fetch";  //required if tested component use fetch api
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

  it('should render links to annotation type', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('a')[0];
        expect(nameElement.innerHTML).toContain('Semantic annotation');
        nameElement = document.getElementsByTagName('a')[1];
        expect(nameElement.innerHTML).toContain('Free-text keywords');
        nameElement = document.getElementsByTagName('a')[2];
        expect(nameElement.innerHTML).toContain('Comment');
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

  it('should render inputs and text area', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('input')[0];
        expect(nameElement.getAttribute('placeholder')).toContain('uri')

        nameElement = document.getElementsByTagName('input')[1];
        expect(nameElement.getAttribute('placeholder')).toContain('uri')
        nameElement = document.getElementsByTagName('input')[2];
        // TODO autocomplete element test
        // expect(nameElement.getAttribute('placeholder')).toContain('tag')

        nameElement = document.getElementsByTagName('input')[3];
        expect(nameElement.getAttribute('placeholder')).toContain('keyword')

        nameElement = document.getElementsByTagName('textarea')[0];
        expect(nameElement.getAttribute('placeholder')).toContain('comment')
        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

  it('should render create and accordion buttons', done => {
    component.create(bootstrap).then(() => {
        let nameElement = document.getElementsByTagName('button')[0];
        expect(nameElement.innerHTML).toContain('Create')
        nameElement = document.getElementsByTagName('button')[1];
        expect(nameElement.innerHTML).toContain('Create')
        nameElement = document.getElementsByTagName('button')[2];
        expect(nameElement.innerHTML).toContain('Semantic')
        nameElement = document.getElementsByTagName('button')[3];
        expect(nameElement.innerHTML).toContain('Keyword')
        nameElement = document.getElementsByTagName('button')[4];
        expect(nameElement.innerHTML).toContain('Cancel')
       //nameElement = document.getElementsByTagName('button')[3];
        //expect(nameElement.innerHTML).toContain('OK')
        nameElement = document.getElementsByTagName('button')[5];
        expect(nameElement.innerHTML).toContain('Create')
        nameElement = document.getElementsByTagName('button')[6];
        expect(nameElement.innerHTML).toContain('All')

        done();
    }).catch(e => {
      fail(e);
      done();
    });
  });

});

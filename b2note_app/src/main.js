import 'core-js/stable';
import 'regenerator-runtime/runtime';
import environment from './environment';
import {PLATFORM} from 'aurelia-pal';

export function configure(aurelia) {
  aurelia.use
    .standardConfiguration()
    .feature(PLATFORM.moduleName('resources/index'));

  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');


  if (environment.testing) {
    aurelia.use.plugin(PLATFORM.moduleName('aurelia-testing'));
  }

  aurelia.start().then(() => aurelia.setRoot(PLATFORM.moduleName('webcomponent/b2note')));
  //to include other main modules - reference them bellow
  PLATFORM.moduleName('webcomponent/main');
  PLATFORM.moduleName('webcomponent/webcomponent');
}

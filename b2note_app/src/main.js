/**
 * main b2note function to be referenced by <body aurelia-app="main"></body>
 * sets aurelia config and the root component to be displayed
 * @param aurelia
 *
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import 'core-js/stable';
import 'regenerator-runtime/runtime';
import environment from './environment';
import {PLATFORM} from 'aurelia-pal';
//import '@babel/polyfill';

export function configure(aurelia) {
  aurelia.use
    .standardConfiguration()
    .feature(PLATFORM.moduleName('resources/index'));

  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');

  if (environment.testing) {
    aurelia.use.plugin(PLATFORM.moduleName('aurelia-testing'));
  }

  aurelia.start().then(() => aurelia.setRoot(PLATFORM.moduleName('widget/b2note')));

  //to include other main modules in webpack bundle - just reference them bellow by PLATFORM.moduleName()
  PLATFORM.moduleName('webcomponent/b2note');
  //PLATFORM.moduleName('aurelia-autocomplete');
}

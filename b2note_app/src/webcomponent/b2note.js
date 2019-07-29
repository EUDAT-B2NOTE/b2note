/**
 * Main function for reffering B2Note as Web component
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import 'core-js/stable';
import 'regenerator-runtime/runtime';
import { CustomElementRegistry } from 'aurelia-web-components';
import {PLATFORM} from 'aurelia-pal';
import environment from '../environment';
//import '@babel/polyfill';

export function configure(aurelia) {
    aurelia.use
      .basicConfiguration()
      .plugin(PLATFORM.moduleName('aurelia-history-browser'))
      .plugin(PLATFORM.moduleName('aurelia-templating-resources'))
      .plugin(PLATFORM.moduleName('aurelia-templating-router'))
      .feature(PLATFORM.moduleName('resources/index'))
      .globalResources(PLATFORM.moduleName('widget/b2note'))
      .globalResources(PLATFORM.moduleName('pages/search'))
      .globalResources(PLATFORM.moduleName('pages/home'))
      .globalResources(PLATFORM.moduleName('pages/help'))

  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');

  aurelia.start().then(() => {
    const registry = aurelia.container.get(CustomElementRegistry);
    registry.fallbackPrefix='b2note-';
    registry.useGlobalElements();

  });
}

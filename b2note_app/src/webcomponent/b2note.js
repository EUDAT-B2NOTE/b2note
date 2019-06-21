/**
 * Main function for reffering B2Note as Web component
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */
import { CustomElementRegistry } from 'aurelia-web-components';
import {PLATFORM} from 'aurelia-pal';
import environment from '../environment';

export function configure(aurelia) {
    aurelia.use
      .basicConfiguration()
      .globalResources(PLATFORM.moduleName('widget/b2note'))
      .globalResources(PLATFORM.moduleName('components/arraysearchdialog'))
      .globalResources(PLATFORM.moduleName('pages/search'))
      .globalResources(PLATFORM.moduleName('pages/home'))
      .globalResources(PLATFORM.moduleName('pages/help'))
      .plugin(PLATFORM.moduleName('aurelia-history-browser'))
      .plugin(PLATFORM.moduleName('aurelia-templating-router'))


  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');

  aurelia.start().then(() => {
    const registry = aurelia.container.get(CustomElementRegistry);
    registry.useGlobalElements();
  });
}

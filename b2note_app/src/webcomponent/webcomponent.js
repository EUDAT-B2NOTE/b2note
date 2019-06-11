import { CustomElementRegistry } from 'aurelia-web-components';
import {PLATFORM} from 'aurelia-pal';
import environment from '../environment';

export function configure(aurelia) {
    aurelia.use
      .basicConfiguration()
      .globalResources(PLATFORM.moduleName('components/arraysearchdialog'))
      .globalResources(PLATFORM.moduleName('webcomponent/b2note'))
      .globalResources(PLATFORM.moduleName('pages/home'))
      .globalResources(PLATFORM.moduleName('pages/search2'))
      .globalResources(PLATFORM.moduleName('pages/help'))


  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');


  if (environment.testing) {
    aurelia.use.plugin(PLATFORM.moduleName('aurelia-testing'));
  }

  aurelia.start().then(() => {
    const registry = aurelia.container.get(CustomElementRegistry);

    registry.useGlobalElements();

  });
}

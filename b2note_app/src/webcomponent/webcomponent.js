import { CustomElementRegistry } from 'aurelia-web-components';
import {PLATFORM} from 'aurelia-pal';

export function configure(aurelia) {
    aurelia.use
      .basicConfiguration()
      .globalResources(PLATFORM.moduleName('components/arraysearchdialog'));

  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');


  if (environment.testing) {
    aurelia.use.plugin(PLATFORM.moduleName('aurelia-testing'));
  }

  aurelia.start().then(() => {
    const registry = aurelia.container.get(CustomElementRegistry);
    registry.useGlobalElements();
  });
}

import {PLATFORM} from 'aurelia-pal';
import 'font-awesome/css/font-awesome.css';
import {AnnotationApi} from './components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)

export class App {

  constructor(api) {
    this.api = api;
  }

 configureRouter(config, router) {
    config.title = 'B2Note';
    config.map([
      {
        route: ['', 'home'],
        name: 'home',
        moduleId: PLATFORM.moduleName('./pages/home'),
        nav: true,
        title: 'Home',
        settings: { icon: 'fa fa-home'}
      },
      {
        route: 'account',
        name: 'account',
        moduleId: PLATFORM.moduleName('./pages/account'),
        nav: true,
        title: 'Account Settings',
        settings: { icon: 'fa fa-user' }
      },
      {
        route: 'search',
        name: 'search',
        moduleId: PLATFORM.moduleName('./pages/search'),
        nav: true,
        title: 'Search',
        settings: { icon: 'fa fa-search'}
      },
      {
        route: 'download',
        name: 'download',
        moduleId: PLATFORM.moduleName('./pages/download'),
        nav: true,
        title: 'Download',
        settings: { icon: 'fa fa-download'}
      },
      {
        route: 'help',
        name: 'help',
        moduleId: PLATFORM.moduleName('./pages/help'),
        nav: true,
        title: 'Help',
        settings: { icon: 'fa fa-question-circle'}
      },
      {
        route: 'logout',
        name: 'logout',
        moduleId: PLATFORM.moduleName('./pages/logout'),
        nav: true,
        title: 'Logout',
        settings: { icon: 'fa fa-sign-out'}
      }
    ]);
    this.router = router;
  }
}

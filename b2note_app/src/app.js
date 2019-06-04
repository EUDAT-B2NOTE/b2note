import {PLATFORM} from 'aurelia-pal';
import 'font-awesome/css/font-awesome.css';

export class App {

 configureRouter(config, router) {
    config.title = 'B2Note';
    config.map([
      {
        route: ['', 'home'],
        name: 'home',
        moduleId: PLATFORM.moduleName('./pages/home'),
        nav: true,
        title: 'Home',
        settings: 'fa fa-home'
      },
      {
        route: 'account',
        name: 'account',
        moduleId: PLATFORM.moduleName('./pages/account'),
        nav: true,
        title: 'Account Settings',
        settings: 'fa fa-user'
      },
      {
        route: 'search',
        name: 'search',
        moduleId: PLATFORM.moduleName('./pages/search'),
        nav: true,
        title: 'Search',
        settings: 'fa fa-search'
      },
      {
        route: 'download',
        name: 'download',
        moduleId: PLATFORM.moduleName('./pages/download'),
        nav: true,
        title: 'Download',
        settings: 'fa fa-download'
      },
      {
        route: 'help',
        name: 'help',
        moduleId: PLATFORM.moduleName('./pages/help'),
        nav: true,
        title: 'Help',
        settings: 'fa fa-question-circle'
      },
      {
        route: 'logout',
        name: 'logout',
        moduleId: PLATFORM.moduleName('./pages/logout'),
        nav: true,
        title: 'Logout',
        settings: 'fa fa-sign-out'
      }
    ]);

    this.router = router;
  }
}

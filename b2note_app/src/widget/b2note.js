/**
 * main widget component to be displayed - tabs are rendered as router buttons,
 * icons are defined in custom settings property
 * all pages are references by PLATFORM.moduleName()
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

import {PLATFORM} from 'aurelia-pal';
import 'font-awesome/css/font-awesome.css';
import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class B2note {

  constructor(api) {
    this.api = api;
  }

 configureRouter(config, router) {
    console.log('configurerouter()',config,router);
    config.title = 'B2Note';
    config.map([
      {
        route: ['', 'b2note_home'],
        name: 'b2note_home',
        moduleId: PLATFORM.moduleName('../pages/home'),
        nav: true,
        title: 'Home',
        settings: { icon: 'fa fa-home'}
      },
      {
        route: 'b2note_account',
        name: 'b2note_account',
        moduleId: PLATFORM.moduleName('../pages/account'),
        nav: true,
        title: 'Account Settings',
        settings: { icon: 'fa fa-user' }
      },
      {
        route: 'b2note_search',
        name: 'b2note_search',
        moduleId: PLATFORM.moduleName('../pages/search'),
        nav: true,
        title: 'Search',
        settings: { icon: 'fa fa-search'}
      },
      {
        route: 'b2note_download',
        name: 'b2note_download',
        moduleId: PLATFORM.moduleName('../pages/download'),
        nav: true,
        title: 'Download',
        settings: { icon: 'fa fa-download'}
      },
      {
        route: 'b2note_help',
        name: 'b2note_help',
        moduleId: PLATFORM.moduleName('../pages/help'),
        nav: true,
        title: 'Help',
        settings: { icon: 'fa fa-question-circle'}
      },
      {
        route: 'b2note_login',
        name: 'b2note_login',
        moduleId: PLATFORM.moduleName('../pages/login'),
        nav: true,
        title: 'Login',
        settings: { icon: 'fa fa-sign-in'}
      },
      {
        route: 'b2note_logout',
        name: 'b2note_logout',
        moduleId: PLATFORM.moduleName('../pages/logout'),
        nav: true,
        title: 'Logout',
        settings: { icon: 'fa fa-sign-out'}
      }
    ]);
    this.router = router;
  }
}

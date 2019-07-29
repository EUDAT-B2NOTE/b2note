/**
 * main widget component to be displayed - tabs are rendered as router buttons,
 * icons are defined in custom settings property
 * all pages are references by PLATFORM.moduleName()
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import {PLATFORM} from 'aurelia-pal';
import 'font-awesome/css/font-awesome.css';
import {AnnotationApi} from '../components/annotationapi';
import {inject,bindable} from 'aurelia-framework';

@inject(AnnotationApi)
export class B2note {
  @bindable targetid;
  @bindable targetsource;

  constructor(api) {
    this.api = api;
  }

  bind(){
    console.log('widget.b2note.bind() id,source',this.targetid,this.targetsource)
    if (this.targetid) this.api.target.id = this.targetid;
    if (this.targetsource) this.api.target.source = this.targetsource;
  }

  //webcomponent workaround to show router-view
  async attached(){
        //console.log('widget.b2note.attached()')
        await sleep(200);
        //console.log('widget.b2note.attached() navigate')
        //ugly workaround - navigate to account and back to render route
    if (!this.api.homeattached) {
      console.log('widget.b2note.attached() render router-view workaround')
      this.router.navigate('b2note_download')
      this.router.navigateBack()
    }
  }

 configureRouter(config, router) {
    //console.log('widget.b2note.configurerouter()',config,router);
    config.title = 'B2Note';

    config.map([
      {
        route: ['','b2note_home','b2note_home/*target'],
        name: 'home',
        moduleId: PLATFORM.moduleName('../pages/home'),
        nav: true,
        title: 'Home',
        href:'#/',
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
        title: 'Login/Logout',
        settings: { icon: '',iconlogin:'fa fa-sign-in',iconlogout:'fa fa-sign-out'}
      }
    ]);
    this.router=router;
    this.api.router = router;
  }
}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Navigation Bar component renders icons and appropriate
 * anchors for pages
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */
import {EventAggregator} from 'aurelia-event-aggregator';
import {Userinfo} from './messages'
import {inject} from 'aurelia-framework';
import {Router} from 'aurelia-router';



@inject(EventAggregator,Router)
export class Navbar {
  //@bindable router;

  constructor(ea,router) {
    this.username = "";
    this.ea = ea;
    this.loggedin=false;
    //console.log('Navbar()')
    this.router=router;
  }

  attached() {
    //console.log('Navbar.attached(), router:',this.router)
    //console.log('Navbar.attached(), router:',this.router.navigation)
    this.navigation=this.router.navigation; //fix - router navbar not rendered in webcomponent
    this.s1 = this.ea.subscribe(Userinfo, msg => this.changeUserInfo(msg.userinfo));
    //debug webcomponents routing - navigate to home doesn't work
    //console.log('navigate to home')
    //this.router.navigate('b2note_home')
  }

  detached() {
    this.s1.dispose();
  }

  changeUserInfo(userinfo) {
    //console.log('changeuserinfo:', userinfo);
    this.username = userinfo.pseudo;
    this.loggedin = (userinfo.id) && (userinfo.id.length>0);
  }

}

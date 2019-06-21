/**
 * Navigation Bar component renders icons and appropriate
 * anchors for pages
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */
import {EventAggregator} from 'aurelia-event-aggregator';
import {Userinfo} from './messages'
import {bindable, inject} from 'aurelia-framework';

@inject(EventAggregator)
export class Navbar {
  @bindable router;

  constructor(ea) {
    this.username = "";
    this.ea = ea;
  }

  attached() {
    this.s1 = this.ea.subscribe(Userinfo, msg => this.changeUserInfo(msg.userinfo));
  }

  detached() {
    this.s1.dispose();
  }

  changeUserInfo(userinfo) {
    console.log('changeuserinfo:', userinfo);
    this.username = userinfo.pseudo;
  }

}

import {EventAggregator} from 'aurelia-event-aggregator';
import {Userinfo} from './components/messages'
import {bindable,inject} from 'aurelia-framework';

@inject(EventAggregator)
export class Navbar{
  @bindable router;
  constructor(ea){
    this.username="Guest";
    this.ea = ea;
  }

   attached(){
      this.s1=this.ea.subscribe(Userinfo, msg => this.changeUserInfo(msg.userinfo));
    }
    detached() {
      this.s1.dispose();
    }

    changeUserInfo(userinfo){
    console.log('changeuserinfo:',userinfo);
      this.username=userinfo.username;
    }

}

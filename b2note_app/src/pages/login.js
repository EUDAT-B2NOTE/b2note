/**
 * implements login page - redirect to b2access and optional google endpoints
 * in backend api
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since v2.0
 */

import {AnnotationApi} from '../components/annotationapi';
import {inject} from 'aurelia-framework';

@inject(AnnotationApi)
export class Login {
  constructor(api) {
    this.allowgoogle = false;
    this.api = api;
    this.popup=undefined;
  //receives message from popup window, define as arrow function due to eventlistener
    this.receiveMessage = event =>
    {
      //document.getElementById(this.target).innerHTML=event.data;
      //document.getElementById(this.target).setAttribute("href",event.data);
      console.log('received messages, closing popup, navigating to home');
      if (this.popup) this.popup.close();
      if (this.api && this.api.router) this.api.router.navigate('b2note_home');
    }
  }

  attached(){
    this.allowgoogle = this.api.allowgoogle;
    this.api.isLoggedIn()
      .then(data => {
        this.loggedin = data;
      })
      .catch(error =>{
        console.log('some error occured  when isloggedin()')
      })
    this.iframe=Login.inIframe();
    //register listener for receiving messages
    window.addEventListener("message", this.receiveMessage, false);
  }

  static inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
    }


  detached() {
    window.removeEventListener("message", this.receiveMessage)
  }

  //opens popup window in defined location
  /**
   * login in iframe needs to open popup - when popup is opened then close it
   */
  popupLogin() {
    console.log('opening popup window to login')
    this.popup=window.open('/api/b2access/login?next=/b2note/', 'B2Access', 'width=800');
    return false;
  }
}

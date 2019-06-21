/**
 * Messages exchanged via EventAggregator pattern among components
 *
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */

export class Userinfo {
  constructor(userinfo) {
    this.userinfo = userinfo;
  }
}


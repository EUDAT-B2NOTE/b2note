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

// domid  - id of DOM element to address this message
// value - value of annotation
export class Taginfo {
  constructor(taginfo) {
    this.taginfo = taginfo;
  }
}

export class Updateall{
  constructor(taginfo) {
    this.taginfo = taginfo;
  }

}
export class Updatefile{
  constructor(taginfo) {
    this.taginfo = taginfo;
  }
}


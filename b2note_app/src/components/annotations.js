export class Annotations {
  constructor() {
    this.showall = false;
    this.showfile = false;
  }

  switchAll() {
    this.showall = !this.showall;
  }

  switchFile() {
    this.showfile = !this.showfile;
  }
}

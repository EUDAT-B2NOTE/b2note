/**
 * Annotattion component with accordion to show overview about existing annotations
 * @todo render table with annotation numbers
 * @author Tomas Kulhanek <https://github.com/TomasKulhanek>
 * @since 06/2019
 */
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

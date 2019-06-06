export class Home {
constructor(){
  this.tabs = [
      { id: 'tab1', label: 'Semantic annotation'},
      { id: 'tab2', label: 'Free-text keywords'},
      { id: 'tab3', label: 'Comment           ' }
    ];
  this.active = 'tab1';
}

switchtab(tabid){
  this.active = tabid;
  return true;
}
}

export class Home {
constructor(){
  this.tabs = [
      { id: 'tab1', label: 'Semantic annotation'},
      { id: 'tab2', label: 'Free-text keywords'},
      { id: 'tab3', label: 'Comment           ' }
    ];
  this.active = 'tab1';
  this.annotationsemantic='';
  this.annotationkeyword='';
  this.annotationcomment='';
}

switchtab(tabid){
  this.active = tabid;
  return true;
}

createSemantic(){
  console.log('create semantic:',this.annotationsemantic)
}

createKeyword(){
  console.log('create keyword:',this.annotationkeyword)

}
createComment(){
  console.log('create semantic:',this.annotationcomment)

}
}

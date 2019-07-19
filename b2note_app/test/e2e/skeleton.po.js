export class PageObjectSkeleton {
  getCurrentPageTitle() {
    return browser.getTitle();
  }

  getPageTabs(){
    return element.all(by.css('navbar > nav > ul > li > a'));
    let hrefs = [];
    console.log('getpagetabs length',anchors.length);
    for (let i=0;i< anchors.length;i++){

        let value = anchors[i].getAttribute('href');//.then(function(value){hrefs.push(value)})
        hrefs.push(value);
      }

    return hrefs;
  }

  getjsoncontent(){

  }
}

export class PageObjectWelcome {
  getGreeting() {
    return element(by.tagName('h3')).getText();
  }
}

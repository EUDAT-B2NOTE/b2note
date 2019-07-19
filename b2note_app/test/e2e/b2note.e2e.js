import {PageObjectWelcome} from './welcome.po';
import {PageObjectSkeleton} from './skeleton.po';
import {config} from '../protractor.conf';

describe('aurelia skeleton app', function() {
  let poWelcome;
  let poSkeleton;


  beforeEach(async () => {
    poSkeleton = new PageObjectSkeleton();
    poWelcome = new PageObjectWelcome();

    await browser.loadAndWaitForAureliaPage(`http://localhost:${config.port}`);
  });

  it('should load the page and display the initial page title', async () => {
    await expect(await poSkeleton.getCurrentPageTitle()).toContain('B2Note');
  });

  it('should display Create annotaiton on first screen', async () => {
    await expect(await poWelcome.getGreeting()).toBe('Create annotation');
  });

  it('should display 9 navigation tabs with hrefs', async () => {
    let items = await poSkeleton.getPageTabs();//.then(function(items){
      //console.log('items lenght',items.length);
      expect(items.length).toBe(6);
      expect(await items[0].getAttribute('href')).toMatch(/.*#\/$/);
      expect(await items[1].getAttribute('href')).toMatch(/.*#\/b2note_account$/);
      expect(await items[5].getAttribute('href')).toMatch(/.*#\/b2note_login$/);
      expect(await items[4].getAttribute('href')).toMatch(/.*#\/b2note_help$/);
    });

});

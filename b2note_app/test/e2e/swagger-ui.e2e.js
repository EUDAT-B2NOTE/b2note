import {config} from '../protractor.conf';

describe('swagger-ui app', function() {


  beforeEach(async () => {
    await browser.get(`http://localhost:${config.port}/swagger-ui.html`);
  });

  it('should load the initial page and display the initial page title', async () => {
    await expect(await browser.getTitle()).toContain('Swagger UI');
  });

});

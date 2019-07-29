# B2NOTE APP

Frontend application consisting of web pages UI and logic in order to support data annotation and 
relevant use case. This component is bootstrapped by [aurelia-cli](https://github.com/aurelia/cli) and bundled using Webpack (https://aurelia.io/docs/cli/webpack).

- `/src` contains all source code for web pages and it's components
- `/dist` contains bundled (and minified) app ready to use in web server, default 'index.html' renders the b2note
widget. Other *.html contains sample code to integrate b2note widget into web application. `swagger-ui.html` renders 
Open-API as rendered by swagger plugin.
- `/aurelia_project` contains configuration files for CLI scripts for developmnent and building
- `/test` contains unit and e2e tests 

## Development environmnent 

Run `au run`, then open `http://localhost:8080`

To open browser automatically, do `au run --open`.

To change dev server port, do `au run --port 8888`.

To enable Webpack Bundle Analyzer, do `au run --analyze`.

To enable hot module reload, do `au run --hmr`.

## Build for development and production

Run `au build --watch`. This will create `/dist` folder containing webpack bundled application and 
static files coppied from `/static` folder.

Run `au build --env prod` to build the app for production environment

## Tests

Unit tests are at `/test/unit/` directory. End to end tests are et `/test/e2e/`.

You may need to add fetch polyfill if the component uses fetch api during it's lifecycle:
```javascript 
import "isomorphic-fetch";  //required if tested component use fetch api
```

Run `au test` (or `au jest`) to run unit tests. To run in watch mode, `au test --watch` or `au jest --watch`.

Router rendering or more complex tests and requires frontend to be reachable at localhost:8080.
 Thus launch the frontend-dev in advance by: `au run & sleep 10`

Run `au protrator` to run E2E tests using protractor framework.

## E2E tests in Travis-CI 

Travis CI container uses older version of chrome. The Protractor task downloads 'gecko' driver, which can fail on
'github rate limit exceeded'. 

If the dev app is not running, launch it before any other tests: `au run & sleep 10`

Run `au teste2e` in order to test without gecko and on Chrome version 73. 
 
## Webcomponents

Web components (https://www.webcomponents.org) is standardized way to export complex web application into reusable component.
B2NOTE app exports custom-elements for these components using 'b2note-' prefix:

- src/widget/b2note as `<b2note-b2note targetsource="" targetid="">`
- src/pages/search as `<b2note-search>`
- src/pages/home as `<b2note-home>`
- src/pages/help as `<b2note-help>`

Further webcomponents can be exported by ammending the `src/webcomponent/b2note.js` and building the app.bundle.js.
 
Script with bundle `b2note_app/dist/app.bundle.js` can be used to add b2note web components into any web application or web page.

The following HTML snippet loads first the `app.bundle.js` script and use custom-element `<b2note-b2note>` with custom attributes
`targetid=""` and `targetsource=""` to specify target for annotation. There is additionally button to hide the `<div>` containing the custom element.

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>B2Note web component</title>
     <script type="module" src="app.bundle.js"></script>
  </head>
  <body aurelia-app="webcomponent/b2note">
  <h3>B2NOTE as web component</h3>
  <p>This is demo page for B2NOTE web component.</p>
  <div id="aucontainer2" style="float:right;width:33%">b2note-b2note
    <button onclick="document.getElementById('aucontainer2').hidden=true" title="close b2note component">x</button>
    <b2note-b2note targetsource="https://b2share.eudat.eu/records/39fa39965b314f658e4a198a78d7f6b5" targetid="http://hdl.handle.net/11304/3720bb44-831c-48f3-9847-6988a41236e1"></b2note-b2note>
  <br/>
  </div>
  </body>
</html>
```

## Embedded iframe

For backward compatibility, embedding IFRAME is supported. See
https://b2note-docs.readthedocs.io/en/latest/integration/widget.html


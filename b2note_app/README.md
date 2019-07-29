# B2NOTE APP

Frontend application consisting of web pages UI and logic in order to support data annotation and 
relevant use case. This component is bootstrapped by [aurelia-cli](https://github.com/aurelia/cli). For more information, go to https://aurelia.io/docs/cli/webpack

## Development environmnent 

Run `au run`, then open `http://localhost:8080`

To open browser automatically, do `au run --open`.

To change dev server port, do `au run --port 8888`.

To enable Webpack Bundle Analyzer, do `au run --analyze`.

To enable hot module reload, do `au run --hmr`.

## Build for production

Run `au build --env prod`.

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

- widget/b2note
- pages/search
- pages/home
- pages/help

Further webcomponents can be exported by ammending the `src/webcomponent/b2note.js`.
 
Script with bundle `b2note_app/dist/app.bundle.js` can be used to add b2note web components into any web application or web page.

The following HTML snippet loads first the `app.bundle.js` script containing b2note widget.
Then within the <body> there is used custom attribute aurelia-app=”webcomponent/b2note” which registers b2note components into custom elements.
Within the <body> the following custom elements can be used:
<au-b2note> renders full b2note widget
<au-search> renders search dialog of b2note widget
<au-home> renders home page (create and annotation overview) of b2note widget

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
  <p>au-b2note</p>
  <au-b2note></au-b2note>
</body>
</html>


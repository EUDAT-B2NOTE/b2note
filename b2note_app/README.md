# B2NOTE APP

This project is bootstrapped by [aurelia-cli](https://github.com/aurelia/cli).

For more information, go to https://aurelia.io/docs/cli/webpack

## Run dev app

Run `au run`, then open `http://localhost:8080`

To open browser automatically, do `au run --open`.

To change dev server port, do `au run --port 8888`.

To enable Webpack Bundle Analyzer, do `au run --analyze`.

To enable hot module reload, do `au run --hmr`.

## Build for production

Run `au build --env prod`.

## Unit tests

Unit tests are at `/test/unit/` directory. Every basic component or page should have a unit test to cover at least basic functionality.
See `test/unit/home.spec.js` how to test component and rendered parts.

You may need to add fetch polyfill if the component uses fetch api during it's lifecycle:
```javascript 
import "isomorphic-fetch";  //required if tested component use fetch api
```

Run `au test` (or `au jest`).

To run in watch mode, `au test --watch` or `au jest --watch`.


## E2E tests

End to end tests are et `test/e2e/`. Router rendering or more complex tests should be made there in order to test basic browser functionality. 

If the dev app is not running, launch it before
`au run & sleep 10`

Run `au protrator`

This will run E2E tests using protractor framework.

## E2E tests in Travis-CI 

Travis CI container uses older version of chrome. The Protractor task downloads 'gecko' driver, which can fail on
'github rate limit exceeded'. 

If the dev app is not running, launch it before any other tests: `au run & sleep 10`

Run `au teste2e` in order to test without gecko and on Chrome version 73. 
 

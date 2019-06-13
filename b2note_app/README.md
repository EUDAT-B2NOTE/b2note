# `b-2-note-app`

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

Run `au test` (or `au jest`).

To run in watch mode, `au test --watch` or `au jest --watch`.

## E2E tests

If the dev app is not running, launch it before
`au run & sleep 10`

Run `au protrator`

This will run E2E tests using protractor framework.

## E2E tests in Travis-CI 

Travis CI container uses older version of chrome. The Protractor task downloads 'gecko' driver, which can fail on
'github rate limit exceeded'. 

Run `au teste2e` in order to test without gecko and on Chrome verison 73. 
 

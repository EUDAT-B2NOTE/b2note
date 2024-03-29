const aureliaConfig = require('../aurelia_project/aurelia.json');
const port = aureliaConfig.platform.port;

exports.config = {
  port: port,

  baseUrl: `http://localhost:${port}/`,

  specs: [
    '**/*.e2e.js'
  ],

  exclude: [],

  framework: 'jasmine',

  allScriptsTimeout: 60000,

  jasmineNodeOpts: {
    showTiming: true,
    showColors: true,
    isVerbose: true,
    includeStackTrace: false,
    defaultTimeoutInterval: 10000
  },

  SELENIUM_PROMISE_MANAGER: false,

  directConnect: true,

  capabilities: {
    'browserName': 'chrome',
    'chromeOptions': {
      'args': [
        '--show-fps-counter',
        '--no-default-browser-check',
        '--no-first-run',
        '--disable-default-apps',
        '--disable-popup-blocking',
        '--disable-translate',
        '--disable-background-timer-throttling',
        '--disable-renderer-backgrounding',
        '--disable-device-discovery-notifications',
        /* enable these if you'd like to test using Chrome Headless */
          '--no-gpu',
          '--headless'

      ]
    }
  },

  onPrepare: function() {
    process.env.BABEL_TARGET = 'node';
    process.env.IN_PROTRACTOR = 'true';
    require('@babel/register');
  },

  plugins: [{
    package: 'aurelia-protractor-plugin'
  }],
};

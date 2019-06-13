import gulp from 'gulp';
var path = require('path');
var child_process = require('child_process');
const {protractor }  = require('gulp-protractor');

gulp.task('protractor', (cb) => {
  gulp.src('test/e2e/**/*.e2e.js')
    .pipe(protractor({configFile: 'test/protractor.conf.js'}))
    .on('error', cb)
    .on('end', cb);
});

function getProtractorBinary(binaryName){
    var winExt = /^win/.test(process.platform)? '.cmd' : '';
    var protractorBin = path.join('node_modules', '.bin', binaryName);
    return path.join(protractorBin, winExt);
}
//defining own webdriver-manager update - with params to disable gecko --gecko=false

gulp.task('protractor-install', function(done){
    child_process.spawn(getProtractorBinary('webdriver-manager'), ['update','--gecko=false','--versions.chrome=73.0.3683.68'], {
        stdio: 'inherit'
    }).once('close', done);
});

// Setting up the test task
export default gulp.series(
  //'webdriver_update',
  'protractor-install',
  'protractor'
);

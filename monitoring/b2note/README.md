B2NOTE probe
===========

Nagios probe for the B2NOTE service.
It is implemented as a bash script.

## Dependencies

curl

## Deployment

It is possible to just copy the script and the related configuration files to the wanted directory.  
Or to create a rpm package, following the next steps.  
Go to the directory monitoring/packaging.  
Execute the script create_rpm_package.sh.  
Deploy the rpm package.  
By default the script is place in:  
/usr/libexec/argo-monitoring/probes/b2note/check_b2note.sh  

## Usage
The script can be executed with the following input parameters:
```
Usage: check_b2note.sh [-h|-V|-d|-t time]
       -h help
       -V version
       -d debug enabled.
       -t timeout limit in seconds. The default is 30 s.
```
It just checks the responsivity of the server.

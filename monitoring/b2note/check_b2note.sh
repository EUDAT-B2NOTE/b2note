#!/bin/bash

# Script that checks the availability of the EUDAT-B2NOTE service

VERSION="0.1"
SUB_VERSION="0"

### Settings
# Nagios return codes
OK="0"
WARN="1"
CRITICAL="2"
UNKNOWN="3"

usage() {
	echo "This is a B2NOTE health check."
        echo "Usage: check_b2note.sh [-h|-V|-d|-t time]"
        echo "       -h help"
        echo "       -V version"
        echo "       -d debug enabled."
        echo "       -t timeout limit in seconds. The default is 30 s."
}

DEBUG=0

### End Settings

### Functions
function execute_checks() {
        if [ "$DEBUG" == "1" ]; then
                echo -e "Executing...\ncurl -m $TIMEOUT https://b2note.eudat.eu/solr/b2note_index/select 2>/dev/null | grep response | wc -l"
        fi
	
	CHECK1=`curl -m $TIMEOUT https://b2note.eudat.eu/solr/b2note_index/select 2>/dev/null`
	
	if [ "$?" != "0" ]; then
		echo "CRITICAL: timed out after $TIMEOUT seconds."
		return $CRITICAL
	fi

	CHECK2=`echo $CHECK1 | grep response | wc -w`
	
	if [ "$CHECK2" != "13" ]; then
		echo "UNKNOWN: service returned an unknown answer."
		return $UNKNOWN
	fi
	return $OK
}

### End Functions


### Execution
if [ "$#" -gt "3" ]; then
    usage
    exit $WARN
fi

while getopts "Vhdt:" opt; do
  if [ "$opt" == "?" ]; then
      exit $WARN
  fi
  declare "opt_$opt=${OPTARG:-0}"
done


if [ "$opt_h" == "0" ]; then
      usage
      exit $OK
fi

if [ "$opt_V" == "0" ]; then
      echo "version $VERSION"
      exit $OK
fi

if [ "$opt_d" == "0" ]; then
      DEBUG=1
fi

if [ "$opt_t" == "" ]; then
      TIMEOUT=30
else
      TIMEOUT=$opt_t
fi

execute_checks

EXIT_CODE=$?
if [ "$EXIT_CODE" != "0" ]; then
      exit $EXIT_CODE
fi

echo "B2NOTE probe passed"
exit $OK

#
# spec file for package nagios-plugins-eudat-b2note
#
# Copyright (c) 2018 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name:           nagios-plugins-eudat-b2note
Version:	%{_version}
Release:	%{_release}
License:	MIT License
Summary:	nagios probe for b2note
Url:		https://b2note.eudat.eu
Group:		Application
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%define _whoami %(whoami)
%define _b2notehomepackaging %(pwd)
%define _b2noteNagiosPackage /usr/libexec/argo-monitoring/probes/eudat-b2note
%define _b2noteNagiosTmp     /var/lib/argo-monitoring/eudat-b2note

%description
This nagios plugin provides the nessecary scripts to test b2note.

%prep
echo "the spec file directory is %{_b2notehomepackaging}"
echo "The user that built this is %{_whoami}"
# create string where git repo is started..
workingdir=`pwd`
cd %{_b2notehomepackaging}
cd ../b2note
b2notehome=`pwd`
cd $workingdir
# empty source directory and copy new files
rm -rf $RPM_SOURCE_DIR/*
cp -ar $b2notehome/* $RPM_SOURCE_DIR

%build
exit 0

%install
rm -rf %{buildroot}
mkdir -p $RPM_BUILD_ROOT%{_b2noteNagiosPackage}
mkdir -p $RPM_BUILD_ROOT%{_b2noteNagiosTmp}

cp $RPM_SOURCE_DIR/*.sh         $RPM_BUILD_ROOT%{_b2noteNagiosPackage}


%clean
rm -rf %{buildroot}

%files
# default attributes
%defattr(-,-,-,-)
# files
#include files
%{_b2noteNagiosPackage}
%{_b2noteNagiosTmp}
# attributes on files and directory's
%attr(-,nagios,nagios)   %{_b2noteNagiosPackage}
%attr(-,nagios,nagios)   %{_b2noteNagiosTmp}
%attr(750,nagios,nagios) %{_b2noteNagiosPackage}/*.sh
%doc

%post
%changelog
* Wed Jun 13 2018  Pablo Rodenas <pablo.rodenas@bsc.es> 1.0
- Initial version of b2note nagios plugin

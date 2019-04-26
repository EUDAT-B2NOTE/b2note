## B2NOTE [![Build Status](https://travis-ci.org/EUDAT-B2NOTE/b2note.svg?branch=master)](https://travis-ci.org/EUDAT-B2NOTE/b2note) [![Build Status](https://travis-ci.org/EUDAT-B2NOTE/b2note.svg?branch=development)](https://travis-ci.org/EUDAT-B2NOTE/b2note)


An [EUDAT](https://www.eudat.eu) service for creating, storing and managing annotations about online resources.
The data model used in B2Note is based on the [W3C web annotation data model](http://www.w3.org/TR/annotation-model/).
Further information in [1]

B2Note demo instance: https://b2note.bsc.es/devel

## Contributors

 Name  |  Affiliation 
-------|-------
Dr. Yann Le Franc   | e-Science Data Factory  
Dr. Antoine Brémaud | e-Science Data Factory  
Mr. Pablo Ródenas Barquero | Barcelona Supercomputing Center 
Dr. Tomas Kulhanek | e-Science Data Factory 

## Instructions for contributing

1) Fork
2) Commit
3) Submit pull request.
 
Further guidelines [github fork branch and pull request](https://gun.io/blog/how-to-github-fork-branch-and-pull-request/)

## Copyright

Copyright © e-Science Data Factory, 2015-2016

Copyright © Barcelona Supercomputing Center, 2015-2016


This software may not be used, sold, licensed, transferred, copied or reproduced in whole or in part in any manner or form or in or on any media by any person other than in accordance with the terms of the Licence Agreement supplied with the software, or otherwise without the prior written consent of the copyright owners.

This software is distributed WITHOUT ANY WARRANTY, express or implied relating to MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE, except where stated in the Licence Agreement supplied with the software.

>     Created By:    Yann Le Franc (PhD),          e-Science Data Factory;
>                    Antoine Brémaud (PhD),        e-Science Data Factory;
>                    Pablo Ródenas Barquero (BSc), Barcelona Supercomputing Center.
>
>     Created for Project:    EUDAT2020

EUDAT receives funding from the European Union's Horizon 2020 programme - DG CONNECT e-Infrastructures. Contract No. 654065

## Release notes
- upgraded to python 3.6, django 2.2, migrated from mongoengine to djongo 
- sqlite version 3.8 and above is required
- mongodb version 4.x is required

[1] In preparation for IEEE EMBC 2019.
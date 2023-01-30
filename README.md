# AusPIX-DGGS-crosswalk code

* Newly added geopandas code that greatly simplifies setup, is more robust and has no bespoke code. Use geopandas method.

This repo maintains code for various DGGS jobs.

The main code for building crosswalk tables is 
https://github.com/GeoscienceAustralia/AusPIX-crosswalk-code/blob/master/SupportingCode/Multiproc_enablement
this code needs to be matched with:
1) the shapefile geographies that need to be built into the table
2) A set of blank tiles for all Australa at DGGS level 4, each with the centroids of all 500,000+ DGGS level 10 cells 
(can be provided in an S3 bucket on request)

Final dataset will be 817 tiles with all the crosswalk information. These tiles, usually in shapefile format are pushed to one 
big PostGIS crosswalk database of about 200GB






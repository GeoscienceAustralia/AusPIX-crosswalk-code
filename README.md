# AusPIX-DGGS-crosswalk-table-API

This repo maintains code for the API over AusPIX Crosswalk Integration tables.
The aim is to allow access to integrated data for Australian Goverment and business.
At the moment, it is pointed to the National Crosswalk table Level 10 dataset which contains half a billion cells at 2.488 ha size for all mainland Australia.

Date: Novemeber 2020
 
This data cross-references a wide range of polygon and raster data, here is the out-put for one cell:

Information available for each cell:

'auspix_dggs': 'R7852372435',

'auspix_uri': http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/ausPIX/R7852372435,

'auspixlong8': '149.11217802164305',
'auspixlat84': '-35.32474119366026',
'auspix_ha_a': '2.44082628',

'sa1_main16': '80106106908',
'sa1sqkm16': '2.4649',
'sa1_uri': http://linked.data.gov.au/dataset/asgs2016/statisticalarealevel1/80106106908,

'sa2_main16': '801061069','sa2_name16': 'Red Hill ACT',

'sa3_code16': '80106','sa3_name16': 'South Canberra',

'ste_name16': 'Australian Capital',

'ssc_code16': '80110','ssc_name16': 'Red Hill ACT','sscsqkm16': '4.8606',

'ced_name': 'Canberra','ced_state': 'ACT','ced19sqkm': '312.26314223983',

'sed_code19': '80003','sedname19': 'Kurrajong','sedsqkm19': '290.2734',

'lga_code19': '89399','lga_name19': 'Unincorporated ACT','lgasqkm19': '2358.172',

'pa_id': 'ACT_21','capad': 'Red Hill','type': 'Nature Reserve','gis_area': '292.77767944',

'ga_bomid': '449058','bom_sqkm': '25.227',

'sparkbgid': 'eslc23322','spark_area': '0.0001',

'geom': '0101000020E61000002EC95CF696A36240A837931E91A941C0'

As development occurs more URI's and more datasets (some from other tables) will be added.
Descriptions of each field are available from the dtata base and may be ported in future development sprints.

# Supporting Code
Supporting code is included, to allow others to build crosswalk tables and manage processes.
See the Supporting code folder

# References:
https://pypi.org/project/rHEALPixDGGS/

https://iopscience.iop.org/article/10.1088/1755-1315/34/1/012012/pdf

https://github.com/GeoscienceAustralia/AusPIX_DGGS

https://raichev.net/files/rhealpix_dggs_preprint.pdf



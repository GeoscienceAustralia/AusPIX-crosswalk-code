# AusPIX-DGGS-dataset

Australian rhealPIX DGGS implementation dataset, as a linked data API.
Includes landing-page with map and data for each AusPIX cell (worldwide including Antarctica).
Search for any cell.

Date: September 2019

Known Issue: the leaflet module map cannot display the polar regions properly (N4 and S4). This is because folium and leaflet are on a planar projection and do not extend all the way to the polar regions.

Data includes: Map, area, parent cell, child cells, vertices, centroid, cell neighbours. 

This is the code for the linked-data API for AusPIX DGGS cells.
API provides basic information about AusPIX cells.

Author: Bell, J.G.

ecat record: 140149

Funded by the Australian Government Loc-I Project

Online at: http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/ausPIX/


References:
https://iopscience.iop.org/article/10.1088/1755-1315/34/1/012012/pdf

https://github.com/GeoscienceAustralia/AusPIX_DGGS

https://raichev.net/files/rhealpix_dggs_preprint.pdf

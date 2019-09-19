# AusPIX-DGGS-dataset

Australian rhealPIX DGGS implementation dataset, as a linked data API.
Includes landing-page with map and data for each AusPIX cell (worldwide including Antarctica).
Search for any cell.

Known Issue: a small percentage of cells do not draw the polygon properly, especially large cells near the edge of the main regions.
For example the cells R8, S0. This is related to how some DGGS vertices display in folium and leaflet mapping modules. 


However centroid marker display and cell data are correct.

Data includes: Map, area, parent cell, child cells, vertices, centroid, cell neighbours. 

References:
https://iopscience.iop.org/article/10.1088/1755-1315/34/1/012012/pdf

https://github.com/GeoscienceAustralia/AusPIX_DGGS

https://raichev.net/files/rhealpix_dggs_preprint.pdf

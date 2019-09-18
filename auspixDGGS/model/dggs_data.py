# -*- coding: utf-8 -*-
import decimal
import json
import os
from flask import render_template, Response

import folium
import auspixDGGS._conf as conf
from pyldapi import Renderer, View
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal



# for DGGS zone attribution
import dggs
rdggs = dggs.RHEALPixDGGS()

class DGGS_data(Renderer):
    """
    This class takes any DGGS cell fed into it and it uses the DGGS ENGINE
    to find the attributes of the cell for pushing out to the landing page
    """

    def __init__(self, request, uri):
        views = {
            'auspix_cell': View(
                '/dggs/auspix/',
                'This view is the standard view delivered by the DGGS dataset in accordance with the '
                'XXXXX Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            )
        }

        super(DGGS_data, self).__init__(request, uri, views, 'auspix_cell', None)
        print('this uir', uri)
        self.id = uri.split('/')[-1]   #probably not needed for this DGGS
        print('selfID in DGGS seracher', self.id)  #self ID is the cell id

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/ausPIX/',
            'label': 'from AusPIX DGGS engine (beta version 0.9):',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }

        self.auspix = None
        self.area_km2 = None
        self.longitude = None
        self.latitude = None
        self.width = None
        self.corners = None
        self.longLatsList = list()
        self.x = None
        self.y = None
        self.centroid = None
        self.neighs = None
        self.contains = None
        self.subCells = None
        self.partOfCell = None

        # use DGGS engine to find values

        self.auspix = self.id
        self.hasName = self.id
        dggsLoc = list()  # empty list ready to fill
        for item in self.auspix:  # build a dggs location cell as a list like dggsLoc = ['R', 7, 2, 4, 5, 6, 3, 2, 3, 4, 3, 8, 3]
            if item.isalpha():  # the letter 'R' at the beginning
                dggsLoc.append(item)
            else:
                item = int(item)  # for all the numbers in the cell
                dggsLoc.append(item)

        cell = rdggs.cell(dggsLoc)
        # self.width = rdggs.cell.cell_width(planar= True)
        #find centroid
        self.centroid = cell.nucleus(plane=False)  # on the ellipsoid

        self.y = self.centroid[1]
        self.x = (self.centroid[0])  # temp repair to get rid of engine problem
        print('y', self.y)
        print('x', self.x)

        self.corners = cell.vertices(plane=False)
        # print('self.corners', self.corners)

        #find the neighbors of the cell
        self.neighbors = cell.neighbors()
        neighs = list()
        nie = list()
        for keys, values in self.neighbors.items():
            print(keys, values)
            nei = (keys, str(values))
            neighs.append(nei)
        print('neighs', neighs)
        self.neighs = str(neighs)

        #print('verts', self.corners)
        num = cell.area(plane=False)
        num = int(num)
        num2 = (f"{num:,d}")
        self.area_km2 = num2
        print('area', self.area_km2)
        # containsList = list()
        # for x in range(0, 9):  #there is no 9 in Auspix
        #     containsList.append(self.auspix + str(x))
        # self.contains = containsList   # there is also a function in the engine called subcells
        self.subcells = cell.subcells()
        # get engine to calculate subcells
        mySubCells = []
        for item in self.subcells:
            mySubCells.append(str(item))
        self.contains = mySubCells
        print('mysubs', mySubCells)
        self.partOfCell = self.auspix[:-1]  #take one number off the end of cell ID, = parent cell





    def export_html(self):
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                'auspix_cell.html',   # uses the html template send all this data to it.
                id=self.auspix,
                hasName=self.hasName,
                dggs = self.auspix,
                #crns=self.corners,
                corners=self.corners,
                neighbours = self.neighbors,
                y = self.y,
                x = self.x,
                area_km2= self.area_km2,
                contains = self.contains,
                partOfCell = self.partOfCell,

                neighs = self.neighs
                # schemaorg=self.export_schemaorg()
            ),
            status=200,
            mimetype='text/html'
        )
        # if we had multiple views, here we would handle a request for an illegal view
        # return NotImplementedError("HTML representation of View '{}' is not implemented.".format(view))

    # maybe should call this function something else - it seems to clash ie Overrides the method in Renderer
    def render(self):
        if self.view == 'alternates':
            return self._render_alternates_view()   # this function is in Renderer
        elif self.format in ['text/turtle', 'application/ld+json']:
            return self.export_rdf()                # this one exists below
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html()

    def export_rdf(self):
        g = Graph()  # make instance of a RDF graph

        PN = Namespace('http://linked.data.gov.au/def/placename/')   #rdf neamespace declaration
        g.bind('pn', PN)


        #loop through the next 3 lines to get subject, predicate, object for the triple store adding each time??
        me = URIRef(self.uri)   # URIRef is a RDF class
        g.add((me, RDF.type, URIRef('http://linked.data.gov.au/def/placename/PlaceName')))  # PN.PlaceName))
        g.add((me, PN.hasName, Literal(self.hasName['value'], datatype=XSD.string)))

        if self.format == 'text/turtle':
            return Response(
                g.serialize(format='turtle'),
                mimetype='text/turtle'
            )
        else:  # JSON-LD
            return Response(
                g.serialize(format='json-ld'),
                mimetype='application/ld+json'
            )
    # for schema dot org format
    def export_schemaorg(self):  #this is all for GNAF - needs to adapted to Placenames
        data = {
            '@context': 'http://schema.org',
            '@type': 'Place',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': self.address_string.split(',')[0],
                'addressLocality': self.locality_name,
                'addressRegion': self.state_prefLabel,    #change these for placenames attributes
                'postalCode': self.postcode,
                'addressCountry': 'AU'
            },
            'geo': {
                '@type': 'GeoCoordinates',
                'latitude': self.latitude,                # keep this for placenames?
                'longitude': self.longitude
            },
            'name': 'Geocoded Address ' + self.id
        }

        #return json.dumps(data, cls=DecimalEncoder) #
        return json.dumps(data, cls=decimal)  # changed to suit import


if __name__ == '__main__':
    # a = Address('GANSW703902211', focus=True)  # not functional because from GNAF - this is placenames
    # print(a.export_rdf().decode('utf-8'))

    print('main process has not been built yet - when build it will test ask for a placename like the code Gnaf above')



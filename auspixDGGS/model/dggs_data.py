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
from auspixengine import dggs
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
        print('this uri', uri)
        self.id = uri.split('/')[-1]   #probably not needed for this DGGS
        print('self.id = ', self.id)  #self ID is the cell id

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
        print('dggs cell ID =', self.auspix)
        self.hasName = self.id
        dggsLoc = list()  # empty list ready to fill
        for item in self.auspix:  # build a dggs location cell as a list like dggsLoc = ['R', 7, 2, 4, 5, 6, 3, 2, 3, 4, 3, 8, 3]
            if item.isalpha():  # the letter 'R' at the beginning
                dggsLoc.append(item)
            else:
                item = int(item)  # for all the numbers in the cell
                dggsLoc.append(item)

        cell = rdggs.cell(dggsLoc)  # define a cell object
        self.corners = cell.vertices(plane=False)
        self.centroid = cell.nucleus(plane=False)  # on the ellipsoid

        self.y = self.centroid[1]  #for html and routes
        self.x = self.centroid[0]  #for html and routes

        self.mypoly = cell.vertices(plane=False)
        self.mypoly.append(self.mypoly[0])  #to close the polygon

        self.wktPoint = 'POINT' + str(cell.nucleus(plane=False))   # centroid as wkt
        self.wktPoly = 'POLYGON' + str(self.mypoly)  # vertices poly as wkt
        self.wktPoly = self.wktPoly.replace('[','(')
        self.wktPoly = self.wktPoly.replace(']',')')


        #find the neighbors of the cell
        self.neighbors = cell.neighbors()  #calls engine for the neighbours - returns dict

        self.neighs = list()
        for keys, values in self.neighbors.items():  #convert to list
            nei = (keys, str(values))
            self.neighs.append(nei)
        #self.neighs = neighs
        print('neighs', self.neighs)
        self.auspixLeft = self.neighs[0][1]
        self.auspixRight = self.neighs[1][1]
        self.auspixDown = self.neighs[2][1]
        self.auspixUp = self.neighs[3][1]
        self.auspixCell = 'Cell'

        #print('verts', self.corners)
        num = cell.area(plane=False)
        num = int(num)
        num2 = str(num) # (f"{num:,d}")
        self.area_m2 = num2
        self.subcells = cell.subcells()  # get engine to calculate subcells

        mySubCells = []
        for item in self.subcells:
            mySubCells.append(str(item))
        self.contains = mySubCells   #for html landing page (?)

        self.childCells = list()
        for item in mySubCells:
            self.childCells.append(('auspix:' + item))


        #print('mysubs', mySubCells)
        self.partOfCell = self.auspix[:-1]  #take one number off the end of cell ID, = parent cell





    def export_html(self):
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                'auspix_cell.html',   # uses the html template send all this data to it.
                id=self.auspix,
                uri=conf.DGGS_PID_PREFIX + self.auspix,
                auspix=self.auspix,
                hasName=self.hasName,
                dggs = self.auspix,
                #crns=self.corners,
                corners=self.corners,
                centroid = self.centroid,
                neighbours = self.neighbors,
                y = self.y,
                x = self.x,
                area_m2= self.area_m2,
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

    def export_rdf(self):  #also for text/turtle

        g = Graph()  # make instance of an RDF graph

        #auspix = Namespace('http://linked.data.gov.au/def/dggs/auspix/')   #rdf namespace declaration
        auspix = Namespace('http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/ausPIX/R78523')  # rdf namespace declaration
        g.bind(self.auspix, auspix)  #made the cell ID the subject of the triples

        me = 'auspix:' + URIRef(self.id)
        # g.add((me, RDF.type, URIRef('http://linked.data.gov.au/def/dggs/auspix')))  #type  . . . . a . . . . .

        geo = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', geo)

        # apo = Namespace('http://linked.data.gov.au/def/ausPIX#')
        # g.bind('apo', apo)

        geox = Namespace('http://linked.data.gov.au/def/geox#')
        g.bind('geox', geox)

        dct = Namespace('http://purl.org/dc/terms/#')
        g.bind('dct', dct)

        dcat = Namespace('http://www.w3.org/ns/dcat/#')
        g.bind('dcat', dcat)

        data = Namespace('http://linked.data.gov.au/def/datatype/#')
        g.bind('data', data)

        rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        g.bind('rdfs', rdfs)

        xsd = Namespace('http://www.w3.org/XML/XMLSchema#')
        g.bind('xsd', xsd)



        #print('version', rdflib __version__)


        #g.add((me, RDF.type, Literal(self.auspix, datatype=xsd.string)))
        g.add((auspix, RDF.type, URIRef('auspix:' + self.auspixCell)))
        #g.add((apo, RDF.type, URIRef('auspix:' + self.apoUp)))

        g.add((me, auspix.upNeighbour, Literal(self.auspixUp, datatype=geo.sfTouches)))
        g.add((me, auspix.downNeighbour, Literal(self.auspixDown, datatype=geo.sfTouches)))
        g.add((me, auspix.rightNeighbour, Literal(self.auspixRight, datatype=geo.sfTouches)))
        g.add((me, auspix.leftNeighbour, Literal(self.auspixLeft, datatype=geo.sfTouches)))




        #g.add((me, RDF.type, self.auspix))
        g.add((me, geox.hasAreaM2, Literal(self.area_m2, datatype=xsd.decimal)))

        #
        g.add((me, dcat.centroid, Literal(self.wktPoint, datatype=geo.wtkLiteral)))
        g.add((me, geo.hasGeometry, Literal(self.wktPoly, datatype=geo.wktLiteral)))
        g.add((me, dct.identifier, Literal(self.auspix)))



        g.add((me, geo.sfContains, Literal(self.childCells, datatype=XSD.string)))
        g.add((me, geo.sfWithin, Literal(('auspix:' + self.partOfCell), datatype=XSD.string)))

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



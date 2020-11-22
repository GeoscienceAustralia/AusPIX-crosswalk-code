# -*- coding: utf-8 -*-

import decimal
import json
#import os
from flask import render_template, Response

#import folium
import _conf as conf
from pyldapi import Renderer, Profile

from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
from rdflib.namespace import XSD, DCTERMS, RDFS   #imported for 'export_rdf' function
#from _conf import DB_CON_DICT
import psycopg2
from _conf import DB_CON_DICT


# for DGGSC:C zone attribution
from rhealpixdggs import dggs
rdggs = dggs.RHEALPixDGGS()

class DGGS_data(Renderer):
    """
    This class takes any DGGS cell fed into it and it uses the DGGS ENGINE
    to find the attributes of the cell for pushing out to the landing page
    Also connects to crosswalk to get integrated data for that cell.
    """

    def __init__(self, request, uri):
        format_list = ['text/html', 'text/turtle', 'application/ld+json', 'application/rdf+xml']
        views = {
            'auspix': Profile(
                'http://linked.data.gov.au/def/AusPix/',
                'AusPIX DGGS cell view',
                'This is the combined view of an AusPIX DGGS Cell delivered by the AusPIX dataset in '
                'accordance with the Profile',
                format_list,
                'text/html'
            )
        }
        #
        super(DGGS_data, self).__init__(request, uri, views, 'auspix')
        print('this uri', uri)
        self.id = uri.split('/')[-1]  #needed for routes
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
        self.sa1code = None
        self.sa2name = None
        self.sedname = None
        self.ssc_code16 = None
        self.ssc_name16 = None
        self. sscsqkm16 = None


        # use DGGS engine to find values

        self.auspix = self.id
        #print('dggs cell ID =', self.auspix)
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

        centrd = str(cell.nucleus(plane=False))   # find the centroid using the engine
        centrd = centrd.replace(',', '') # prepare for wkt
        self.wktPoint = 'POINT ' + centrd   # centroid as wkt

        self.wktPoly = 'POLYGON ' + str(self.mypoly)  # vertices poly
        # convert poly data to vertices list to wkt
        self.wktPoly = self.wktPoly.replace('(', '')  # prepare for wkt
        self.wktPoly = self.wktPoly.replace(', ', ' ')  # prepare for wkt
        self.wktPoly = self.wktPoly.replace('),', ',')  # prepare for wkt
        self.wktPoly = self.wktPoly.replace(') ', ', ')  # prepare for wkt

        self.wktPoly = self.wktPoly.replace('[','((')  # prepare for wkt
        self.wktPoly = self.wktPoly.replace(']','))')   # prepare for wkt
        self.wktPoly = self.wktPoly.replace(')))', '))')  # prepare for wkt

        #find the neighbors of the cell
        self.neighbors = cell.neighbors()  #calls engine for the neighbours - returns dict

        self.neighs = list()
        for keys, values in self.neighbors.items():  #convert to list
            nei = (keys, str(values))
            self.neighs.append(nei)
        #self.neighs = neighs
        #print('neighs', self.neighs)
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
        self.contains = mySubCells  # for html landing page (?)

        self.childCells = list()
        for item in mySubCells:
            self.childCells.append((item))

        self.child0 = self.childCells[0]
        self.child1 = self.childCells[1]
        self.child2 = self.childCells[2]
        self.child3 = self.childCells[3]
        self.child4 = self.childCells[4]
        self.child5 = self.childCells[5]
        self.child6 = self.childCells[6]
        self.child7 = self.childCells[7]
        self.child8 = self.childCells[8]

        #print('mysubs', mySubCells)
        self.partOfCell = self.auspix[:-1]  #take one number off the end of cell ID, = parent cell

        # connect to crosswalk table and get crosswalk information for this cell
        mycells = (self.auspix, "", "")

        print('query AWS database . . . . ')
        connection = psycopg2.connect(**DB_CON_DICT)

        cursor = connection.cursor()

        # postgreSQL_select_Query = " SELECT * FROM crosswalk WHERE auspix_dggs IN %s;"   # works but return not json
        # return data as json
        postgreSQL_select_Query = " SELECT json_agg(crosswalk) FROM crosswalk WHERE auspix_dggs IN %s;"  # seems to only get the first item as json

        # postgreSQL_select_Query = " SELECT json_agg(crosswalk) FROM crosswalk WHERE auspix_dggs IN  ('R7852348515', 'R7852348516', 'R7852348517');"
        cursor.execute(postgreSQL_select_Query, (mycells,))

        print("Selecting rows from national crosswalk table using cursor.fetchall")

        theseRecords = cursor.fetchall()
        print('num Recs', theseRecords)

        result = theseRecords[0][0][0]

        for key, value in result.items():
            print(key, ' : ', value)

        print("SA1 code 2016 = ", result['sa1_main16'])
        self.sa1code = result['sa1_main16']

        print('sa2 name', result['sa2_name16'])
        self.sa2name = result['sa2_name16']
        self.sedname = result['sedname19']
        self.ssc_code16 = result['ssc_code16']
        self.ssc_name16 = result['sedname19']
        self.sscsqkm16 = result['sscsqkm16']




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
                    neighs = self.neighs,
                    # schemaorg=self.export_schemaorg()
                    sa1code = self.sa1code,
                    sa2name = self.sa2name,
                    sedname = self.sedname,
                    ssc_code16 = self.ssc_code16,
                    ssc_name16 = self.ssc_name16,
                    sscsqkm16 = self.sscsqkm16,

                ),
                status=200,
                mimetype='text/html'
        )
        # if we had multiple views, here we would handle a request for an illegal view
        # return NotImplementedError("HTML representation of View '{}' is not implemented.".format(view))

    def render(self):
        if self.profile == 'alt':
            print('alt profile active')
            return self._render_alt_profile()  # this function is in Renderer
        elif self.mediatype in ['text/turtle', 'application/ld+json', 'application/rdf+xml']:
            return self.export_rdf()
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html()


    def crosswalk_fetch(cell):
        mycells = ("R7852372438", "")

        print('query AWS database . . . . ')
        connection = DB_CON_DICT
        cursor = connection.cursor()

        # postgreSQL_select_Query = " SELECT * FROM crosswalk WHERE auspix_dggs IN %s;"   # works but return not json
        # return data as json
        postgreSQL_select_Query = " SELECT json_agg(crosswalk) FROM crosswalk WHERE auspix_dggs IN %s;"  # seems to only get the first item as json

        # postgreSQL_select_Query = " SELECT json_agg(crosswalk) FROM crosswalk WHERE auspix_dggs IN  ('R7852348515', 'R7852348516', 'R7852348517');"
        cursor.execute(postgreSQL_select_Query, (mycells,))

        print("Selecting rows from national crosswalk table using cursor.fetchall")

        theseRecords = cursor.fetchall()
        print('num Recs', len(theseRecords))

        result = theseRecords[0][0][0]

        for key, value in result.items():
            print(key, ' : ', value)

        print("AusPIX cell URI", result['auspix_uri'])

        print("SA1 code 2016", result['sa1_main16'])
        print("SA1 SQkm 2016 ", result['sa1sqkm16'])
        return print('done')








    def export_rdf(self):  #also for text/turtle
        g = Graph()  # make instance of an RDF graph

        # namespace declarations
        auspix = URIRef('http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/')
        g.bind('auspix', auspix)  #made the cell ID the subject of the triples

        apo = Namespace('http://linked.data.gov.au/def/auspix#')  # ontolgy  = /def/  #the ontolgy   auspix ontolgy == apo
        g.bind('apo', apo)
        # g.add((auspix, RDF.type, URIRef('http://linked.data.gov.au/def/dggs/auspix')))  # pattren for type  . . . . a . . . . .
        geo = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', geo)
        geox = Namespace('http://linked.data.gov.au/def/geox#')
        g.bind('geox', geox)
        # dcterms = Namespace('http://purl.org/dc/terms/')  # already imported
        g.bind('dcterms', DCTERMS)
        dcat = Namespace('http://www.w3.org/ns/dcat/#')
        g.bind('dcat', dcat)
        #rdfs = Namespace('http://www.w3.org/2001/XMLSchema#')    # already imported at top
        #g.bind('rdfs', RDFS)    # (not used ??)
        #xsd = Namespace('http://www.w3.org/XML/XMLSchema#')     # already imported
        g.bind('xsd', XSD)

        data = Namespace('http://linked.data.gov.au/def/datatype/')
        g.bind('data', data)

        # build the graphs
        # first line - points the dggs cell to the ontology == apo
        g.add((URIRef(auspix + self.id), RDF.type, URIRef(apo + 'Cell'))) ;

        # neighbours
        g.add((auspix + self.id, apo.hasNeighbourUp, URIRef(auspix + self.auspixUp))) ;
        g.add((auspix + self.id, apo.hasNeighbourDown, URIRef(auspix + self.auspixDown))) ;
        g.add((auspix + self.id, apo.hasNeighbourLeft, URIRef(auspix + self.auspixLeft))) ;
        g.add((auspix + self.id, apo.hasNeighbourRight, URIRef(auspix + self.auspixRight))) ;

        #area needs special treatment  - a Blank Node   - 2 options
        #create the blank node
        curr_bnode = BNode()
        #add details for the blank node
        g.add((curr_bnode, data.value, Literal(self.area_m2, datatype=XSD.decimal)))
        #create the link between the parent node and the blank node
        g.add((auspix + self.id, geox.hasAreaM2, curr_bnode))

        #create the blank node for Area -1st option from Jonathan
        # curr_bnode = BNode()
        # #add details for the blank node
        # g.add((curr_bnode, RDF.type, geox.SpatialMeasure))
        # g.add((curr_bnode, data.unit, URIRef("http://qudt.org/vocab/unit/M2")))
        # g.add((curr_bnode, data.value, Literal(self.area_m2, datatype=XSD.decimal)))
        # #create the link between the parent node and the blank node
        # g.add((auspix + self.id, geox.hasArea, curr_bnode))

        # other data
        g.add((auspix + self.id, DCTERMS.identifier, Literal(self.auspix))) ;
        g.add((auspix + self.id, geo.hasGeometry, Literal(self.wktPoly, datatype=geo.wktLiteral))) ;
        g.add((auspix + self.id, geox.hasCentroid, Literal(self.wktPoint, datatype=geo.wtkLiteral))) ;
        g.add((auspix + self.id, geo.sfWithin, URIRef(auspix + self.partOfCell))) ;

        #child cells
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child0)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child1)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child2)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child3)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child4)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child5)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child6)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child7)))
        g.add((auspix + self.id, geo.sfContains, URIRef(auspix + self.child8))) ;


        if self.mediatype == 'text/turtle':
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

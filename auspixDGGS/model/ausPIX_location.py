# -*- coding: utf-8 -*-
import decimal
import json
import os
from flask import render_template, Response

import folium
import auspixDGGS._conf as conf
from pyldapi import Renderer, View
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal


class Placename(Renderer):
    """
    This class represents a placename and methods in this class allow a placename to be loaded from the GA placenames database
    and to be exported in a number of formats including RDF, according to the 'PlaceNames Ontology'

    """

    def __init__(self, request, uri):
        views = {
            'pn': View(
                'Place Names View',
                'This view is the standard view delivered by the Place Names dataset in accordance with the '
                'Place Names Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            )
        }

        super(Placename, self).__init__(request, uri, views, 'pn', None)

        print('uri is ', uri)
        self.id = uri.split('/')[-1]

        print('selfid inausPix location', self.id)
        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/ausPIX/',
            'label': 'from AusPIX DGGS engine (beta version 0.9):',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }

        self.register = {
            'label': None,
            'uri': None
        }

        self.wasNamedBy = {
            'label': None,
            'uri': None
        }

        self.hasNameFormality = {
            'label': 'Official',
            'uri': 'http://linked.data.gov.au/def/placenames/nameFormality/Official'
        }

        self.authority = {
            'label': None,
            'web': None
        }
        self.auspix = None

        self.area_km2 = None

        self.hasPronunciation = None   # None == don't display
        # pronunciation will only be displyed on webpage if it exists

        self.longitude = None
        self.latitude = None
        self.longLatsList = list()

        q = '''
            SELECT 
              	"id", "auspix", "width_m", "corners", "area_km2"
                 
                
            FROM "cells"
            WHERE "id" = '{}'
        '''.format(self.id)
        for auspix in conf.db_select(q):
            # for item in placename:
            #     print(item)
            #print(placename)
            #print('list', auspix[0], auspix[1], auspix[2], auspix[3], auspix[4])
            # set up x y location from database
            self.auspix = auspix[1]
            self.width = auspix[2]
            self.hasName = auspix[1]
            self.corners = auspix[3]  #import the corners
            self.area_km2 = auspix[4]

            # convert corners into a list
            longLatsList = list()
            for thing in self.corners.split('},'):
                #print('PY', self.corners)
                thing = thing.replace("{", "")
                thing = thing.replace("}", "")
                #print('thingPY', thing)

                split_thing = thing.split(',')
                latLongs = [split_thing[1], split_thing[0]]

                coords = list()

                for item in latLongs:
                    coords.append(float(item))
                longLatsList.append(coords)

            self.longitude = longLatsList[0][1]
            self.latitude = longLatsList[0][0]



    def export_html(self):
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                'ausPIX_location.html',   # uses the placenames.html template send all this data to it.
                id=self.id,
                hasName=self.hasName,

                ausPIX_DGGS = self.auspix,
                crns=self.corners,
                longitude = self.longitude,
                latitude = self.latitude,
                area_km2 = self.area_km2,
                width_m = self.width
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



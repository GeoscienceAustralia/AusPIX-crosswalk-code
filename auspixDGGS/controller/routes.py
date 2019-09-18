from flask import Blueprint, request, redirect, url_for, Response, render_template, send_file
import flask
from auspixDGGS.model.ausPIX_location import Placename
from auspixDGGS.model.dggs_data import DGGS_data
#from auspixDGGS.model.gazetteer import Gazetteer, GAZETTEERS
from pyldapi import RegisterRenderer
import auspixDGGS._conf as conf
import folium
import os

routes = Blueprint('controller', __name__)

DEFAULT_ITEMS_PER_PAGE=1000


@routes.route('/', strict_slashes=True)
def home():
    return render_template('home.html')

@routes.route('/ausPIX/')
def ausPIX():
    search_string = request.values.get('search')
    return render_template('ausPIX.html',
                           search_query=search_string,
                           search_enabled=True
                           )

@routes.route('/ausPIX/<string:auspix_cell_id>')
def auspix_cell(auspix_cell_id):
    auspix_cell = DGGS_data(request, request.base_url)
    return auspix_cell.render()


@routes.route('/map')
def show_map():
    '''
    Function to render a map around the specified coordinates
    '''
    print('showmap activated')
    auspix = request.values.get('auspix')
    #print('name in requests = ', name)  # not working
    corners = (request.values.get('location')).split('),')
    print('map corners', corners)

    #corners is straight from database vis auspix_location.py and auspix_location.html
    #print('cornersXXroutes', corners[0], corners[1], corners[2], corners[3])
    # convert the corner information  into a list for the leaflet map
    longLatsList = list()
    for thing in corners:
        thing = thing.replace("{", "")
        thing = thing.replace("}", "")
        thing = thing.replace("[", "")
        thing = thing.replace("]", "")
        thing = thing.replace("(", "")
        thing = thing.replace(")", "")
        # thing = thing.replace('-180', '180') # temp fix
        # thing = thing.replace('-150', '150') # temp fix
        # thing = thing.replace('-90', '90')  # temp fix
        # thing = thing.replace('-120', '120')# temp fix
        print('thing', thing)

        split_thing = thing.split(',')
        # needs latitude first
        latLongs = [split_thing[1], split_thing[0]]
        #print('splitlATlongs', latLongs)
        coords = list()
        # convert to floats
        for item in latLongs:
            coords.append(float(item))
        longLatsList.append(coords)
    #
    x = float(request.values.get('x'))
    y = float(request.values.get('y'))
    print('centx', x)
    print('centy' , y)



    # try for centroid values if available

    # create a new map object
    tooltip = 'Click for more information'
    folium_map = folium.Map(location=[y, x], zoom_start=3)
    # create markers
    folium.Marker([y, x],
        popup = auspix,
        tooltip=tooltip).add_to(folium_map)

    # create polygon
    folium.vector_layers.Polygon(locations=longLatsList,
                                 popup=auspix,
                                 tooltip='tooltip',
                                 ).add_to(folium_map)
    folium.vector_layers.path_options(line=True,
                                      radius=5,
                                      color='#FF6347')

    return folium_map.get_root().render()




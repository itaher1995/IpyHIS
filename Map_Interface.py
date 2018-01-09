# -*- coding: utf-8 -*-


from __future__ import print_function
import ipyleaflet as ipyl
from suds.client import Client
import ipywidgets as widgets
from IPython.display import display
import itertools
import json
import os
import numpy as np
import shapely
from shapely.geometry import shape
import re
import time
#from IPython.display import HTML
#from multiprocessing import Pool

class Map:
    '''
    A class created using methods from the ipyleaflet library. This class is
    not a subclass of ipyleaflet at this time, therefore the methods included 
    with ipyleaflet will not work on the map.
    '''
    def __init__(self):
        self.map=ipyl.Map(center = [54.5260,-105.2551],zoom=3)

    def showMap(self):
        '''
        Displays a ipython leaflet map that has several built-in functionality.
        Saves bounding box globally so that it can be used by the HIS API functions
        included in this widget. Although not typical or ideal, we have nested
        functions so that users don't call functions by mistake and break the code.
        '''
        #creates the buttons that help switch between the different functionalities
        toggleButtons= widgets.ToggleButtons(
                options=['Polygon', 'State Boundary','HUC Boundary'],
                description='Type:',
                disabled=False,
                button_style='',
                )
        #mappy is a reference to the map. This is done so that the map can be
        #referenced in the functions below.
        mappy=self.map
        dc=ipyl.DrawControl()
        
        global geoJSONDic #global dictionary for state geojsons
        geoJSONDic={}
        global hucGlobalDic #global dictionary for huc region geojsons
        hucGlobalDic={}
        global huc12GlobalDic #global dictionary for huc-12 region geojsons
        huc12GlobalDic={}
        
        #helper functions
        def BOUNDCREATION(self):
            '''Creates bounds for the custom polygon option'''
            global coords1 #global coordinates of polygon to remove false positives later.
            coords=dc.last_draw['geometry']['coordinates'][0]
            coords1=dc.last_draw['geometry']
            
            #global to create bounding box for HIS Catalog search
            global max_lat
            global max_lon
            global min_lat
            global min_lon
            max_lat=-1000
            max_lon=-1000
            min_lat=1000
            min_lon=1000
            
            #develop max latitude/longitude and min latitude/longitude
            for coord in coords:
                if coord[1]>max_lat:
                    max_lat=round(coord[1],1)
                if coord[1]<min_lat:
                    min_lat=round(coord[1],1)
                if coord[0]>max_lon:
                    max_lon=round(coord[0],1)
                if coord[0]<min_lon:
                    min_lon=round(coord[0],1)
            print('max lat: {0}, max lon: {1}, min lat: {2}, min lon: {3}'.format(max_lat,max_lon,min_lat,min_lon))    
            print('The values for the edges of the bounding box are stored in max_lat, min_lat, max_lon, min_lon')
        
        def SAVEBOX(self,action,geo_json):
            '''Displays an ipython widget button that will call bound creation
            to save the custom polygon created.'''
            button=widgets.Button(description='Save Polygon')
            display(button)
            button.on_click(BOUNDCREATION)
        
        def GRABSTATEBOUNDS(event,properties,id):
            '''Grabs state bounding box.'''
            getState=id[-2:]+'.geo.json'
            with open('IPyHIS/US-STATES/{0}'.format(getState)) as f:
                global coords1
                coords1=json.loads(f.read())['features'][0]['geometry']
                coords=coords1['coordinates']
                if type(coords[0][0][0])==list:
                    coords=list(itertools.chain(*itertools.chain(*coords)))
                else:
                    coords=list(itertools.chain(*coords))
                lon=np.unique([x[0] for x in coords])
                lat=np.unique([x[1] for x in coords])
                global max_lat
                global max_lon
                global min_lat
                global min_lon
                max_lon=max(lon)
                max_lat=max(lat)
                min_lon=min(lon)
                min_lat=min(lat)
                print('max lat: {0}, max lon: {1}, min lat: {2}, min lon: {3}'.format(max_lat,max_lon,min_lat,min_lon))
        
        def GRABHUCBOUNDS(event,properties,id):
            '''
            Saves huc-12 polygon bounding box to global variables.
            '''
            getHUC=id+'.geo.json'
            with open('IPyHIS/HUC-US-1/{0}'.format(getHUC)) as f:
                global coords1
                coords1=json.loads(f.read())['features'][0]['geometry']
                coords=coords1['coordinates']
                if type(coords[0][0][0])==list:
                    coords=list(itertools.chain(*itertools.chain(*coords)))
                else:
                    coords=list(itertools.chain(*coords))
                lon=np.unique([x[0] for x in coords])
                lat=np.unique([x[1] for x in coords])
                global max_lat
                global max_lon
                global min_lat
                global min_lon
                max_lon=max(lon)
                max_lat=max(lat)
                min_lon=min(lon)
                min_lat=min(lat)
                print('max lat: {0}, max lon: {1}, min lat: {2}, min lon: {3}'.format(max_lat,max_lon,min_lat,min_lon))
        
        def ADDHUC12(huc12):
            '''
            Adds huc-12 polygons to the map in a multiprocessed fashion.
            '''
            huc12FolderName='IPyHIS/HUC-US-1/'
            f=open(huc12FolderName+huc12)
            readHuc12=f.read()
            #if huc-12 is in proper json format load it, if not skip
            try:
                huc12json=json.loads(readHuc12)
                huc12GeoJson=ipyl.GeoJSON(data=huc12json, hover_style={'fillColor':'red'})
                huc12GlobalDic[huc12[:-9]]=huc12GeoJson
                huc12GeoJson.on_click(GRABHUCBOUNDS)
                mappy.add_layer(huc12GeoJson)
            except:
                pass

        def HUCZOOM(event,properties,id):
            '''
            Zooms in on a specified huc region, removes all the hucs and replaces 
            them with huc-12s in that region
            '''
            with open('IPyHIS/hucs/{0}'.format(id+'.geo.json')) as f:
                coords=json.loads(f.read())['features'][0]['geometry']
                
                #use centroid to center in on huc region
                centroid=list(map(float,re.sub(r'.* \((.*)\).*',r'\1',shape(coords).buffer(0.0).centroid.wkt).split(' ')))[::-1]
                mappy.center=centroid
                time.sleep(0.5)
                mappy.zoom=6
                
                #get all hucs associated with that region
                hucRegion = re.search(r'[A-Z]+_(\d+)[A-Z]?',id).group(1)
                huc12FolderName='IPyHIS/HUC-US-1/'
                huc12Folder=[x for x in os.listdir(huc12FolderName) if x[:2]==hucRegion]
                for huc in huc12Folder:
                    ADDHUC12(huc)
                #initialize pool with workers to increase efficiency
#                p = Pool(processes=20)
#                p.map_async(addHUC12,huc12Folder)
                


        def DISPLAYREGIONS(event,properties):
            '''
            A helper function that runs at the end of a move. Checks what the 
            zoom level is and either removes the original huc regions or adds them.
            Also removes or adds any huc12s on the map.
            '''
            if mappy.zoom>=6:
                for huc in hucGlobalDic:
                    if hucGlobalDic[huc] in mappy.layers:
                        mappy.remove_layer(hucGlobalDic[huc])
            else:
                for huc in hucGlobalDic:
                    if hucGlobalDic[huc] not in mappy.layers:
                        hucGlobalDic[huc].on_click(HUCZOOM)
                        mappy.add_layer(hucGlobalDic[huc])
                for huc12 in huc12GlobalDic:
                    if huc12GlobalDic[huc12] in mappy.layers:
                        mappy.remove_layer(huc12GlobalDic[huc12])
        
        #add box saving functionality to the draw control
        dc.on_draw(SAVEBOX)
        self.map.add_control(dc)
        
        def toggle_boundaries(self,event,action):
            '''Function that controls the buttons that allow for switching between
            map functionalities.'''            
            toggler=toggleButtons
            if toggler.label=='State Boundary':
                if dc in mappy.controls:
                    mappy.remove_control(dc) #remove draw control. Not needed for this function
                if len(mappy.layers)>1:
                    for huc in hucGlobalDic:
                        if hucGlobalDic[huc] in mappy.layers:
                            mappy.remove_layer(hucGlobalDic[huc])
                if len(mappy.layers)>52:
                    for huc12 in huc12GlobalDic:
                        if huc12GlobalDic[huc12] in mappy.layers:
                            mappy.remove_layer(huc12GlobalDic[huc12])
                states=[x for x in os.listdir('IPyHIS/US-STATES') if 'geo.json' in x]
                if len(geoJSONDic)==0:
                    for state in states:
                        #read in state geojson and add it to global cache of stategeojson.                   
                        f=open('IPyHIS/US-STATES/{0}'.format(state))
                        jayson = json.loads(f.read())
                        stateGeoJson=ipyl.GeoJSON(data=jayson,hover_style={'fillColor': 'red'})
                        geoJSONDic[jayson['features'][0]['id']]=stateGeoJson
                        stateGeoJson.on_click(GRABSTATEBOUNDS)
                        mappy.add_layer(stateGeoJson)
                else:
                    for state in geoJSONDic:
                        if geoJSONDic[state] not in mappy.layers:
                            stateGeoJson=geoJSONDic[state]
                            stateGeoJson.on_click(GRABSTATEBOUNDS)
                            mappy.add_layer(stateGeoJson)
            elif toggler.label=='Polygon':
                #remove all layers that not the original map and add the draw control.
                if len(mappy.layers)>1:
                    for state in geoJSONDic:
                        if geoJSONDic[state] in mappy.layers:
                            mappy.remove_layer(geoJSONDic[state])
                    for huc in hucGlobalDic:
                        if hucGlobalDic[huc] in mappy.layers:
                            mappy.remove_layer(hucGlobalDic[huc])
                    for huc12 in huc12GlobalDic:
                        if huc12GlobalDic[huc12] in mappy.layers:
                            mappy.remove_layer(huc12GlobalDic[huc12])
                    if dc not in mappy.controls:
                        mappy.add_control(dc)
            elif toggler.label=='HUC Boundary':
                hucBounds = os.listdir('IPyHIS/hucs')
                if dc in mappy.controls:
                    mappy.remove_control(dc)
                else:
                    for state in geoJSONDic:
                        if geoJSONDic[state] in mappy.layers:
                            mappy.remove_layer(geoJSONDic[state])
                if len(hucGlobalDic)==0:
                    for huc in hucBounds:
                        f=open('IPyHIS/hucs/{0}'.format(huc))
                        jayson=json.loads(f.read())
                        hucGeoJson=ipyl.GeoJSON(data=jayson,hover_style={'fillColor':'red'})
                        hucGlobalDic[jayson['features'][0]['id']]=hucGeoJson
                        hucGeoJson.on_click(HUCZOOM)
                        mappy.add_layer(hucGeoJson)
                else:
                    for huc in hucGlobalDic:
                        if hucGlobalDic[huc] not in mappy.layers:
                            hucGeoJson=hucGlobalDic[huc]
                            hucGeoJson.on_click(HUCZOOM)
                            mappy.add_layer(hucGeoJson)

                mappy.on_moveend(DISPLAYREGIONS)
                    
        toggleButtons.on_msg(toggle_boundaries)
        display(toggleButtons)
        return self.map
    
    def HISGetMetadata(self,medium,keyword):
        # Connect to the HIS Central SOAP API
        hiscentral_wsdl = 'http://hiscentral.cuahsi.org/webservices/hiscentral.asmx?wsdl'
        client = Client(hiscentral_wsdl)# Search for Sites Containing Bromide Data
        params = dict ( getData = 'true',        
                getFacetOnCV = 'true',   
                ymin = min_lat,
                xmin = min_lon,
                ymax = max_lat,
                xmax = max_lon,
                sampleMedium = medium,
                conceptKeyword = keyword,
                dataType = '',
                valueType = '',
                generalCategory = '',
                networkIDs = '',
                beginDate = '',
                endDate = '')
        f = client.factory.create('GetSeriesMetadataCountOrData')
        f.__dict__.update(params)
        # Invoke SOAP Method
        response = client.service.GetCountOrData(f)
        
        #create polygon shape
        polygonshape=shape(coords1).buffer(0.0)
        result=[x for x in response.series.SeriesRecordFull if polygonshape.contains(shapely.geometry.Point([x.longitude,x.latitude]))]
        return result
    
    def HISGetSites(self,medium,keyword):
        # Connect to the HIS Central SOAP API
        hiscentral_wsdl = 'http://hiscentral.cuahsi.org/webservices/hiscentral.asmx?wsdl'
        client = Client(hiscentral_wsdl)# Search for Sites Containing Bromide Data
        params = dict (   
                ymin = min_lat,
                xmin = min_lon,
                ymax = max_lat,
                xmax = max_lon,
                sampleMedium = medium,
                conceptKeyword = keyword,
                networkIDs = '',
                beginDate = '',
                endDate = '')
        f = client.factory.create('GetSites')
        f.__dict__.update(params)
        # Invoke SOAP Method
        response = client.service.GetSites(f)
        polygonshape=shape(coords1).buffer(0.0)
        sites = list(response)[0][1]
        result=[x for x in sites if polygonshape.contains(shapely.geometry.Point([x.Longitude,x.Latitude]))]
        return result

    
        
    
        
        
          
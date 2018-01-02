# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 19:55:30 2017

@author: ibiyt
"""

import geopandas as gpd

def getSitesByHUC12(HUC12):
    if len(HUC12)!=12:
        return 'This is an invalid huc 12 code. Please try again!'
    gdf=gpd.read_file('sitesWithHucs.csv')
    return gdf[['Latitude','Longitude','SiteCode','SiteName','servCode','servURL']].loc[gdf.Huc_Codes==HUC12]

def getSitesByHUC10(HUC10):
    if len(HUC10)!=10:
        return 'This is an invalid huc code. Please try again!'
    gdf=gpd.read_file('sitesWithHucs.csv')
    return gdf[['Latitude','Longitude','SiteCode','SiteName','servCode','servURL']].loc[gdf.Huc_Codes==HUC10]

def getSitesByHUC8(HUC8):
    if len(HUC8)!=8:
        return 'This is an invalid huc code. Please try again!'
    gdf=gpd.read_file('sitesWithHucs.csv')
    return gdf[['Latitude','Longitude','SiteCode','SiteName','servCode','servURL']].loc[gdf.Huc_Codes==HUC8]
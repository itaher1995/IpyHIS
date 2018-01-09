# IpyHIS
An Ipython Module that allows for a visual interface to the HIS API. This module is currently in its first iteration of development. 

## Objective of this Module
To allow hydrologic scientists that use CUAHSI's services to access information using a visual interface or by specific identifiers known as huc codes. This module will work with the HIS API. To learn more about the API click (insert link here.)

## Submodules
Map - A class that derives much of its functionality from the ipyleaflet module. However, it is NOT a subclass.

Site Search - A pool of functions that search sites based on identifiers known as huc codes. Can use huc 8, huc 10 and huc 12.

## Known issues
001 - The logic for toggling between functionalities in the map submodules is not complete. Although you can toggle between the "Polygon" and "State Boundary" functionalities with ease, the full implementation of the "Huc Boundaries" is not completed. This is top priority.

002 - The huc regions (defined as the polygons that appear when you click "Huc Boundary") are overlapping. The main issue with this is that we are creating convex hulls of watershed regions for these polygons. I am currently not sure if simply creating unions of polygons will drastically impact performance or if it is even feasible.

003 - Not all huc-12 sites will load onto the map. This is because during the translation from shape to json, some of the files did not convert into json effectively. This is a matter of fixing the script that created these json.

004 - The huc-12 sites do not load efficiently. Exploring possibilities of how to increase efficiency or working into the interface an live method that explains how many hucs-12s are left to load. This tool is also limited by the data rate of jupyter notebook.

##Documentation

###Map

Map.Map()

Initializes a map with zoom = 3 and centered around North America.

Map.Map.showMap()

Displays an openstreetmap map that is centered around the United States of America. It has three options that allow you to toggle between the following three options:
* Polygon - The option that allows you to extract data at custom made polygons.
* State Boundary - The option that allows you to extract data at state-based boundaries (i.e. Pennsylvania, Texas, etc.)
* HUC Boundary - The option that allows you to extract data based on HUC 12 sites. To learn more about HUC visit (this will be a link.)

After selecting or saving a polygon, it's bounding box is cached. This will allow you to access that data when you call supporting functions.

Map.Map.HISGetMetadata(medium,keyword)

Allows one to gather metadata regarding sites that sample the designated medium and identify with a keyword. This function calls the HIS API's GetMetadata function.

Map.Map.HISGetSites(medium,keyword)

Gathers site names for sites that sample the designated medium and identify with a keyword. This function calls the HIS API's GetSites() function.

###site_search

site_search.getSitesByHUC12(HUC12)

Searches already cached data for the corresponding HUC12 codes.

site_search.getSitesByHUC10(HUC10)

Searches already cached data for the corresponding HUC10 codes.

site_search.getSitesByHUC8(HUC8)

Searches already cached data for the corresponding HUC8 codes.


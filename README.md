# Transit_range_isochrone_mapping
Mapping time based ranges of public transportation services from points of interest. Isochrone is defined as "a line drawn on a map connecting points at which something occurs or arrives at the same time". So in my understanding isochrone map is, contouring points that are at same range from an origin with respect to environmental effects (steepness, traffic, etc...) from a particular point. This project aims to create and display such maps using google_maps.  

This is a dirty mockup project that would hopefully be useful to my real estate agent. It is really hard to find a good (cheap and okayish) apartment in Tokyo, it gets even harder when you don't know much about billions of districts that your agent starts to ask if they are good. Anything helps... 

Idea is, I'll probably be happy with an apartment 20- 25 minutes to common districts, so I can safely return home after a night of drinking in city center. So this project builds an isochronic map of areas that are close to a busy district.


Whole code can be [seen here](https://github.com/umutto/Transit_range_isochrone_mapping/blob/master/tokyo_ischrones_google_maps.ipynb) as a Jupyter notebook or sample results can be [seen here](https://umutto.github.io/Transit_range_isochrone_mapping/isochrone_maps/sample.html).

**Requirements:**  
[googlemaps python API](https://github.com/googlemaps/google-maps-services-python)*  
**can be adapted to use web api if needed*  
[Shapely](https://github.com/Toblerity/Shapely) *required for rough combination of all areas between*  

**Disclaimer:**  
- Google maps api does not support transit distances in Tokyo yet... (Learned that after starting the project) And responses back the walking distances instead. If you set it to driving, or walking with a longer duration, it still works okay for my purposes. But this should work as intended with google maps distance matrix supported regions.  
- Another thing is Google maps api may sometimes return an address that it cannot interpret, maybe its better to try/catch or regex them. Neither of them are done in this project.

---
Heavy calculations are mostly taken from [isocronut](https://github.com/drewfustin/isocronut).

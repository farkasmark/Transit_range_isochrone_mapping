# Transit_range_isochrone_mapping
Mapping time based ranges of public transportation services from points of interest. Isochrone are defined as isochrone is defined as "a line drawn on a map connecting points at which something occurs or arrives at the same time". So in my understanding isochrone map is, contouring points that are at same range with respect to environmental challenges (steepness, traffic, etc...) from a particular point. This project aims to create such maps and display using google_maps.  

This is a dirty mockup project that would hopefully be useful to my real estate agent. It is really hard to find a good (cheap and okayish) apartment in Tokyo, it gets even harder when you don't know much about billions of districts and your agent starts to ask if these areas are good. 

Idea is, I'll probably be happy with an apartment 20- 25 minutes to common districts, so I can safely return home after a night of drinking. So this project builds a isochronic map of areas that are close to a busy district.


Whole code can be [seen here](https://github.com/umutto/Tokyo_Isochrone_Map/blob/master/tokyo_ischrones_google_maps.ipynb) as a Jupyter notebook or sample results can be [seen here](https://umutto.github.io/Tokyo_Isochrone_Map/isochrone_maps/shibuya_ueno_ikebukuro_shimokita_2017-06-13_21-53_.html).

**Requirements:**  
[googlemaps python API](https://github.com/googlemaps/google-maps-services-python) *  
**can easily be adapted to use web api*

**Disclaimer:**  
- Google maps api does not support transit distances in Tokyo yet... (Learned that after starting the project) And responses back the walking distances instead. If you set it to driving, or walking with a longer duration, it still works okay for my purposes. But this should work as intended with supported places.  
- Another thing is Google maps api may sometimes return an address that it cannot interpret, maybe its better to try/catch or regex them.

---
Heavy calculations are mostly taken from [isocronut](https://github.com/drewfustin/isocronut).  
Google maps html is a modified version of generated html from [gmplot](https://github.com/vgm64/gmplot).

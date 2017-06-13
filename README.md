# Tokyo_Isochrone_Map
Mapping time based ranges of public transportation services in points of interests in Tokyo.

This is a dirty mockup project that would hopefully be useful to my real estate agent. It is really hard to find a good (cheap and okayish) apartment in Tokyo, it gets even harder when you don't know much about billions of districts and your agent starts to ask if these areas are good. 

Idea is I'll probably be happy with an apartment 20- 25 minutes to common districts, so I can safely return home after a night of drinking. So this project builds a isochronic map of areas that are close to a busy district.

**Requirements:**
[googlemaps python API](https://github.com/googlemaps/google-maps-services-python) * can easily be adapted to use web api

**Disclaimer:**
Google maps api does not support transit distances in Tokyo yet... (Learned that after the project) And responses back the walking distances instead. It still works okay for the project's purposes.
Another thing is Google maps api may sometimes return an address that it cannot interpret, maybe its better to try/catch or regex them.

---
Calculations are mostly taken from [isocronut](https://github.com/drewfustin/isocronut).

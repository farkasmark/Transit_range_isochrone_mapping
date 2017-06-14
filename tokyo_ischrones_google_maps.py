from math import cos, sin, pi, radians, degrees, asin, atan2
import os
import time
import datetime
import googlemaps
import shapely.geometry as geometry


class isochrone:

    def __init__(self, api_key,
                 departure_date=datetime.datetime.strptime('Jun 12 2017  1:00PM',
                                                           '%b %d %Y %I:%M%p'),
                 transportation_mode="transit", transit_mode="rail",
                 routing_preference="fewer_transfers"):

        self.departure_date = departure_date
        self.transportation_mode = transportation_mode
        self.transit_mode = transit_mode
        self.routing_preference = routing_preference
        self.api_key = api_key
        self.google_maps = googlemaps.Client(key=api_key)

    def select_destination(self, origin, angle, radius):
        # Radius of the Earth in km
        r = 6378.137
        # Bearing in radians converted from angle in degrees
        bearing = radians(angle)
        lat1 = radians(origin["lat"])
        lng1 = radians(origin["lng"])
        lat2 = asin(sin(lat1) * cos(radius / r) + cos(lat1) *
                    sin(radius / r) * cos(bearing))
        lng2 = lng1 + atan2(sin(bearing) * sin(radius / r) *
                            cos(lat1), cos(radius / r) - sin(lat1) * sin(lat2))
        lat2 = degrees(lat2)
        lng2 = degrees(lng2)

        return {"lat": lat2, "lng": lng2}

    def get_bearing(self, origin, destination):
        lat1, lng1 = origin["lat"], origin["lng"]
        lat2, lng2 = destination["lat"], destination["lng"]

        bearing = atan2(sin((lng2 - lng1) * pi / 180) *
                        cos(lat2 * pi / 180),
                        cos(lat1 * pi / 180) * sin(lat2 * pi / 180) -
                        sin(lat1 * pi / 180) * cos(lat2 * pi / 180) *
                        cos((lng2 - lng1) * pi / 180))
        bearing = bearing * 180 / pi
        bearing = (bearing + 360) % 360
        return bearing

    def sort_points(self, origin, iso):
        bearings = [self.get_bearing(origin, row) for row in iso]

        return [i for (b, i) in sorted(zip(bearings, iso))]

    def calc_iso_points(self, geocode, number_of_angles,
                        duration, tolerance, epoch_limit):
        # direction and magnitude of isochronic point ranges
        rad = [duration / 12] * number_of_angles
        phi = [i * (360 / number_of_angles) for i in range(number_of_angles)]

        # location/size of the step to take, similar to learning rate with time
        # based decay
        step = 0.5
        step_decay = .025
        step_base = 1
        iso = [[0, 0]] * number_of_angles

        # epoch is used to break prematurely if it takes too long
        epoch = 0
        converged = False

        while not converged and epoch <= epoch_limit:

            converged = True

            # get predicted point coordinates
            iso = [self.select_destination(geocode, phi[i], rad[i])
                   for i in range(number_of_angles)]

            # Calculate transit distance between original point and predicted points
            # Google maps api can't return public transportation values for Tokyo yet...
            # So it returns walking distances.
            data = self.google_maps.distance_matrix(origins=geocode,
                                                    destinations=iso,
                                                    mode=self.transportation_mode,
                                                    units="metric",
                                                    language="en",
                                                    departure_time=self.departure_date,
                                                    transit_routing_preference=self.routing_preference,
                                                    transit_mode=self.transit_mode)

            # google maps gets confused with the returned addresses,
            # so using coordinates are more robust
            data["destination_addresses"] = iso[:]

            for i in range(number_of_angles):
                data_duration = data["rows"][0]["elements"][
                    i]["duration"]["text"].split()
                data_duration = data_duration[0] if data_duration[
                    1] == 'mins' else data_duration[0] * 60
                data_duration = int(data_duration)

                # If selected point duration is smaller than wanted,
                # make it bigger
                if data_duration < (duration - tolerance):
                    rad[i] *= (step_base + step)
                    converged = False

                # Else If selected point duration is bigger than wanted,
                # make it smaller
                elif data_duration > (duration + tolerance):
                    rad[i] /= (step_base + step)
                    converged = False

                # Else, if points are within range, do nothing,
                # if all points are good it is converged

            epoch += 1
            step = step * 1 / (1 + step_decay * epoch)
            print("Epoch: {}/{}".format(epoch, epoch_limit), end="\r")

            # to throthle the over use of google maps api
            time.sleep(.2)

        print()
        return self.sort_points(geocode, iso)

    def get_isochrone(self, query_location, number_of_angles=20,
                      duration=25, tolerance=10, epoch_limit=15):
        # get latitude and longtitude of the location from google maps
        geocode_result = self.google_maps.geocode(query_location,
                                                  language="en")[0]
        geocode = geocode_result['geometry']['location']

        # calculate approximate isochronic ranges from geocode
        iso = self.calc_iso_points(geocode, number_of_angles,
                                   duration, tolerance, epoch_limit)

        return geocode, iso

    def create_polygon(self, location, fill_opacity, line_opacity, line_weight):
        polygon = "var coords_{} = [".format(location["name"])
        polygon += ",".join(["new google.maps.LatLng({}, {})".
                             format(i["lat"], i["lng"])
                             for i in location["coords"]])
        polygon += "];"
        polygon += """
            var polygon_{0} = new google.maps.Polygon({{
            clickable: false,
            geodesic: true,
            fillColor:"#{1}",
            fillOpacity:{2},
            paths:coords_{0},
            strokeColor:"#{1}",
            strokeOpacity:{3},
            strokeWeight:{4}
            }});
            polygon_{0}.setMap(map);
            """.format(location["name"], location["color"],
                       fill_opacity, line_opacity, line_weight)

        return polygon

    # build a simple google maps html to display, html is a modified version of gmplot
    # from https://github.com/vgm64/gmplot
    def plot_map_to_html(self, center, coords, zoom_level=5,
                         fill_opacity=0.3, line_opacity=1.0, line_weight=1):

        html_text = """
        <html>
        <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
        <title>Simple ischrone map</title>
        <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key={}&libraries=visualization"></script>
        <script type="text/javascript">
            function initialize() {{
                var centerlatlng = new google.maps.LatLng({}, {});
                var myOptions = {{
                    zoom: {},
                    center: centerlatlng,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                }};
                var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
        """.format(self.api_key, center["lat"], center["lng"], zoom_level)

        for location in coords:
            html_text += self.create_polygon(location,
                                             fill_opacity, line_opacity, line_weight)

        html_text += """
            }
            </script>
            </head>
            <body style="margin:0px; padding:0px;" onload="initialize()">
                <div id="map_canvas" style="width: 100%; height: 100%;"></div>
            </body>
            </html>

        """

        return html_text


if __name__ == "__main__":
    api_key = "YOUR API KEY HERE"
    iso_mapper = isochrone(api_key)

    locations = [
        {"address": "2 Chome Dogenzaka, Shibuya-ku, Tōkyō-to 150-0002, Japan",
         "name": "Shibuya", "duration": 45, "angles": 20, "c": "3ea190"},
        {"address": "Japan, 〒110-0005 Tōkyō-to, 台東区Ueno, 7 Chome−1−1",
         "name": "Ueno", "duration": 40, "angles": 20, "c": "6eb190"},
        {"address": "1丁目 Minamiikebukuro Toshima-ku, Tōkyō-to Japan",
         "name": "Ikebukuro", "duration": 35, "angles": 20, "c": "6eb190"},
        {"address": "Japan, 〒155-0031 Tōkyō-to, Setagaya-ku, Kitazawa, 2 Chome−２３",
         "name": "Shimokitazawa", "duration": 30, "angles": 20, "c": "3ea190"},
        {"address": "Japan, 〒180-0003 Tōkyō-to, Musashino-shi, Kichijōji Minamichō, 2 Chome−１ 吉祥寺南町1丁目",
         "name": "Kichioji", "duration": 20, "angles": 20, "c": "ced190"},
        {"address": "Japan, 〒166-0003 Tōkyō-to, Suginami-ku, 杉並区Kōenjiminami, 4 Chome−４８",
         "name": "Koenji", "duration": 25, "angles": 20, "c": "9ec190"},
        {"address": "Japan, 〒103-0012 Tōkyō-to, Chūō-ku, Nihonbashihoridomechō, 2 Chome−１−１３",
         "name": "Nihonbashi", "duration": 25, "angles": 20, "c": "3ea190"},
        {"address": "Japan, 〒141-0021 Tōkyō-to, Shinagawa-ku, Kamiōsaki, 4 Chome−２−１",
         "name": "Meguro", "duration": 25, "angles": 20, "c": "6eb190"},
        {"address": "1 Chome Hyakuninchō, Shinjuku-ku, Tōkyō-to 169-0073, Japan",
         "name": "Okubo", "duration": 20, "angles": 20, "c": "9ec190"}
    ]
    poly_list = []

    for location in locations:
        print("Processing {}...".format(location["name"]))
        geocode, iso = iso_mapper.get_isochrone(location["address"],
                                                duration=location["duration"],
                                                number_of_angles=location["angles"])
<<<<<<< HEAD
        poly_list.append({"name": location["name"], "geocode": geocode,
                          "coords": iso, "color": location["c"],
                          "duration": location["duration"]})

    print("Done.")

    # Rough outer region approximation to contour the areas in between
    outer_points = geometry.MultiPoint([(p["lat"], p["lng"])
                                        for poly in poly_list
                                        for p in poly["coords"]])
    outer_polygon = list(outer_points.convex_hull.exterior.coords)
    centroid = list(outer_points.centroid.coords)[0]

    centroid = {"lat": centroid[0], "lng": centroid[1]}
    outer_polygon = [{"lat": p[0], "lng":p[1]} for p in outer_polygon]

    outer_wrapper = {"name": "outer", "geocode": centroid,
                     "coords": outer_polygon, "color": "95b8af",
                     "duration": 0}
    poly_map = [outer_wrapper] + poly_list

    # create html file
    html_file = iso_mapper.plot_map_to_html(centroid, poly_map, zoom_level=12,
                                            fill_opacity=0.3, line_opacity=0,
                                            line_weight=0)

    # save to local
    path = os.path.join(os.path.dirname(__file__),
                        'isochrone_maps\\shibuya_ueno_ikebukuro_shimokita')
    file_path = "{}_{}_.html".format(path, datetime.datetime.now().
                                     strftime("%Y-%m-%d_%H-%M"))
    with open(file_path, "w") as f:
        print(html_file, file=f)
=======
        poly_list.append({"name": location["name"],
                          "geocode": geocode,
                          "coords": iso,
                          "color": location["c"]})

    center = poly_list[0]["geocode"]
    _, html_file = iso_mapper.plot_map_to_html(api_key, center, poly_list,
                                               file_name='shibuya_ueno_ikebukuro_shimokita',
                                               zoom_level=12,
                                               fill_opacity=0.3, line_opacity=1.0,
                                               line_weight=1)
>>>>>>> 6002e00b4bad3032dff568a9b17fe00cf80652d1

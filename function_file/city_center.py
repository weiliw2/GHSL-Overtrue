from geopy.distance import geodesic
def calculate_bounding_box(city_center_point, x_km, y_km):

    latitude, longitude = city_center_point

    north = geodesic(kilometers=y_km).destination((latitude, longitude), 0).latitude
    south = geodesic(kilometers=y_km).destination((latitude, longitude), 180).latitude
    east = geodesic(kilometers=x_km).destination((latitude, longitude), 90).longitude
    west = geodesic(kilometers=x_km).destination((latitude, longitude), 270).longitude

    return {
        "north": (north, longitude),
        "south": (south, longitude),
        "east": (latitude, east),
        "west": (latitude, west)
    }

city_center_point = (41.8781, -87.6298)
x_km = 5
y_km = 5
bounding_box = calculate_bounding_box(city_center_point, x_km, y_km)
print(bounding_box)

from geopy.distance import geodesic

STORE_LOCATION = (13.026792442998042, 77.68224603078411)  # (latitude, longitude)
MAX_DISTANCE_KM = 5


def verify_geo_location(longitude: float, latitude: float) -> bool:
    customer_location = (latitude, longitude)
    print(customer_location);

    distance = geodesic(STORE_LOCATION, customer_location).km
    print(distance)

    return distance <= MAX_DISTANCE_KM
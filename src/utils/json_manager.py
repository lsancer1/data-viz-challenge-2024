

 # utils 
def extract_rescoordinates(geojson_data):
    """
    *** Autodocstring ***
    Extract coordinates and status from a GeoJSON object.

    Args:
        geojson_data (dict): A dictionary representing GeoJSON data that contains 
                             features with 'geo_point_2d' in their properties.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'lat' (latitude), 
              'lon' (longitude), and 'statut' (status) extracted from the GeoJSON features.
    """
    return [
        {
            'lat': feature['properties']['geo_point_2d']['lat'],
            'lon': feature['properties']['geo_point_2d']['lon'],
            'statut': feature['properties']['statut']
        }
        for feature in geojson_data['features'] if 'geo_point_2d' in feature['properties']
    ]
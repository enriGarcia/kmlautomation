import geopandas as gpd
import fiona
from shapely.geometry import Polygon, Point


HURRICAN_KML = 'al212021_025adv_CONE.kml'
GPS_POINT = (38.27704, -36.63373)

def read_kml(kml_file):
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    df = gpd.read_file(kml_file, driver='KML')
    return df

gdf_hurrican = read_kml(HURRICAN_KML)
hurrican_poly = gdf_hurrican.iloc[0]['geometry']
gps_point = Point(GPS_POINT)

# Interseccion entre el punto del gps y el
# poligono del huracan
print('Hay Interseccion? = ', gps_point.within(hurrican_poly))

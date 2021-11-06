import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, MultiPolygon, shape

# Aqui va el archivo KML
HURRICAN_KML = 'al212021_025adv_CONE.kml'
# Aqui va el punto GPS
GPS_POINT = (-30.0004, 43.63373)


# Convierte de kml a geopandas df
def read_kml(kml_file):
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    df = gpd.read_file(kml_file, driver='KML')
    return df


# Convierte la informacion geometrica del shape de 3D a 2D
def convert_3D_2D(geometry):
    new_geo = []
    for p in geometry:
        if p.has_z:
            if p.geom_type == 'Polygon':
                lines = [xy[:2] for xy in list(p.exterior.coords)]
                new_p = Polygon(lines)
                new_geo.append(new_p)
            elif p.geom_type == 'MultiPolygon':
                new_multi_p = []
                for ap in p:
                    lines = [xy[:2] for xy in list(ap.exterior.coords)]
                    new_p = Polygon(lines)
                    new_multi_p.append(new_p)
                new_geo.append(MultiPolygon(new_multi_p))
    return new_geo

gdf_hurrican = read_kml(HURRICAN_KML)
gdf_hurrican.geometry = convert_3D_2D(gdf_hurrican.geometry)
poly_hurrican = gdf_hurrican.iloc[0]['geometry']

point_gps = Point(GPS_POINT)

# Interseccion entre el punto del gps y el
# poligono del huracan
print('Hay Interseccion? = ', point_gps.within(poly_hurrican))

# Graficando el huracan y el punto GPS
x,y = poly_hurrican.exterior.xy
plt.plot(x,y)
plt.plot(point_gps.x, point_gps.y, marker='o', markersize=3, color="red")
plt.show()

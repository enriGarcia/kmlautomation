import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
import xmltodict
import folium
import webbrowser
from shapely.geometry import Polygon, Point, MultiPolygon, shape
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO


# Aqui va el link
LINK = "http://www.nhc.noaa.gov/gis/kml/nhc_active.kml"
# Aqui va el punto GPS
GPS_POINT = (-30.0004, 43.63373)

#
def scrap():
    #Abrir link
    data = urlopen(LINK)

    dicto = xmltodict.parse(data)
    newDict = dicto["kml"]["Document"]["Folder"]


    wspTemp = ""
    wsp = {}
    cyclones = []
    #crear diccionario
    for x in newDict:
        #agregar los datos de wsp
        if x["@id"] == "wsp":
            wspTemp = x["Folder"]["NetworkLink"]
            for y in wspTemp:

                wsp[y["@id"]] = {
                    "name": y["name"],
                    "visibility": y["visibility"],
                    "open": y["open"],
                    "link": y["Link"]["href"],
                    "kml": kmzToKml(y["Link"]["href"])
                }
            continue
        #extraer los datos cientificos de cada ciclon
        tempMetadata = {}
        for y in x["ExtendedData"][0]["Data"]:
            tempMetadata[y["@name"]] = y["value"]

        #extraer el link y datos generales
        tempDatos = {}
        for y in x["NetworkLink"]:
            tempDatos[y["@id"]] = {
                "name": y["name"],
                "visibility": y["visibility"],
                "link": y["Link"]["href"],
                "kml": kmzToKml(y["Link"]["href"])
            }
        #agregarlo a lista
        cyclones.append({
            "id": x["@id"],
            "name": x["name"],
            "visibility": x["visibility"],
            "metaData": tempMetadata,
            "id": x["@id"],
            "datos": tempDatos

        })

        return wsp


def kmzToKml(link):
    resp = urlopen(link)

    name = ""
    zipfile = ZipFile(BytesIO(resp.read()))
    for x in zipfile.namelist():
        if "kml" in x:
            name = x

    kml = zipfile.open(name, 'r')
    return kml


# Convierte de kml a geopandas df
def read_kml(kml_file):
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    return gpd.read_file(kml_file, driver='KML')


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


# Lee todos los KML y los convierte en polygonos
def read_all_kml(gdf):
    poly_hurrican = []
    for p in gdf_hurrican.geometry:
        if p.geom_type == 'Polygon':
            poly_hurrican.append(p)
        elif p.geom_type == 'MultiPolygon':
            poly_hurrican.append(max(p, key=lambda a: a.area))
    return poly_hurrican


# Devuelve un poligono y un punto
def createPoint(gps_point):
    return Point(gps_point)


# Devuelve si GPS_POINT esta dentro del huracan
def isIntersecting(poly, point):
    danger_info = []
    for p in poly:
        danger_info.append(point.within(p))
    return danger_info


# Grafica el GPS_POINT y el HURRICAN_KML
def graphHurrican(poly, point):
    for p in poly:
        x,y = p.exterior.xy
        plt.plot(x,y)
    plt.plot(point.x, point.y, marker='o', markersize=3, color="red")
    plt.show()



# Programa principal
if __name__ == "__main__":
    wsp = scrap()
    gdf_hurrican = read_kml(wsp["wsp34"]["kml"])
    poly = read_all_kml(gdf_hurrican)
    point = createPoint(GPS_POINT)
    print(isIntersecting(poly, point))

    mymmap = folium.Map(location=[19,-89],zoom_start=6,tiles=None)
    folium.TileLayer("stamenterrain").add_to(mymmap)
    folium.TileLayer("openstreetmap").add_to(mymmap)
    text_dist = 'La distancia es de: ' + str(poly[0].exterior.distance(point)) + ' km'
    folium.Marker(
        location=[point.x, point.y],
        popup="<stong>Aqui estoy</stong>",
        tooltip=text_dist).add_to(mymmap)
    GT = gdf_hurrican.geometry.to_json()
    sp = folium.features.GeoJson(GT,name='Cono')
    mymmap.add_child(sp)
    mymmap.add_child(folium.map.LayerControl())
    mymmap.save('cono.html')
    webbrowser.open('cono.html')
    #graphHurrican(poly, point)

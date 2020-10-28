import os
from io import StringIO

import gpxpy
import gpxpy.gpx
import pynmea2
from lxml import etree
from pykml.factory import GX_ElementMaker as GX
from pykml.factory import KML_ElementMaker as KML
from pykml.parser import Schema
from utils import sd_to_dm

# DATA
GPX_FILE = "data/pre-nav-solo.gpx"
NMEA_FILE = "data/pre-nav-solo.nmea"
KML_FILE = "data/pre-nav-solo.kml"

nmea_buffer = StringIO()

coordinates_buffer = StringIO()
waypoint_placemarks = []

with open(GPX_FILE, "r") as gpx_file:
    gpx = gpxpy.parse(gpx_file)

    poi_count = 0

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                poi_count += 1
                elevation_feet = point.elevation * 3.28084
                print(
                    "Point at ({0},{1}) -> {2} - {3}".format(
                        point.latitude, point.longitude, point.elevation - 50, elevation_feet
                    )
                )

                # Extraction des infos
                speeds = [
                    tag.text for tag in point.extensions if tag.tag.endswith("speed")
                ]
                speedMeterPerSeconds = float(speeds[0]) if speeds else 0

                speedKmh = speedMeterPerSeconds * 3600 / 1000

                time = f"{point.time:%H%M%S.%f}"[:-3]
                lat, lon = sd_to_dm(point.latitude, point.longitude)

                # Génération des traces NMEA
                msg = pynmea2.GGA(
                    "GP",
                    "GGA",
                    (
                        time,
                        lat[0],
                        lat[1],
                        lon[0],
                        lon[1],
                        "1",
                        "00",
                        "",
                        f"{point.elevation:.1f}",
                        "M",
                        "0.0",
                        "M",
                        "",
                        "0000",
                    ),
                )
                nmea_buffer.write(f"{msg}\r\n")
                msg = pynmea2.RMC(
                    "GP",
                    "RMC",
                    (
                        time,  # Timestamp
                        "A",  # Status A or V
                        lat[0],  # Latitude
                        lat[1],  # Latitude direction
                        lon[0],  # Longitude
                        lon[1],  # Longitude
                        f"{speedKmh:.2f}".zfill(6),  # Speed
                        "0.0",  # True course
                        f"{point.time:%d%m%y}",  # Datestamp
                        "",  # Magnetic Variation
                        "",
                        "E",  # Magnetic Variation Direction
                    ),
                )
                nmea_buffer.write(f"{msg}\r\n")

                coordinate = f"{point.longitude},{point.latitude},{point.elevation}"
                coordinates_buffer.write(f"{coordinate}\n")

                description = f"<br/>Altitude {point.elevation:.1f}m {elevation_feet:.1f}f "
                if speedKmh:
                    description += f"<br/>Speed {speedKmh:.2f}km/h"

                waypoint_placemarks.append(
                    KML.Placemark(
                        KML.name(f"POI #{poi_count}"),
                        KML.description(description),
                        KML.visibility(0),
                        KML.styleUrl("#IconWpt"),
                        KML.Point(
                            KML.altitudeMode("absolute"),
                            KML.extrude("1"),
                            KML.coordinates(coordinate),
                        )
                    )
                )

        


# Generate NMEA file
with open(NMEA_FILE, "w") as nmea_file:
    nmea_file.write(nmea_buffer.getvalue())

# Generate KML file
# Generation du fichier KML
kml_name = os.path.basename(KML_FILE).rsplit(".", 1)[0]


doc = KML.kml(
    KML.Document(
        KML.name(kml_name),
        KML.description("Trace GPS — gpxutils"),
        KML.Folder(
            KML.name("Mes vols"),
            KML.Placemark(
                KML.name(kml_name),
                KML.description("Trace GPS — gpxutils"),
                KML.styleUrl("#yellowLineGreenPoly"),
                KML.Style(
                    KML.LineStyle(KML.color("7fff0000"), KML.width(4)),
                    KML.PolyStyle(KML.color("7fff0000"),),
                    id="yellowLineGreenPoly",
                ),
                KML.LineString(
                    KML.extrude(1),
                    KML.tessellate(0),
                    KML.altitudeMode("absolute"),
                    KML.coordinates(coordinates_buffer.getvalue()),
                ),
                id="",
            ),
        ),

        KML.Folder(
            KML.name("Trace Waypoint"),
            *waypoint_placemarks
        ),
    )
)

with open(KML_FILE, "wb") as kml_file:
    kml_file.write(etree.tostring(doc, pretty_print=True))

import gpxpy


if __name__ == "__main__":

    with open('/home/richja/Downloads/City_Loop.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                print(f'{point.time} Point at ({point.latitude},{point.longitude}) -> {point.elevation}')


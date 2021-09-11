class Point:
    def __init__(self, lat, lon):
        self.lon = lon
        self.lat = lat

    def __sub__(self, other):
        return Point(self.lat - other.lat, self.lon - other.lon)

    def __add__(self, other):
        return Point(self.lat + other.lat, self.lon + other.lon)

    def __mul__(self, other):
        if isinstance(other, float):
            return Point(self.lat * other, self.lon * other)
        raise ValueError(f"Can't multiply a {type(self)} with a {type(other)}")

    def __str__(self):
        return f"Point(lat={self.lat}, lon={self.lon}"

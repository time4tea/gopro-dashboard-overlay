class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, float):
            return Coordinate(self.x * other, self.y * other)
        raise ValueError(f"Can't multiply a {type(self)} with a {type(other)}")

    def __str__(self):
        return f"Coordinate(x={self.x}, y={self.y})"

    def tuple(self):
        return self.x, self.y


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

    def __rmul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        return f"Point(lat={self.lat}, lon={self.lon})"

    def __repr__(self):
        return str(self)


class Point3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Point3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Point3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other):
        if isinstance(other, float):
            return Point3(self.x * other, self.y * other, self.z * other)
        raise ValueError(f"Can't multiply a {type(self)} with a {type(other)}")

    def __str__(self):
        return f"Point3(x={self.x}, y={self.y}, z={self.z})"

    def __repr__(self):
        return str(self)

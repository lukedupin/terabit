import math
from website.helpers.util import xfloat

# Handle comparison box for lat/lng
class GeoBox:
    def __init__( self, top=0, right=0, bottom=0, left=0 ):
        self.First = True
        self.Top = top
        self.Right = right
        self.Bottom = bottom
        self.Left = left


    # Create a new bounding box around the given center
    @staticmethod
    def box( lat, lng, dist=0 ):
        if dist <= 0:
            return GeoBox( top=lat, right=lng, bottom=lat, left=lng )

        # Calculate the corner of the box
        dist2 = xfloat(dist) * 1.414 #Root 2
        tup = distanceBearing( lat, lng, dist2, 45 )

        # Get a distance from center to bearing
        dlat = tup[0] - xfloat(lat)
        dlng = tup[1] - xfloat(lng)

        return GeoBox( top=tup[0], right=tup[1],
                       bottom=(xfloat(lat) - dlat), left=(xfloat(lng) - dlng))


    # True if the lat/lng is inside the bounding box
    def contains( self, lat, lng ):
        return self.Top >= lat and self.Bottom <= lat and self.Right >= lng and self.Left <= lng


    # Returns true if another bounding box overlaps with me
    def overlaps( self, box ):
        return not (box.Top < self.Bottom or  box.Right < self.Left or \
                    box.Bottom > self.Top or box.Left > self.Right)


    # Return the center of the box
    def center( self ):
        return ((self.Top - self.Bottom) / 2.0, (self.Right - self.Left) / 2.0)


    # Width of the box in meters
    def width( self ):
        lat = self.center()[0]
        return distance( lat, self.Left, lat, self.Right )


    # Height of the box in meters
    def height( self ):
        lng = self.center()[1]
        return distance( self.Top, lng, self.Bottom, lng )


    # Increase the size of the box to hold this point
    def add( self, lat, lng, tol = 0.0 ):
        # On the first pass, we recenter the box
        if self.First:
            self.Right = self.Left = lng
            self.Top = self.Bottom = lat
            self.First = False

        # Add the points
        if lng + tol > self.Right:
            self.Right = lng + tol
        if lng - tol < self.Left:
            self.Left = lng - tol
        if lat + tol > self.Top:
            self.Top = lat + tol
        if lat - tol < self.Bottom:
            self.Bottom = lat - tol

        return self


# Calculate the distance from two lat/lng points
def distance( lat1, lng1, lat2, lng2 ):
    lat1 = xfloat(lat1)
    lng1 = xfloat(lng1)
    lat2 = xfloat(lat2)
    lng2 = xfloat(lng2)
    diff_lat = math.radians( lat2 - lat1 )
    diff_lng = math.radians( lng2 - lng1 )
    lat1 = math.radians( lat1 )
    lat2 = math.radians( lat2 )

    #Call the distance
    sin_lat = math.sin(diff_lat / 2.0)
    sin_lng = math.sin(diff_lng / 2.0)
    val = sin_lat * sin_lat + \
          sin_lng * sin_lng * \
          math.cos(lat1) * math.cos(lat2)
    raw = 2.0 * math.atan2( math.sqrt(val), math.sqrt(1.0-val) )

    # Convert to meters
    return EARTH_RADIUS * raw

# Return the bearing from two given points
def bearing( lat1, lng1, lat2, lng2 ):
    lat1 = xfloat(lat1)
    lng1 = xfloat(lng1)
    lat2 = xfloat(lat2)
    lng2 = xfloat(lng2)
    y = math.sin(lng2 - lng1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - \
            math.sin(lat1) * math.cos(lat2) * math.cos(lng2 - lng1)
    return math.degrees( math.atan2(y, x) )

# Returns a lat/lng a distance and bearing away from the provided lat/lng
def distanceBearing( dlat, dlng, dist, bearing ):
    dlat = xfloat(dlat)
    dlng = xfloat(dlng)
    dist = xfloat(dist)
    bearing = xfloat(bearing)

    lat = math.radians( dlat )
    lng = math.radians( dlng )
    br = math.radians( bearing )
    d = dist / EARTH_RADIUS

    # Calculate my new lat/lng
    result_lat = math.asin( math.sin(lat)*math.cos(d) + \
                 math.cos(lat) * math.sin(d) * math.cos(br) )
    result_lng = lng + math.atan2( math.sin(br) * math.sin(d)*math.cos(lat), \
                                   math.cos(d) - math.sin(lat) * math.sin(result_lat))

    # Convert my lat to the correct quadrant (This will fail if our distance is traveling over a quad bounds)
    r_lat = math.degrees(result_lat)
    if dlat < -90.0:
        return (-(180 + r_lat), math.degrees(result_lng))
    elif dlat > 90.0:
        return (180 - r_lat, math.degrees(result_lng))

    return (r_lat, math.degrees(result_lng))

EARTH_RADIUS = 6371000

# Calc the speed meteres and timestamps
def speedDist( m_s, ts0, ts1 ):
    if ts0 == ts1:
        return 0
    
    # Get the speed
    d = (ts1 - ts0)
    if isinstance(d, int) or isinstance(d, float):
        ts = xfloat(d)
    else:
        ts = d.days * 86400.0 + float(d.seconds) + float(d.microseconds / 1000000.0)
    return m_s / math.fabs( ts )

# Calc the speed of two points and unix timestamps
def speed( lat0, lng0, ts0, lat1, lng1, ts1 ):
    if ts0 == ts1:
        return 0
    
    # Get the speed
    m_s = distance( lat0, lng0, lat1, lng1 )
    return speedDist( m_s, ts0, ts1 )

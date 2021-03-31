  //Return the distance
export default class Geo {
    static distance( lat1, lng1, lat2, lng2 ) {
        const RADIUS = 6371000;

        //Convert from degrees to radians
        const diff_lat = ( lat2 - lat1 ) / 180.0 * 3.14159;
        const diff_lng = ( lng2 - lng1 ) / 180.0 * 3.14159;
        lat1 = ( lat1 ) / 180.0 * 3.14159;
        lat2 = ( lat2 ) / 180.0 * 3.14159;

        //calc my distance value
        const d_sin_lat = Math.sin(diff_lat / 2.0);
        const d_sin_lng = Math.sin(diff_lng / 2.0);
        const a = (d_sin_lat * d_sin_lat) +
                (d_sin_lng * d_sin_lng) * (Math.cos(lat1) * Math.cos(lat2));
        const c = 2.0 * Math.atan2( Math.sqrt(a), Math.sqrt(1.0-a) );

        //Convert to the earth's radius
        return RADIUS * c;
    }

    //Return a new lat lng based on current point, distance and bearing
    static distanceBearing( lat1, lng1, dist, bearing ) {
        const RADIUS = 6371000;

        //Setup my input variables
        const br = bearing * Math.PI / 180.0;
        const d = dist / RADIUS;
        lat1 = lat1 * Math.PI / 180.0;
        lng1 = lng1 * Math.PI / 180.0;

        //Calculate my new lat/lng
        const lat2 = Math.asin( Math.sin(lat1) * Math.cos(d) +
                                Math.cos(lat1) * Math.sin(d) * Math.cos(br) );
        const lng2 = lng1 + Math.atan2( Math.sin(br) * Math.sin(d) * Math.cos(lat1),
                                        Math.cos(d) - Math.sin(lat1) * Math.sin(lat2));

        return { lat: lat2 * 180.0 / Math.PI,
                 lng: lng2 * 180.0 / Math.PI };
    }

    static boxCorners( lat, lng, dist ) {
        const corner = this.distanceBearing( lat, lng, dist * 1.414213562, 45 )

        const lat_diff = corner.lat - lat
        const lng_diff = corner.lng - lng

        return [
            [lng + lng_diff, lat + lat_diff],
            [lng + lng_diff, lat - lat_diff],
            [lng - lng_diff, lat - lat_diff],
            [lng - lng_diff, lat + lat_diff],
            [lng + lng_diff, lat + lat_diff],
        ]
    }
}


  /*
    //Return the speed based on distance and time
  double Geo::speedDist( double m_s, qint64 ts0, qint64 ts1 )
  {
    if ( ts0 == ts1 )
      return 0;

      //Get the speed
    double ts = qAbs( (double)(ts1 - ts0) / 1000000.0);
    return m_s / ts;
  }

    //Return the speed
  double Geo::speed( double lat0, double lng0, qint64 ts0,
                     double lat1, double lng1, qint64 ts1 )
  {
    if ( ts0 == ts1 )
      return 0;

      //Get the speed
    double m_s = distance( lat0, lng0, lat1, lng1 );
    return speedDist( m_s, ts0, ts1 );
  }
  */

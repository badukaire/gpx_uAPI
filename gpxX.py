import sys

# local dir imports
from gpxpy import gpxpy
from gpxpy.gpxpy import gpx


print "read from stdin ..."
lFileGPX = sys.stdin

try :
  gXmlGPX = gpxpy.parse( lFileGPX )
  lFileGPX.close()
  print "file read and parsed OK"

except :
  print "FATAL: Error parsing GPX data"
  raise
  sys.exit( 1 )


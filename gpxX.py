import sys
import getopt
from datetime import datetime
from datetime import timedelta

# local dir imports
from gpxpy import gpxpy
from gpxpy.gpxpy import gpx


def eprint( sErrorMsg ) :
  sys.stderr.write( sErrorMsg )
  sys.stderr.write( "\n" )


# TODO : when classifying, use a __doc__ string
def usage() :

  print "displays/edits a GPX file"
  print "the file can be a parameter (after options) or stdin"
  print ""
  print "options :"
  print "* -h : display this help text"
  print "* -d <displayWhat>: what to display"
  print "  <displayWhat> can be: r/routes, w/waypoints, t/tracks"
  print "* -n <displayWhich>: which one to display (number starting by 1)"
  print "* -T <datetime>: reset initial time to provided ISO-format datetime"
  print "* -o <file>: output file, compulsory for GPX-data transforming options"
  print ""
  print "Examples:"
  print "python gpxX.py -h"
  print "python gpxX.py -d w"
  print "python gpxX.py -d waypoints -d t"
  print "python gpxX.py -d tracks -n 2"
  print "python gpxX.py -T \"2016-06-06 12:00:01\" -o jun06.gpx"


def checkOptions( pListParams ) :

  global gsFileGPX
  print( "checkOptions, args:", pListParams )
  try:
    lOptList, lList = getopt.getopt( pListParams, 'o:T:n:d:h' )

  except getopt.GetoptError:
    eprint( "FATAL : error analyzing command line options" )
    eprint( "" )
    usage()
    sys.exit( 1 )

  # TODO : use shift / setenv --

  #print "parsed opts list:", lOptList
  #print "remaining p list:", lList
  for lOpt in lOptList :
    #print "-- loop lOpt: " + str( lOpt )
    if lOpt[0] == '-h' :
      usage()
      sys.exit( 0 )
    elif lOpt[0] == "-n" :
      lsVal = lOpt[1]
      try :
        liVal = int( lsVal )
      except :
        eprint( "FATAL: %s not a valid number" % lsVal )
        eprint( "" )
        usage()
        sys.exit( 1 )
      if liVal > 0 :
        global giWhich
        giWhich = liVal
      else :
        eprint( "FATAL: %d must be >= 1" % liVal )
        usage()
        sys.exit( 1 )
    elif lOpt[0] == "-d" :
      lsVal = lOpt[1]
      if lsVal == "w" or lsVal == "waypoints" :
        global gbDispWaypts
        gbDispWaypts = True
      elif lsVal == "t" or lsVal == "tracks" :
        global gbDispTracks
        gbDispTracks = True
      elif lsVal == "r" or lsVal == "routes" :
        global gbDispRoutes
        gbDispRoutes = True
      else :
        eprint( "FATAL: Invalid item to display %s" % lsVal )
        eprint( "==========" )
        eprint( "" )
        usage()
        sys.exit( 1 )
    elif lOpt[0] == "-o" :
      lsVal = lOpt[1]
      global gsOutput
      gsOutput = lsVal
    elif lOpt[0] == "-T" :
      lsVal = lOpt[1]
      try :
        lDTval = datetime.strptime( lsVal, "%Y-%m-%d %H:%M:%S" )
      except :
        eprint( "FATAL: %s not a valid ISO-format datetime" % lsVal )
        eprint( "" )
        usage()
        sys.exit( 1 )
      if not lDTval == None :
        global gDTnew
        gDTnew = lDTval
        print "gDTnew :", gDTnew

  #print "loop finished, lList => ", lList
  if len( lList ) > 0 :
    gsFileGPX = lList[ 0 ]
    print "will read file %s" % gsFileGPX


def dispPoint( pPoint ) :
  print "Point at ({0},{1}) -> {2}".format( pPoint.latitude, pPoint.longitude, pPoint.elevation )
  print "-- timestamp:%s:" % pPoint.time


def resetTrackTime() :
  global giWhich
  global gDTnew
  lTimeIni = None
  liTrack = 0
  for lTrack in gXmlGPX.tracks:
    liTrack += 1
    print "track #%d ..." % liTrack
    if giWhich > 0 :
      print "giWhich = %d" % giWhich
      if not liTrack == giWhich :
        print "skip track #%d" % liTrack
        continue

    print "============="
    print "track #%d name:%s:" % ( liTrack, lTrack.name )
    liSegment = 0
    for lSegment in lTrack.segments:
      liSegment += 1

      # empty segment for the 
      #lSegmentOut = gpx.GPXTrackSegment()
      print "--"
      print "segment #%d, track #%d" % ( liSegment, liTrack )
      for lPoint in lSegment.points:
        if lTimeIni == None :
          print "lTimeIni == None ..."
          lDT = lPoint.time
          print lDT
          lTdiff = gDTnew - lDT
          print "=>", gDTnew
          print "time diff:", lTdiff
          lDTnew = lDT + lTdiff
          print "new initial time:", lDTnew
          lTimeIni = lDTnew
        dispPoint( lPoint )
        print "--"
        #lPoint2 = gpx.GPXTrackPoint()
        lPoint.time += lTdiff
        print "----"
      print "end of segment #%d, lTrack #%d" % ( liSegment, liTrack )
      print "----"
    print "end of track #%d" % ( liTrack )
    print "--------"
    print ""
  global gsOutput
  print "write new XML into %s file ..." % ( gsOutput )
  try :
    lFileOut = open( gsOutput, "w" )
  except :
    eprint( "FATAL, can not open output file %s, quitting ..." % ( gsOutput ) )
    sys.exit( 1 )

  lFileOut.write( gXmlGPX.to_xml() )
  lFileOut.close()
  print "new XML written into %s file" % ( gsOutput )


def dispTracks() :
  lTimeIni = None
  liTrack = 0
  for lTrack in gXmlGPX.tracks:
    liTrack += 1
    global giWhich
    if giWhich > 0 :
      print "giWhich = %d" % giWhich
      if not liTrack == giWhich :
        print "skip track #%d" % liTrack
        continue
    print "============="
    print "track #%d name:%s:" % ( liTrack, lTrack.name )
    liSegment = 0
    for lSegment in lTrack.segments:
      liSegment += 1
      print "--"
      print "segment #%d, track #%d" % ( liSegment, liTrack )
      for lPoint in lSegment.points:
        if lTimeIni == None :
          lTimeIni = lPoint.time
          print "lTimeIni =", lTimeIni
        dispPoint( lPoint )
        lTimeEnd = lPoint.time
      print "end of segment #%d, lTrack #%d" % ( liSegment, liTrack )
      print "----"
    print "end of track #%d" % ( liTrack )
    lTdiff = lTimeEnd - lTimeIni
    print "start time: %s - end time: %s" % ( str( lTimeIni ), str( lTimeEnd ) )
    print "time lapse: %s" % ( str( lTdiff ) )
    print "--------"
    print ""


def dispWaypts() :
  liWaypt = 0
  for lWaypoint in gXmlGPX.waypoints:
    liWaypt += 1
    print "============="
    print "waypoint #%d" % ( liWaypt )
    print "waypoint {0} -> ({1},{2})".format( lWaypoint.name, lWaypoint.latitude, lWaypoint.longitude )
    print "-- comment:", lWaypoint.comment
    print "-- description:", lWaypoint.description
    print "-- symbol:", lWaypoint.symbol
    

def dispRoutes() :
  liRoute = 0
  for lRoute in gXmlGPX.routes:
    liRoute += 1
    print "============="
    print "Route: #%d" % ( liRoute )
    for lPoint in lRoute.points:
      dispPoint( lPoint )

# main starts here

gbDispTracks = False
gbDispWaypts = False
gbDispRoutes = False
giWhich = 0

gsFileGPX = None
gsOutput = None
gDTnew = None

liArgs = len( sys.argv )
if liArgs < 2 :
  print "NO params provided => will read from stdin and display everything"
  lFileGPX = sys.stdin
  gbDispTracks = True
  gbDispWaypts = True
  gbDispRoutes = True
else : # stdin, display everything, dont transform
  checkOptions( sys.argv[ 1 : ] )

if not gsFileGPX == None :
  try :
    lFileGPX = open( gsFileGPX, "r" )
  except :
    eprint( "FATAL: could not open file %s, quitting ..." % ( gsFileGPX ) )
    sys.exit( 1 )
else :
  eprint( "NO GPX file provided, read from stdin ..." )
  lFileGPX = sys.stdin


try :
  gXmlGPX = gpxpy.parse( lFileGPX )
  lFileGPX.close()
  print "file read and parsed OK"

except :
  eprint( "FATAL: Error parsing GPX data" )
  raise
  sys.exit( 1 )


if gbDispTracks == False and gbDispWaypts == False and gbDispRoutes == False :
  print "NOT displaying anything"
  print "transforming GPX data? ..."
  if gDTnew == None :
    eprint( "FATAL, can't transform data, need to have a datetime to reset (-T option)" )
    eprint( "" )
    usage()
    sys.exit( 1 )
  if gsOutput == None :
    eprint( "FATAL, can't transform data, need to have an output file (-o option)" )
    eprint( "" )
    usage()
    sys.exit( 1 )
  resetTrackTime()
else :
 if gbDispTracks == True :
  print "================"
  print "display Tracks ..."
  dispTracks()
  print ""
  print "Tracks displayed"
  print "================"
  print ""
 if gbDispWaypts == True :
  print "================"
  print "display Waypts ..."
  dispWaypts()
  print ""
  print "Waypts displayed"
  print "================"
  print ""
 if gbDispRoutes == True :
  print "================"
  print "display Routes ..."
  dispRoutes()
  print ""
  print "Routes displayed"
  print "================"
  print ""


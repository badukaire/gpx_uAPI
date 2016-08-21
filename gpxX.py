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

  print ""
  print "----------"
  print "gpxX.py : displays/edits a GPX file"
  print "the file can be a parameter (after options) or stdin"
  print ""
  print "options :"
  print "* -h : display this help text"
  print "* -d <displayWhat>: what to display"
  print "  <displayWhat> can be: r/routes, w/waypoints, t/tracks"
  print "* -n <displayWhich>: which one to display (number starting by 1)"
  print "* -s <segment>: which segment to display/edit (number starting by 1)"
  print "* -o <file>: output file, compulsory for GPX-data transforming options"
  print "* -T <datetime>: reset initial time to provided ISO-format datetime"
  print "* -D <duration>: track duration (-n must be specified / max 24h)"
  print ""
  print "Examples: (must have at least a -d or -D/-T or -X option)"
  print "python gpxX.py -h"
  print "python gpxX.py -d w"
  print "python gpxX.py -d waypoints -d t"
  print "python gpxX.py -d tracks -n 2"
  print "python gpxX.py -T \"2016-06-06 12:00:01\" -o jun06.gpx"
  print "python gpxX.py -n 2 -T \"2016-06-06 12:00:01\" -o jun06.gpx"
  print "python gpxX.py -n 2 -D 2:03:01 -T \"2016-06-06 12:00:01\" -o jun06.gpx"


def checkOptions( pListParams ) :

  global gsFileGPX
  print( "checkOptions, args:", pListParams )
  try:
    lOptList, lList = getopt.getopt( pListParams, 'o:D:T:s:n:d:hv' )

  except getopt.GetoptError:
    eprint( "FATAL : error analyzing command line options (unknown/bad formatted option?)" )
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
    elif lOpt[0] == '-v' :
      global gbVerbose
      gbVerbose = True
      print "will be verbose (many output)"
    elif lOpt[0] == "-s" :
      lsVal = lOpt[1]
      try :
        liVal = int( lsVal )
      except :
        eprint( "FATAL: %s not a valid segment number (-s)" % lsVal )
        usage()
        sys.exit( 1 )
      if liVal > 0 :
        global giSegment
        giSegment = liVal
        print "segment (-s) set to %d" % ( giSegment )
      else :
        eprint( "FATAL: %d (-s) must be >= 1" % liVal )
        usage()
        sys.exit( 1 )
    elif lOpt[0] == "-n" :
      lsVal = lOpt[1]
      try :
        liVal = int( lsVal )
      except :
        eprint( "FATAL: %s (-n) not a valid number" % lsVal )
        usage()
        sys.exit( 1 )
      if liVal > 0 :
        global giWhich
        giWhich = liVal
        print "item (-n) set to %d" % ( giWhich )
      else :
        eprint( "FATAL: %d (-n) must be >= 1" % liVal )
        usage()
        sys.exit( 1 )
    elif lOpt[0] == "-d" :
      lsVal = lOpt[1]
      if lsVal == "w" or lsVal == "waypoints" :
        global gbDispWaypts
        gbDispWaypts = True
        print "will display (-d) waypoints"
      elif lsVal == "t" or lsVal == "tracks" :
        global gbDispTracks
        gbDispTracks = True
        print "will display (-d) tracks/segments"
      elif lsVal == "r" or lsVal == "routes" :
        global gbDispRoutes
        gbDispRoutes = True
        print "will display (-d) routes"
      else :
        eprint( "FATAL: Invalid item (-d) to display %s" % lsVal )
        usage()
        sys.exit( 1 )
    elif lOpt[0] == "-o" :
      lsVal = lOpt[1]
      global gsOutput
      gsOutput = lsVal
      print "output file (-o) : %s" % ( gsOutput )
    elif lOpt[0] == "-D" :
      lsVal = lOpt[1]
      try :
        lDTval = datetime.strptime( lsVal, "%H:%M:%S" )
      except :
        eprint( "FATAL: %s (-D) not a valid ISO-format duration (max is 23:59:59)" % lsVal )
        usage()
        sys.exit( 1 )
      #print "gDTzero:", gDTzero
      if not lDTval == None :
        global gDurationNew
        gDurationNew = lDTval - gDTzero
        print "duration (-D) to set :", gDurationNew
        #print "gDurationNew :", gDurationNew.__class__
    elif lOpt[0] == "-T" :
      lsVal = lOpt[1]
      try :
        lDTval = datetime.strptime( lsVal, "%Y-%m-%d %H:%M:%S" )
      except :
        eprint( "FATAL: %s (-T) not a valid ISO-format datetime" % lsVal )
        usage()
        sys.exit( 1 )
      if not lDTval == None :
        global gDTnew
        gDTnew = lDTval
        print "date (-T) to reset to :", gDTnew

  #print "loop finished, lList => ", lList
  liLenList = len( lList )
  if liLenList > 0 :
    gsFileGPX = lList[ 0 ]
    print "input will be read from file %s" % gsFileGPX
    if liLenList > 1 :
      print "the following %d files will be ignored" % ( liLenList - 1 )
      #gsFileGPX = lList[ 0 ]



def dispPoint( pPoint ) :
  print "Point at ({0},{1}) -> {2}".format( pPoint.latitude, pPoint.longitude, pPoint.elevation )
  print "-- timestamp:%s:" % pPoint.time


def resetTrackTime() :
  lbOK = True
  global giSegment
  global giWhich
  global gDTnew
  lDurationNew = None
  lTimeIni = None
  liTrack = 0
  for lTrack in gXmlGPX.tracks:
    lbDontTouch = False
    liTrack += 1
    print "track #%d ..." % liTrack
    if giWhich > 0 :
      print "giWhich = %d" % giWhich
      if not liTrack == giWhich :
        print "track #%d, dont touch anything ..." % liTrack
        lbDontTouch = True
      else :
        global gDurationNew
        if not gDurationNew == None :
          lDurationNew = gDurationNew
          print "will adjust track time to fit into a %s duration" % ( str( gDurationNew ) )
        else :
          print "track time will just be shifted (duration won't be changed)"

    print "============="
    print "track #%d name:%s:" % ( liTrack, lTrack.name )
    liSegment = 0
    for lSegment in lTrack.segments:
      lbDontTouch = False
      liSegment += 1
      print "--"
      print "segment #%d ..." % liSegment
      global giSegment
      if giSegment > 0 :
        print "giSegment = %d" % giSegment
        if not liSegment == giSegment :
          print "segment #%d, dont touch anything" % liSegment
          lbDontTouch = True

      # TODO : count points for all segments first, for splitting time
      # <trkseg>
      if not lDurationNew == None :
        liPoints = len( lSegment.points )
        lTDpoint = lDurationNew / liPoints
        lDTaccu = timedelta( 0 )
        print "points = %d, point Timedelta: %s" % ( liPoints, str( lTDpoint ) )
        print "lDTaccu:", lDTaccu

      # empty segment for the
      #lSegmentOut = gpx.GPXTrackSegment()
      print "--"
      print "segment #%d, track #%d" % ( liSegment, liTrack )
      for lPoint in lSegment.points:
       if lbDontTouch == False :
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
        print "=>"
        #lPoint2 = gpx.GPXTrackPoint()
        if lDurationNew == None :
          lPoint.time += lTdiff
        else :
          lPoint.time = gDTnew
          lPoint.time += lDTaccu
          lDTaccu += lTDpoint
          print "lDTaccu:", lDTaccu
        dispPoint( lPoint )
       else :
        dispPoint( lPoint )
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
    lbOK = False

  lFileOut.write( gXmlGPX.to_xml() )
  lFileOut.close()
  print "new XML written into %s file" % ( gsOutput )

  return lbOK


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
      print "segment #%d ..." % liSegment
      print "--"
      global giSegment
      if giSegment > 0 :
        print "giSegment = %d" % giSegment
        if not liSegment == giSegment :
          print "skip segment #%d" % liSegment
          continue
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

def display() :
  global gbDispWaypts, gbDispTracks, gbDispRoutes

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

def setOpenFile( psFileGPX ) :
  """
  psFileGPX : input, the file name (string)
  lFileGPX : output, the file descriptor (None if error)
  """
  lFileGPX = None
  if not psFileGPX == None :
    try :
      lFileGPX = open( psFileGPX, "r" )
    except :
      eprint( "FATAL: could not open file %s, quitting ..." % ( gsFileGPX ) )
  else :
    eprint( "NO GPX file provided, read from stdin ..." )
    lFileGPX = sys.stdin
  return lFileGPX


def parseGpxFile( pFileGPX ) :
  """
  pFileGPX : input, the file
  lXmlGPX : output, the parsed content (None if error)
  """
  lXmlGPX = None
  try :
    lXmlGPX = gpxpy.parse( pFileGPX )
    pFileGPX.close()
    print "file read and parsed OK"

  except :
    eprint( "FATAL: Error parsing GPX data" )
    raise

  return lXmlGPX

# main starts here

gbVerbose = False
gbDispTracks = False
gbDispWaypts = False
gbDispRoutes = False
giWhich = 0
giSegment = 0

gsFileGPX = None
gsOutput = None
gDTnew = None
gDurationNew = None

gDTzero = datetime.strptime( "00:00:00", "%H:%M:%S" )
gTdiffZero = gDTzero - gDTzero

# if no params, this should return []
lListParams = sys.argv[ 1 : ]

# TODO : find way to remove dumb if
if not lListParams == None :

  checkOptions( lListParams )
  lbOptsOK = validateOptions()
  if lbOptsOK == False :
    usage()
    sys.exit( 1 )
  # TODO : use a backup of gsXformFile when reading the file for unsetting and validating

gFileGPX = setOpenFile( gsFileGPX )
if gFileGPX == None :
  sys.exit( 1 )

gXmlGPX = parseGpxFile( gFileGPX )
if gXmlGPX == None :
  sys.exit( 1 )

if gbDispTracks == False and gbDispWaypts == False and gbDispRoutes == False :
  print "transform GPX data ..."
  if resetTrackTime() == False :
    sys.exit( 1 )
else : # display
  display()


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
  print "* -X <command file>: file with sets of -T/-D/-n/-s options"
  print ""
  print "Examples: (must have at least a -d or -D/-T or -X option)"
  print "python gpxX.py -h"
  print "python gpxX.py -d w"
  print "python gpxX.py -d waypoints -d t"
  print "python gpxX.py -d tracks -n 2"
  print "python gpxX.py -T \"2016-06-06 12:00:01\" -o jun06.gpx"
  print "python gpxX.py -n 2 -T \"2016-06-06 12:00:01\" -o jun06.gpx"
  print "python gpxX.py -n 2 -D 2:03:01 -T \"2016-06-06 12:00:01\" -o jun06.gpx"
  print "python gpxX.py -n 2 -s 1 -D 2:03:01 -T \"2016-06-06 12:00:01\" -o jun06.gpx"
  print "python gpxX.py -X setJun06.txt -o jun06.gpx"


def checkOptions( pListParams ) :

  global gsFileGPX
  print( "checkOptions, args:", pListParams )
  try:
    lOptList, lList = getopt.getopt( pListParams, 'X:o:D:T:s:n:d:hv' )

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
    elif lOpt[0] == "-X" :
      lsVal = lOpt[1]
      global gsXformFile
      gsXformFile = lsVal
      print "transform command file (-X) : %s" % ( gsXformFile )
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
        lDTval = datetime.strptime( lsVal, "%Y-%m-%dT%H:%M:%S" )
      except :
        eprint( "FATAL: %s (-T) not a valid ISO-format (like \"2016-08-20T13:09:47\") datetime" % lsVal )
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


def cleanXformOpts() :
  """
  cleans up transform options
  to be called only when using command file (-X)
  """
  global giWhich, giSegment
  global gDurationNew, gDTnew

  giWhich = 0
  giSegment = 0
  gDurationNew = None
  gDTnew = None


def validateOptionsXform() :
  global giAction
  global gsXformFile
  global giWhich, giSegment
  global gDurationNew, gDTnew
  global gbDispWaypts, gbDispTracks, gbDispRoutes

  lbOK = True
  if not gsXformFile == None :
    lbOK == False
    print "ERROR, -X cant be set on file"
  if gbDispWaypts == True or gbDispTracks == True or gbDispRoutes == True :
    lbOK == False
    print "ERROR, -d cant be set on transform file"
  if not gsOutput == None :
    lbOK = False
    print "ERROR : option -o can NOT be set on transform file"
  # TODO : from here, there should be a "validateTransform" method
  # that is called from here and and validateOptions, with the 
  # same conditions
  if giWhich == 0 : 
    lbOK = False
    print "ERROR : -n must be set on transform file"
  if giSegment > 0 :
    if giWhich == 0 :
      lbOK = False
      print "ERROR : if option -s is set, -n must be set too"
  if gDurationNew == None and gDTnew == None :
    lbOK = False
    print "ERROR : -T and/or -D must be set on transform file"
  return lbOK


def validateOptions() :
  global giAction # is set here? TODO : check if == 0
  global gsXformFile
  global giWhich, giSegment
  global gDurationNew, gDTnew
  global gbDispWaypts, gbDispTracks, gbDispRoutes

  lbOK = True
  if not gsXformFile == None :
    giAction = 2 # transform XML
    giAction += 4 # transform XML with file (2 + 4 = bits 1 and 2)
    if giWhich == 0 and giSegment == 0 and gDurationNew == None and gDTnew == None :
      if gsOutput == None :
        lbOK = False
        print "ERROR : if option -X is set, -o must be set too"
    else :
      lbOK = False
      print "ERROR : if option -X is set, -n, -s, -T and -D must NOT be set"
    # TODO : check display options => ERROR
  else :
    # display options?
    if gbDispWaypts == True or gbDispTracks == True or gbDispRoutes == True :
      giAction = 1 # display
      if not ( gDurationNew == None and gDTnew == None ) :
        lbOK = False
        print "ERROR : if option -d, -D and -T must NOT be set"

    # transformation options?
    # no need to check if -d is set, this is done above
    elif not ( gDurationNew == None and gDTnew == None ) :
      giAction = 2 # transform XML
      if gsOutput == None :
        lbOK = False
        print "ERROR : if option -D or -T is set, -o must be set too"
      # this is not an error
      """
      if not gDurationNew == None :
        if gDTnew == None :
          lbOK = False
      """
      if giWhich == 0 : 
        lbOK = False
        print "ERROR : if option -T or -D is set, -n must be set too"

    else :
      if not gsOutput == None :
        lbOK = False
        print "ERROR : if option -o is set, other options must be set too"

      lbOK = False
      print "ERROR : must have at least a -d or -D/-T option"

    # aixo sempre es mira
    if giSegment > 0 :
      if giWhich == 0 :
        lbOK = False
        print "ERROR : if option -s is set, -n must be set too"

  return lbOK


def dispPoint( pPoint ) :
  print "Point at ({0},{1}) -> {2}".format( pPoint.latitude, pPoint.longitude, pPoint.elevation )
  print "-- timestamp:%s:" % pPoint.time


def resetTrackTime() :
  global gXmlGPX
  global gDTnew
  global gDurationNew
  global giSegment
  global giWhich
  global gDTnew

  lbOK = True
  lDurationNew = None
  lTimeIni = None
  lTimeEnd = None
  lbProcessed = False
  liTrack = 0
  for lTrack in gXmlGPX.tracks :
    lbDontTouch = False
    liTrack += 1
    print "track #%d ..." % liTrack
    if giWhich > 0 :
      print "giWhich = %d" % giWhich
      if not liTrack == giWhich :
        print "track #%d, dont touch anything ..." % liTrack
        lbDontTouch = True
      else :
        if not gDurationNew == None :
          lDurationNew = gDurationNew
          print "will adjust track time to fit into a %s duration" % ( str( gDurationNew ) )
        else :
          print "track time will just be shifted (duration won't be changed)"

    print "============="
    print "track #%d name:%s:" % ( liTrack, lTrack.name )
    liSegment = 0
    for lSegment in lTrack.segments :
      lbDontTouch = False
      liSegment += 1
      print "--"
      print "segment #%d ..." % liSegment
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
      for lPoint in lSegment.points :
       if lbDontTouch == False :
        lbProcessed = True
        if lTimeIni == None :
          print "lTimeIni == None ..."
          lDT = lPoint.time
          print lDT
          if gDTnew == None :
            # FIXME this is ugly ...
            lTdiff = gTdiffZero
            print "NO initial time diff"
            #print lTdiff.__class__
            if not lTimeEnd == None :
              lDTnew = lTimeEnd
              print "initial time diff as end time last segment: %s" % ( lDTnew )
            else :
              lDTnew = lDT
              print "initial time diff as in original: %s" % ( lDTnew )
            lTimeIni = lDTnew
          else :
            lTdiff = gDTnew - lDT
            print "=>", gDTnew
            print "time diff:", lTdiff
            lDTnew = lDT + lTdiff
            print "new initial time:", lDTnew
            lTimeIni = lDTnew
        if gbVerbose == True :
          dispPoint( lPoint )
        print "=>"
        #lPoint2 = gpx.GPXTrackPoint()
        if lDurationNew == None :
          lPoint.time += lTdiff
        else :
          """
          if gDTnew == None :
            print "NONE gDTnew"
            lPoint.time = lTimeIni
          """
          lPoint.time = lDTnew
          #print "lDTaccu", lDTaccu
          lPoint.time += lDTaccu
          lDTaccu += lTDpoint
          print "lDTaccu:", lDTaccu
        dispPoint( lPoint )
       else : # if lbDontTouch == False :
        dispPoint( lPoint )
       lTimeEnd = lPoint.time
       print "----"
      print "end of segment #%d, lTrack #%d" % ( liSegment, liTrack )
      print "----"
    print "end of track #%d" % ( liTrack )
    print "--------"

  if lbProcessed == True :
    print "transform finished, processing done"
  else :
    print "transform finished, NO processing done"
    lbOK = False
  print "--------"
  print ""

  return lbOK


def writeOutput() :
  global gsOutput
  global gXmlGPX

  lbOK = True
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
  for lTrack in gXmlGPX.tracks :
    liPoints = 0
    lTimeIni = None
    lTimeEnd = None
    lTrackTdiff = gTdiffZero
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
    for lSegment in lTrack.segments :
      lTimeSegIni = None
      lTimeSegEnd = None
      liSegment += 1
      print "segment #%d ..." % liSegment
      print "--"
      global giSegment
      if giSegment > 0 :
        print "giSegment = %d" % giSegment
        if not liSegment == giSegment :
          print "skip segment #%d" % liSegment
          continue
      liSegPoints = len( lSegment.points )
      liPoints += liSegPoints
      print "segment #%d, track #%d => %d points" % ( liSegment, liTrack, liSegPoints )
      for lPoint in lSegment.points :
        if lTimeSegIni == None :
          lTimeSegIni = lPoint.time
          if lTimeIni == None :
            lTimeIni = lTimeSegIni
          print "lTimeSegIni =", lTimeSegIni
        if gbVerbose == True :
          dispPoint( lPoint )
        lTimeSegEnd = lPoint.time
        lTimeEnd = lTimeSegEnd
      if lTimeSegEnd == None or lTimeSegIni == None :
        print "no time lapse for segment %d, track #%d" % ( liSegment, liTrack )
        lSegTdiff = gTdiffZero
      else :
        lSegTdiff = lTimeSegEnd - lTimeSegIni
        print "start time: %s - end time: %s (segment)" % ( str( lTimeSegIni ), str( lTimeSegEnd ) )
        print "time lapse: %s (segment %d, track #%d)" % ( str( lSegTdiff ), liSegment, liTrack )
      lTrackTdiff += lSegTdiff

      print "end of segment #%d, lTrack #%d" % ( liSegment, liTrack )
      print "----"
    print "end of track #%d" % ( liTrack )
    print "total points = %d" % ( liPoints )
    if lTimeEnd == None or lTimeIni == None :
      print "no time lapse for track #%d" % ( liTrack )
    else :
      print "start time: %s - end time: %s" % ( str( lTimeIni ), str( lTimeEnd ) )
      print "diff time lapse (IniToEnd): %s (track #%d)" % ( str( lTimeEnd - lTimeIni ), liTrack )
      print "accu time lapse (segments): %s (track #%d)" % ( str( lTrackTdiff ), liTrack )
    print "--------"
    print ""


def dispWaypts() :
  liWaypt = 0
  for lWaypoint in gXmlGPX.waypoints :
    liWaypt += 1
    print "============="
    print "waypoint #%d" % ( liWaypt )
    print "waypoint {0} -> ({1},{2})".format( lWaypoint.name, lWaypoint.latitude, lWaypoint.longitude )
    print "-- comment:", lWaypoint.comment
    print "-- description:", lWaypoint.description
    print "-- symbol:", lWaypoint.symbol


def dispRoutes() :
  liRoute = 0
  for lRoute in gXmlGPX.routes :
    liRoute += 1
    print "============="
    print "Route: #%d" % ( liRoute )
    liPoints = lRoute.points
    for lPoint in lRoute.points :
      if gbVerbose == True :
        dispPoint( lPoint )
    print "end of route #%d" % ( liRoute )
    print "total points = %d" % ( liPoints )
    print "--------"
    print ""


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


def unsplitOptParams( pss ) :

  print "-------------------"
  print "unsplitOptParams"
  lssRet = []
  print pss
  if pss[ 0 ].startswith( "-" ) :
    i = 0
    liRemaining = len( pss[ i : ] )
    while liRemaining > 0 and pss[ i ].startswith( "-" ) :
      print "i=%d, pss[ %d ]:%s: remaining=%d" % ( i, i, pss[ i ], liRemaining )
      if len( pss[ i : ] ) > 1 :
        lss = ""
        liJoined = 1
        for ls in pss[ i + liJoined : ] :
          print "ls:%s: joined=%d" % ( ls, liJoined )
          if ls.startswith( "-" ) :
            print "break"
            liJoined -= 1
            break
          lss += " " + ls
          liJoined += 1
          print "lss:%s: joined=%d" % ( lss, liJoined )
        lssU = [ pss[ i ], lss[ 1 : ] ]
        print "lss:%s: => lssU:%s:" % ( lss, lssU )
        lssRet.extend( lssU )
      # if len ...
      i += 1 + liJoined
      liRemaining = len( pss[ i : ] )
      print "=> i=%d, remaining=%d" % ( i, liRemaining )
      print "----"
    # while loop
    print "leaving while, i=%d" % ( i )
  else :
    print "FATAL!"
  print lssRet
  print "unsplitOptParams OK"
  print "-------------------"
  return lssRet


def readXformFile( psXformFile ) :
  """
  psXformFile : input, the file name (string)
  lListXforms : output, the transform commands list (None if error)
  """
  lListXforms = None
  lbOK = True
  try :
    lFile = open( psXformFile, "r" )
  except :
    eprint( "FATAL: could not open file %s, quitting ..." % ( gsFileGPX ) )
    return lListXforms

  print "checking lines in command file %s ..." % ( psXformFile )
  liLine = 0
  lList = []
  for ls in lFile.readlines() :
    liLine += 1
    if not ls.startswith( "#" ) :
      lss = ls.split()
      print "line #%d split: %s" % ( liLine, lss )
      # TODO : check if some option "-?" has more than 2 params => join with blank
      if len( lss ) > 0 :
        cleanXformOpts()
        lss2 = unsplitOptParams( lss )
        #checkOptions( lss2 ) # this may exit!
        #if validateOptionsXform() == False :
        #  print "line #%d validation on file %s failed" % ( liLine, psXformFile )
        #  lbOK = False
        #  #break
        #else :
        #  lList.append( lss )
        #  #print lList
    else :
      print "# ..."
    print "--"
  lFile.close()
  if lbOK == True :
    print "successful command file reading"
    lListXforms = lList
  else :
    print "ERROR, command file reading failed"

  # TODO debug, remove
  sys.exit( 0 )
  # TODO debug, remove

  return lListXforms


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

giAction = 0 # default, no action
gbVerbose = False
gbDispTracks = False
gbDispWaypts = False
gbDispRoutes = False
giWhich = 0
giSegment = 0

gsXformFile = None
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
  if not gsXformFile == None :
    lsXformFile = gsXformFile # backup
    gsXformFile = None
    lsOutput = gsOutput # backup
    gsOutput = None
    gListXforms = readXformFile( lsXformFile )
    if gListXforms == None :
      sys.exit( 1 )
    gsXformFile = lsXformFile # restore
    gsOutput = lsOutput # restore

gFileGPX = setOpenFile( gsFileGPX )
if gFileGPX == None :
  sys.exit( 1 )

gXmlGPX = parseGpxFile( gFileGPX )
if gXmlGPX == None :
  sys.exit( 1 )

if not giAction == 1 : # transform, NO display?
  print "transform GPX data ..."
  if not gsXformFile == None :
    liXform = 0
    for lXforms in gListXforms :
      liXform += 1
      print "process transform #%d ..." % ( liXform )
      cleanXformOpts()
      checkOptions( lXforms ) # NO errors now, no need to validate
      lbOK = resetTrackTime()
      print "transform #%d result=%s" % ( liXform, str( lbOK ) )
      print "----"
      if lbOK == False :
        print "WARNING : transform #%d did NOT do anything" % ( liXform )
        #break
  else :
    # uses cmd-line options set
    lbOK = resetTrackTime()
    print "transform result=%s" % ( str( lbOK ) )

  # only 1 shared write
  lbOK = writeOutput()
  if lbOK == False :
    print "ERROR, could not write XML to %s" % ( gsOutput )
  else :
    print "XML written into to %s OK!" % ( gsOutput )

else : # display

  display()

print ""
print "======"
print "DONE"
print "======"

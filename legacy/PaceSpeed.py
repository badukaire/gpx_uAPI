"""
Calculates speed (m/s, km/h) and pace (mins/km) for a given set of
time and distance pairs, i.e. from a running session.

Reads from a file (or from stdin) lines with sets of time (min'sec'')
and distance (kms), which are expected to be in a format like this:

+8'39''    +1.88
+3'20''     2.51
+9'28''     4.32 HALF

# this is half session

+9'46''     6.23
+3'24''     6.89
43'41''     8.57

Both time and distance can be absolute or relative to the previous line, in
such case this is indicated with a '+' just before the figure. Absolute is
meant to be split times, and relative is like laps.

Empty lines and lines starting with '#' (comments) are also possible.

It is also possible to add tags to each time, to indicate special points. 
Then the output will also include a section detailing split time/pace
between these points (including start and end points).

It can also parse a time and distance directly from parameters.

Usage examples :

$ python PaceSpeed.py f.txt
$ cat f.txt | python PaceSpeed.py
$ python PaceSpeed.py "3'34''" 0.89 # notice use of ""
$ python PaceSpeed.py 3,34,, 0.89 # commas may also be used

The output displays the speed for each set in m/s, km/h and mins/km (pace).

"""

import sys
import string

class PaceSpeed :

  def __init__( self, psInputFile = None ) :

    # default values, explicit declarations
    self.mFile = None
    self.miTotalSecs = 0
    self.mfTotalDist = .0
    self.mListTags = []

    if psInputFile == None :
      self.mFile = sys.stdin
    else :
      try :
        lFile = open( psInputFile )
      except :
        print >> sys.stderr, 'invalid file ' + psInputFile
        print >> sys.stderr, 'quitting'
        sys.exit( 1 )

      self.mFile = lFile


  def parseFile( self ) :

    liLine = 0
    for lsLraw in self.mFile :
      liLine += 1
      if lsLraw[ 0 ] == '#' :
        continue
      if len( lsLraw ) < 3 :
        continue

      liRet = self.parse( lsLraw )
      if liRet == None : continue # where? not necessary


  def parse( self, psLraw ) :

    try :
      lss = psLraw.split()
      lsTime = lss[ 0 ]
      lsDist = lss[ 1 ]
      if len( lss ) > 2 :
        lsTagp = lss[ 2 ]
        lsTagText = '  *** tag: ' + lsTagp
      else :
        lsTagText = ''
    except :
      print >> sys.stderr, 'syntax error in line', liLine
      return 9
    print 'time:%s: dist:%s:%s' % ( lsTime, lsDist, lsTagText )

    lRet, lbRel = PaceSpeed.parseTime( lsTime )
    if lRet == None : return lRet
    self.useTime( lRet, lbRel )

    lRet, lbRel = PaceSpeed.parseDist( lsDist )
    if lRet == None : return lRet
    self.useDist( lRet, lbRel )

    PaceSpeed.display( self.miIncrSecs, self.mfIncrDist )

    if not lsTagText == '' :
      self.mListTags.append( ( self.miTotalSecs, self.mfTotalDist, lsTagp ) )


  @staticmethod
  def parseTime( sTime ) :

    try :
      if sTime[ -1 ] == ',' :
        lss = sTime.split( ',' )
      else :
        lss = sTime.split( '\'' )
      lsMin = lss[ 0 ]
      lsSec = lss[ 1 ]
    except :
      print >> sys.stderr, 'syntax error parsing mins/secs :', sTime
      return None, None
    lbRelTime = False
    liPos = 0
    if lsMin[ 0 ] == '+' :
      liPos = 1
      lbRelTime = True
    try :
      liMin = int( lsMin[ liPos : ] )
    except :
      print >> sys.stderr, 'syntax error parsing mins :', lsMin
      return None, None
    try :
      liSec = int( lsSec )
    except :
      print >> sys.stderr, 'syntax error parsing secs :', lsSec
      return None, None
    liSecs = liMin * 60 + liSec
    return liSecs, lbRelTime


  def useTime( self, liSecs, lbRelTime ) :

    if lbRelTime == True :
      self.miTotalSecs += liSecs
      self.miIncrSecs = liSecs
      lsAdd = '(+)'
    else :
      liTotalSecs0 = self.miTotalSecs
      self.miTotalSecs = liSecs
      self.miIncrSecs = self.miTotalSecs - liTotalSecs0
      lsAdd = '***'

    PaceSpeed.displayTotalTime( liSecs, self.miIncrSecs, lsAdd, self.miTotalSecs )



  @staticmethod
  def secs2hms( piSecs ) :
    liS = piSecs
    liH = liS / 3600
    liS -= liH * 3600
    liM = liS / 60
    liS -= liM * 60
    return liH, liM, liS

  @staticmethod
  def displayTime( piSecs ) :
    liH, liM, liS = PaceSpeed.secs2hms( piSecs )
    print 'time: %4ds (%dh%02d\'%02d\'\')' % ( piSecs, liH, liM, liS )

  @staticmethod
  def displayTotalTime( piSecs, piIncrSecs, psAdd, piTotalSecs ) :
    liHi, liMi, liSi = PaceSpeed.secs2hms( piIncrSecs )
    liH, liM, liS = PaceSpeed.secs2hms( piTotalSecs )
    print 'time: %4ds  %s +%4ds (+%dh%02d\'%02d\'\') => total = %4ds (%dh%02d\'%02d\'\')' % ( piSecs, psAdd, piIncrSecs, liHi, liMi, liSi, piTotalSecs, liH, liM, liS )


  @staticmethod
  def parseDist( sDist ) :

    lbRelDist = False
    liPos = 0
    if sDist[ 0 ] == '+' :
      liPos = 1
      lbRelDist = True
    try :
      lfDist = float( sDist[ liPos : ] )
    except :
      print >> sys.stderr, 'syntax error parsing distance :', sDist
      return None, None
    return lfDist, lbRelDist


  def useDist( self, lfDist, lbRelDist ) :

    if lbRelDist == True :
      self.mfTotalDist += lfDist
      self.mfIncrDist = lfDist
      lsAdd = '(+)'
    else :
      lfTotalDist0 = self.mfTotalDist
      self.mfTotalDist = lfDist
      self.mfIncrDist = self.mfTotalDist - lfTotalDist0
      lsAdd = '***'

    PaceSpeed.displayTotalDist( lfDist, self.mfIncrDist, lsAdd, self.mfTotalDist )


  @staticmethod
  def displayDist( pfDist ) :
    print 'dist: %.2fkm' % ( pfDist )

  @staticmethod
  def displayTotalDist( pfDist, pfIncrDist, psAdd, pfTotalDist ) :
    print 'dist: %.2fkm %s +%.2fkm             => total = %.2fkm' % ( pfDist, psAdd, pfIncrDist, pfTotalDist )


  @staticmethod
  def display( piIncrSecs, pfIncrDist  ) :

    try :
      lfSpeed = ( 1000 * pfIncrDist ) / piIncrSecs
      lfMinkm = piIncrSecs / pfIncrDist / 60
      liMinkm = int( lfMinkm )
      lfX = lfMinkm - liMinkm
      liSecKm = lfX * 60
      print 'speed: %.2fm/s %.2fkm/h' % ( lfSpeed, lfSpeed * 3.6 ) ,
      print '- pace: %2d\'%02d\'\'/km (%.2f\'/km)' % ( liMinkm, liSecKm, lfMinkm )

    except ZeroDivisionError :
      print 'could not calculate speed / minsxkm (div by zero)'
    print '--'


  def dumpTags( self ) :

    lsLastTagName = 'start'
    liLastTime = 0
    lfLastDist = .0
    print '===='
    print 'TAGS:'
    if len( self.mListTags ) == 0 :
      print '(none)'
      return

    for lTag in self.mListTags :
      liTagTime = lTag[ 0 ]
      lfTagDist = lTag[ 1 ]
      lsTagName = lTag[ 2 ]

      liTimeDiff = liTagTime - liLastTime
      lfDistDiff = lfTagDist - lfLastDist
      print 'TAG : %s - %s' % ( lsLastTagName, lsTagName )
      PaceSpeed.displayTime( liTimeDiff )
      PaceSpeed.displayDist( lfDistDiff )
      PaceSpeed.display( liTimeDiff, lfDistDiff )

      liLastTime = liTagTime
      lfLastDist = lfTagDist
      lsLastTagName = lsTagName

    liTimeDiff = self.miTotalSecs - liLastTime
    lfDistDiff = self.mfTotalDist - lfLastDist
    print 'TAG : %s - %s' % ( lsLastTagName, 'end' )
    PaceSpeed.displayTime( liTimeDiff )
    PaceSpeed.displayDist( lfDistDiff )
    PaceSpeed.display( liTimeDiff, lfDistDiff )


  def dump( self ) :
    
    self.dumpTags()

    print '===='
    print 'TOTAL:'
    PaceSpeed.displayTime( self.miTotalSecs )
    PaceSpeed.displayDist( self.mfTotalDist )
    PaceSpeed.display( self.miTotalSecs, self.mfTotalDist )

    self.mFile.close()


if __name__ == "__main__" :

  liArgc = len( sys.argv )
  # only 1 distance
  if liArgc > 2 :

    liSecs, lbRel = PaceSpeed.parseTime( sys.argv[ 1 ] )
    if liSecs == None : sys.exit( 1 )
    lfDist, lbRel = PaceSpeed.parseDist( sys.argv[ 2 ] )
    if lfDist == None : sys.exit( 1 )
  
    PaceSpeed.display( liSecs, lfDist )

  # use a file / stdin
  else :

    if liArgc > 1 :
      # use file
      lPaceSpeed = PaceSpeed( sys.argv[ 1 ] )
    else :
      # use stdin
      lPaceSpeed = PaceSpeed()
    lPaceSpeed.parseFile()
    lPaceSpeed.dump()



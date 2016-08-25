# gpx_uAPI

GPX micro API to display and/or edit GPX files. Written
in python.

It takes as input a GPX file, and with it it can do
basically 2 things:

- **display** info about GPX elements: tracks, segments,
routes and waypoints, as well as the start time and
duration on specific tracks and segments

- **edit** the *start time* and *duration* on specific
tracks and segments

It can not yet display the distance covered of the GPX
elements, for that any other GPX app will do.

Currently the code does not have an API format but a 
*proof-of-concept* format, with scripts.

The code uses [gpxpy](http://github.com/tkrajina/gpxpy)
as its _GPX parsing library_. This library is managed
through the _git submodule_ feature.


## how to use it

The main script is called `gpxX.py`. It takes as input
(what should be) a valid GPX file. Beware since every
GPX app produces a GPX format/dialect of its own, using
more or less XML tags. The output format produced by
the _gpxpy_ library may produce data that may cause
others GPX apps to decline reading or to crash.

This input for the script can be fed to the script either
as standard input or as a file name passed as a command-line
parameter.

The script is self-documented (when called with the _-h_
option). Let's see however some examples on how to use it.


### script usage

For **displaying** the contents of the GPX file, the _-d_ 
option shall be used. This option needs a value to
complement it, that sets what GPX elements to display :
_tracks_, _waypoints_ or _segments_ (concepts defined by
the GPX format).

For **editing** GPX files there is a compulsory option
_-o_, to set the output file name. It is not possible
to send the output to _standard output_ since that is
used for displaying and debugging.

There are other options for editing, to specify **which**
GPX element to edit (*-n* for track, *-s* for segment). And
finally those to specify **what values to set** : the
duration (*-D*) and/or the start time (*-T*).

For complex and multi-option edits, there is the *-X*
option, that allows specifying multiple editions through
a file, that are processed in a single run.


### command format and examples

To simplify and to improve readability, all the following examples do
not specify the input file. As mentioned above, the input data can be
fed through standard input or via a command-line parameter. That would
be like:

* standard input : `cat input.gpx | python -d w`
* command-line parameter : `python -d w input.gpx`

display examples :

```
# display waypoints
python gpxX.py -d w

# display waypoints and tracks
python gpxX.py -d waypoints -d t

# display track #2
python gpxX.py -d tracks -n 2
```

edit examples :

```
# no track/segment specified: first track will have this
# datetime, and next tracks/segments will have time after
# finishing the first track/segment
# -- durations won't be modified
python gpxX.py -T "2016-06-06 12:00:01" -o jun06.gpx

# set start time on track #2
python gpxX.py -n 2 -T "2016-06-06 12:00:01" -o jun06.gpx

# set duration and start time on track #2
python gpxX.py -n 2 \
  -o jun06.gpx \
  -D 2:03:01 -T "2016-06-06 12:00:01"

# set duration and start time on track #2, segment #1
python gpxX.py -n 2 -s 1 -D 2:03:01 \
  -T "2016-06-06 12:00:01" -o jun06.gpx

# use a file with a set of edit commands, probably
# for more than 1 track and segment
python gpxX.py -X setJun06.txt -o jun06.gpx
```

edit with file examples :

When using an edit file, the *-o* option must be provided
in the command line, and not in the file. This way every
line of the file will contain only edit options, i.e. a
combination of (not necessarily all) : *-D*, *-T*, *-n*,
*-s*.

This an example file :

```
-T 2016-08-20 20:00:00 -D 0:33:33 -n 1 -s 1
-T 2016-08-20 20:39:00 -D 0:44:44 -n 1 -s 2
-D 0:33:33 -n 2 -s 1
-D 0:44:44 -n 3 -s 1
```

Please notice that quotes ('"') are necessary when using the
*-T* option on the command line, but these must not be on
the file. This is because *bash* needs them for not separating
them.



## the PaceSpeed script

Included in this API there is a helper tool called *PaceSpeed*. It
is a script (`legacy/PaceSpeed.py`) than can calculate the speed and
pace for a given set of time/distance segments, each one in a file line.
Both time and distance for each segment can be absolute or relative to
the last one.

The script is self-documented (when called with the *-h* option). Its 
input can be read input both from standard input (with a pipe) or from
a file specified as a command-line parameter.

If the user knows the distance between the waypoints of a route, she
does not need to carry a GPS smartphone or buy a GPS watch. With just
a simple chronometer that can record lap times she can know the
speed and pace between waypoints, and also feed them into her GPX
files, using this script or manually.


### input format

The input file format for the `PaceSpeed` script consists of 
lines, each line containing at least 2 columns. Each line represents
a track segment, the columns being the time and length. A third
column can be present, meaning a _human-meaningful tag_ for
that segment.

Everything on a line after a '#' is ignored. Lines without columns
are ignored too. Line with less than 2 columns or with format errors
cause the script to _abort processing_.

The time is specified as minutes and seconds (no hours or millis
are allowed), separated by '\'' or ','. The format is
`[]<mins>'<secs>''` - or `[+]<mins>,<secs>,,` if using commas
instead of aposthophes (this is useful for a command-line
feature not described yet). If a duration is longer than 1
hour, add 60 to the minutes as many times as necessary, i.e.
3h20' => use 200'. Seconds can not be larger than 60.

The distance is specified as kilometers, with decimals. It is 
recommended to use 2 or 3 decimals.

The output units are km/h and m/s for speed. The pace is
given in time per kilometer, where time is given in both
minutes-seconds and minutes with decimals.

Notice there is an optional *plus* ('+') sign at the beginning
of the figures. This means that the time or distance is relative
respect of the last point. That is, it refers only to this
segment. Without the *plus* sign, the time or distance are
absolute, therefore respect to the start of the track.


### input file example

This is an example input file for the `PaceSpeed` script.

```
# route: W1
# type: running
# date: 2015-10-14

+08'41''  +1.88
+04'05''   2.51
+10'18''   4.32  HALF
# half session, 23'04''

+10'48''   6.23
+04'03''   6.89
 47'11''   8.57

# total time was 47'11''
```

Presumably, it is quite self-comprehensible. Notice that
some of the figures start with a plus sign and some
others don't. These can be combined as required, depending
on whether there is a relative or absolute reference
available.

Notice too that the script is tolerant to lines with
contents starting with a blank. This way it is possible
to have the columns perfectly aligned in case there is
a combination of absolute and relative times, allowing
for a good readability.

This other input file is absolutely identical, but in this
case some plus signs have been removed or added. Running
the script on either example yields the same result.


```
# route: W1
# type: running
# date: 2015-10-14

+08'41''   1.88
+04'05''  +0.63
 23'04''   4.32  HALF
# half session, 23'04''

+10'48''  +1.91
+04'03''  +0.66
 47'11''   8.57

# total time was 47'11''
```

That is the output, providing the distance, time, speed and
pace for every segment, in absolute (from the beginning) and
relative reference. And also for the defined tags, in this
case _HALF_ meaning half the circuit.

```
time:+08'41'': dist:1.88:
time:  521s  (+) + 521s (+0h08'41'') => total =  521s (0h08'41'')
dist: 1.88km *** +1.88km             => total = 1.88km
speed: 3.61m/s 12.99km/h - pace:  4'37''/km (4.62'/km)
--
time:+04'05'': dist:+0.63:
time:  245s  (+) + 245s (+0h04'05'') => total =  766s (0h12'46'')
dist: 0.63km (+) +0.63km             => total = 2.51km
speed: 2.57m/s 9.26km/h - pace:  6'28''/km (6.48'/km)
--
time:23'04'': dist:4.32:  *** tag: HALF
time: 1384s  *** + 618s (+0h10'18'') => total = 1384s (0h23'04'')
dist: 4.32km *** +1.81km             => total = 4.32km
speed: 2.93m/s 10.54km/h - pace:  5'41''/km (5.69'/km)
--
time:+10'48'': dist:6.23:
time:  648s  (+) + 648s (+0h10'48'') => total = 2032s (0h33'52'')
dist: 6.23km *** +1.91km             => total = 6.23km
speed: 2.95m/s 10.61km/h - pace:  5'39''/km (5.65'/km)
--
time:+04'03'': dist:+0.66:
time:  243s  (+) + 243s (+0h04'03'') => total = 2275s (0h37'55'')
dist: 0.66km (+) +0.66km             => total = 6.89km
speed: 2.72m/s 9.78km/h - pace:  6'08''/km (6.14'/km)
--
time:47'11'': dist:8.57:
time: 2831s  *** + 556s (+0h09'16'') => total = 2831s (0h47'11'')
dist: 8.57km *** +1.68km             => total = 8.57km
speed: 3.02m/s 10.88km/h - pace:  5'30''/km (5.52'/km)
--
====
TAGS:
TAG : start - HALF
time: 1384s (0h23'04'')
dist: 4.32km
speed: 3.12m/s 11.24km/h - pace:  5'20''/km (5.34'/km)
--
TAG : HALF - end
time: 1447s (0h24'07'')
dist: 4.25km
speed: 2.94m/s 10.57km/h - pace:  5'40''/km (5.67'/km)
--
====
TOTAL:
time: 2831s (0h47'11'')
dist: 8.57km
speed: 3.03m/s 10.90km/h - pace:  5'30''/km (5.51'/km)
--
```


### command-line syntax

The script accepts only one command-line option, *-h* as
said before. But it can also accept some parameters in a
subtle way.

If there is 1 parameter, it is taken as the input file
name as seen before.

If there are 2 parameters, the 1st one is taken as the
time, and the 2nd as the distance. With them a pace/speed
calculation, is performed. The format is the same as in
a file, but here it may be convenient to use commas 
instead of apostrophes to avoid the shell interpreting
them as quotes and having to use escape sequences 
like '\\'.

Example (notice the use of commas) :

```
marc@ibm:~/git/github/gpx_uAPI$ python legacy/PaceSpeed.py +10,48,, 6.23
speed: 9.61m/s 34.61km/h - pace:  1'44''/km (1.73'/km)
--
marc@ibm:~/git/github/gpx_uAPI$ 
```


## URLs

The URLs of the repos where this project is stored are:

- github : the actual working repo, at <https://github.com/badukaire/gpx_uAPI.git>
- subversion : the legacy folder is sync'ed in the _svn_ branch, stored at <https://svn.geekisp.com/marc3/gps/timer>.


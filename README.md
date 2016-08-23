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
instead of aposthophes. If a duration is longer than an hour, add
60 to the minutes as necessary, i.e. 3h20' => 200'. Seconds can not
be larger than 60.

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

# this is half session

+10'48''   6.23
+04'03''   6.89
47'25''    8.57

# total marca 47'43'' => 47'25''
```

It is presumably quite self-comprehensible.




## URLs

The URLs of the repos where this project is stored are:

- github : the actual working repo, at <https://github.com/badukaire/gpx_uAPI.git>
- subversion : the legacy folder is sync'ed in the _svn_ branch, stored at <https://svn.geekisp.com/marc3/gps/timer>.


This is a simple interval timer that I wrote for use while practicing
a [pecha kucha][] presentation.

I use this in combination with [xdotool][] to advance the slides of my
presentation every 20 seconds, like this:

    pktimer -s 20 -r 20 \
      -a 'xdotool  search --name Slides key Right'

I found it very useful to have a visual timer on the same screen as my
slides.

[pecha kucha]: http://www.pechakucha.org/
[xdotool]: https://github.com/jordansissel/xdotool

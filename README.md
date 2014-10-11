My most stupid scripts.

# emojiart

Create emoji art (as in ascii art).

    Usage:
        emojiart.py [-s=<sc>] [-f=<fs>] <path_to_image>

    Options:
        -h --help                       Show this screen
        -s=<sc> --scale=<sc>            Resize image by this value before conversion [default: 1.0]
        -f=<fs> --height_to_width=<fs>  Rescale width by this value to match fonts height to width proportion [default: 1.8]

![Emoji art example](http://procrastinationlog.net/images/github/emojiart.png)

# asciiart

Create ascii art.

    Usage:
        asciiart.py [-s=<sc>] [-f=<fs>] [-c=<na>] [-b]<path_to_image>

    Options:
        -h --help                       Show this screen
        -s=<sc> --scale=<sc>            Resize image by this value before conversion [default: 1.0]
        -f=<fs> --height_to_width=<fs>  Rescale width by this value to match fonts height to width proportion [default: 1.8]
        -c=<na> --symbols_set=<na>      Name of symbols set to use, possible values: small_stars, block3, block2, stars, big_ascii, small_ascii, arrows, block, math [default: small_ascii]
        -b --black_on_white             Reverse symbols set


![Ascii art example](http://procrastinationlog.net/images/github/asciiart.png)

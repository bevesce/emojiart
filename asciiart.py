# -*- coding: utf-8 -*-
from PIL import Image
import random
from bisect import bisect
import docopt

# contains lists of symbols that can be used to create ascii art
# list should contain symbols from the the lightes to the darkest one
# if some level contains more than one symbol one is choosen at random
symbols_sets = {
    'block': (u' ', u'░', u'▒', u'▓', u'█'),
    'block2': (u' ', u'▏', u'▎', u'▍', u'▌', u'▋', u'▊', u'▉'),
    'block3': (u' ', u'▏', u'░', u'▎', u'▍', u'▌', u'▓', u'▋', u'▊', u'▓', u'▉'),
    'small_ascii': (u' ', u'.', u'v', u't', u'K', u'W', u'#'),
    'math': (u' ', u'.', u'-', u'_', u'+', u'*', u'%'),
    'stars': (u' ', u'✧', u'☆', u'✦', u'★', u'✵', u'✹'),
    'small_stars': (u' ', u'☆', u'★'),
    'arrows': (
        u' ',
        u'˯˰˱˲',
        u'←↑→↓',
        u'⤡⤢⤣⤤⤥⤦',
        u'⤧⤨⤩⤪⤭⤮⤯⤰⤱⤲',
        u'⇹⇺⇻⇼',
        u'⬅⬆⬇',
    ),
    'big_ascii': (
        u' ',
        u'.,-',
        u'_ivc=!/|~;',
        u'gjez2]/(YL)t[+T7Vf',
        u'K4ZGbNDXY5PQ',
        u'W8KMA',
        u'#%$',
        u'@',
    ),
}

__doc__ = u"""
Create ascii art.

              ▒▒▒▓▓▓▓▓▓▓▒▒▒
           ▒▒▓▓▓██████████▓▓▒▒
         ▒▒▓▓███████████████▓▓▓▒
        ▒▓▓███████████████████▓▓▒▒
       ▒▒▓█████████████████████▓▓▒
       ▒▓▓█████▓▒▒▓███▓▒░▒█████▓▓▓
      ▒▓▓▓████▓▒▒░▒▓▓▓▒░▒▒▓████▓▓▓▒
      ▒▓▓▓▓▓▓▓▓▒▓▓▒▓▓▓▒▓█▓▓▓▓▓▓▓▓▓▒
      ▒▓▓▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓▓▒
      ░▒▓▓▓▒░░░░░░░▒▒░░░░░░░░▒▓▓▓▓░
       ▒▓▓▓▓░▒▓███████████▓▒▒▓▓▓▓▓
        ▒▓▓█▓▒▒░░░░░░░░░░░▒▒▓█▓▓▓▒
         ▒▓▓██▓▒▒▒▒▒▒▒▒▒▒▒▓██▓▓▒░
          ░▒▓▓▓██▓▒▒▒▒▓▓▓█▓▓▓▒░
             ░▒▓▓▓▓██▓▓▓▓▓▒░
                 ░░▒▒▒░░

Usage:
    asciiart.py [-s=<sc>] [-f=<fs>] [-c=<na>] [-b]<path_to_image>

Options:
    -h --help                       Show this screen
    -s=<sc> --scale=<sc>            Resize image by this value before conversion [default: 1.0]
    -f=<fs> --height_to_width=<fs>  Rescale width by this value to match fonts height to width proportion [default: 1.8]
    -c=<na> --symbols_set=<na>      Name of symbols set to use, possible values: {} [default: small_ascii]
    -b --black_on_white             Reverse symbols set
""".format(', '.join(symbols_sets.keys()))


def print_art(filename,
              scale=1.0, height_to_width=1.8,
              symbols_set_name='big_ascii', black_on_white=False):
    MAX_VAL = 255
    symbols_set = symbols_sets[symbols_set_name]
    if not black_on_white:
        symbols_set = symbols_set[::-1]
    no_zones = len(symbols_set)
    zone_size = MAX_VAL / no_zones
    zonebounds = [i * zone_size for i in range(1, no_zones)]

    im = Image.open(filename)
    width, height = im.size
    width, height = int(width * height_to_width * scale), int(height * scale)
    im = im.resize((width, height))
    im = im.convert("L")

    ascii_art = []
    for y in range(0, height):
        ascii_art.append([])
        for x in range(0, width):
            lum = MAX_VAL - im.getpixel((x, y))
            matching_zone_index = bisect(zonebounds, lum)
            possibles = symbols_set[matching_zone_index]
            ascii_art[-1].append(possibles[random.randint(0, len(possibles) - 1)])

    print u'\n'.join([''.join(l) for l in ascii_art]).encode('utf-8')


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    print_art(
        arguments['<path_to_image>'],
        scale=float(arguments['--scale']),
        height_to_width=float(arguments['--height_to_width']),
        symbols_set_name=arguments['--symbols_set'],
        black_on_white=arguments['--black_on_white']
    )

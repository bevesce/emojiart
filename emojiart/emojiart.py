# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
from bisect import bisect
import random
import docopt
import math
import pickle
from collections import OrderedDict
import scipy.spatial.kdtree as kd

from edges import find_edges
from pixelmatrix import PixelMatrix
from resources.emojis import emojis


class AsciiArt(object):
    MAX_PIXEL = 255

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

    def __init__(
        self, image,
        width=None,
        scale=1.0, height_to_width=1.8,
        symbols_set_name='big_ascii', black_on_white=False,
        **kwargs
    ):
        self._prepare_image(image, width, scale, height_to_width)
        self._prepare_symbols_set(symbols_set_name, black_on_white)
        self._prepare_ascii_art()

    def _prepare_image(self, image, width=None, scale=1.0, height_to_width=1.8):
        self.orginal_image = image
        self._scale_image(image, width, scale, height_to_width)
        self._image = self._image.convert("L")
        self._pixel_matrix = PixelMatrix.from_image(self._image)

    def _scale_image(self, image, width, scale, height_to_width):
        iwidth, iheight = image.size
        if width:
            height = int(width / (iwidth + 0.) * iheight / height_to_width)
        else:
            self.scale = scale
            self.height_to_width = height_to_width
            width, height = int(iwidth * height_to_width * scale), int(iheight * scale)
        self._image = image.resize((width, height))

    def _prepare_symbols_set(self, set_name, black_on_white=False):
        self.symbols_set_name = set_name
        self.black_on_white = black_on_white

        symbols_set = self.symbols_sets[set_name]
        if not black_on_white:
            symbols_set = symbols_set[::-1]
        self._symbols_set = symbols_set
        self._prepare_zones(symbols_set)

    def _prepare_zones(self, symbols_set):
        no_zones = len(symbols_set)
        zone_size = self.MAX_PIXEL / no_zones
        self._zonebounds = [i * zone_size for i in range(1, no_zones)]

    def _prepare_ascii_art(self):
        self._ascii_art_matrix = self._pixel_matrix.map(self.pixel_to_ascii)

    def pixel_to_ascii(self, pixel, *args):
        return self.change_pixel_to_symbol(pixel)

    def change_pixel_to_symbol(self, pixel):
        lum = self.MAX_PIXEL - pixel
        matching_zone_index = bisect(self._zonebounds, lum)
        possibles = self._symbols_set[matching_zone_index]
        return possibles[random.randint(0, len(possibles) - 1)]

    def __str__(self):
        return str(self._ascii_art_matrix)


class EdgeAsciiArt(AsciiArt):
    def __init__(
        self, image,
        width=None,
        scale=1.0, height_to_width=1.8,
        symbols_set_name='big_ascii', black_on_white=False,
        gauss_blur=2,
        **kwargs
    ):
        self._prepare_image(image, width, scale, height_to_width, gauss_blur)
        self._prepare_ascii_art()

    def _prepare_image(self, image, width, scale, height_to_width, gauss_blur):
        self._scale_image(image, width, scale, height_to_width)
        self._image = self._image.convert("L")
        self._edges_matrix = find_edges(self._image, gauss_blur)

    def _prepare_ascii_art(self):
        self._ascii_art_matrix = self._edges_matrix.map(self.pixel_to_ascii)

    def pixel_to_ascii(self, pixel, *args):
        value, angle = pixel
        if value > 0:
            return ' '
        else:
            return self.angle_to_symbol(angle)

    def angle_to_symbol(self, angle):
        angle = abs(angle)
        pi8 = math.pi / 8.0
        if angle < pi8:
            return '|'
        elif angle < 3 * pi8:
            return '/'
        elif angle < 5 * pi8:
            return '-'
        elif angle < 7 * pi8:
            return '\\'
        return '|'


class FillAsciiArt(EdgeAsciiArt):
    def __init__(
        self, image,
        width=None,
        scale=1.0, height_to_width=1.8,
        symbols_set_name='big_ascii', black_on_white=False,
        gauss_blur=2,
        **kwargs
    ):
        self._prepare_image(image, width, scale, height_to_width, gauss_blur)
        self._prepare_symbols_set(symbols_set_name, black_on_white)
        self._prepare_ascii_art()

    def _prepare_ascii_art(self):
        self._pixel_matrix = PixelMatrix.from_image(self._image)
        self._ascii_art_matrix = self._edges_matrix.map(self.pixel_to_ascii)
        self._ascii_art_matrix = self._ascii_art_matrix.map(self.join_two)

    def join_two(self, v, d, x, y):
        if v != ' ':
            return v
        return self.change_pixel_to_symbol(
            self._pixel_matrix[x, y]
        )


class AvgColor(object):
        BIG_NUM = 256 * 3

        def __init__(self, channels):
            super(AvgColor, self).__init__()
            self.channels = channels
            self.channels_values = OrderedDict([(c, []) for c in channels])

        def add(self, pixel):
            for channel, channel_value in zip(self.channels, pixel):
                self.channels_values[channel].append(channel_value)

        def calculate(self):
            return [
                sum(v) / len(v) if v else self.BIG_NUM for v in self.channels_values.values()
            ]


class EmojiArt(AsciiArt):
    @staticmethod
    def _load_or_create(filename, create):
        try:
            with open(filename) as f:
                return pickle.load(f)
        except (IOError, EOFError):
            with open(filename, 'w') as f:
                creation = create()
                pickle.dump(creation, f)
                return creation

    @staticmethod
    def _create_emojis_colors_test_image(colors, width, height, filename):
        im = Image.new('RGBA', (width, len(colors) * height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(im)
        for i, color in enumerate(colors):
            color = tuple(color)
            draw.rectangle([0, i * height, width, (i + 1) * height], fill=color)
        # im.show()
        im.save('test_images/' + filename, 'PNG')

    @staticmethod
    def convert_emojis_to_colors():
        emojis_image_path = 'resources/emojis.png'
        emojis_image = Image.open(emojis_image_path)
        width, height = emojis_image.size
        emoji_height = 47
        base_y = 0
        processed_emojis_counter = 0
        emoji_colors = []
        while base_y + emoji_height < height:
            avgs = AvgColor(['red', 'green', 'blue'])
            for x in range(0, width):
                for y in range(base_y, base_y + emoji_height):
                    pixel = emojis_image.getpixel((x, y))
                    if pixel[3] == 255:
                        avgs.add(pixel)
            emoji_colors.append(avgs.calculate())
            processed_emojis_counter += 1
            base_y += emoji_height
        return emoji_colors

    @staticmethod
    def get_emoji_average_colors():
        emoji_colors = EmojiArt._load_or_create(
            'resources/emoji_colors.pickle',
            EmojiArt.convert_emojis_to_colors
        )
        return emoji_colors

    def __init__(self, *args, **kwargs):
        self.emoji_average_colors = EmojiArt.get_emoji_average_colors()
        super(EmojiArt, self).__init__(*args, **kwargs)

    def _prepare_image(self, image, width, scale, height_to_width):
        self._scale_image(image, width, scale, height_to_width)
        self._pixel_matrix = PixelMatrix.from_image(self._image)

    def _prepare_ascii_art(self):
        self._pixel_matrix = PixelMatrix.from_image(self._image)
        self.colors_kd_tree = kd.KDTree(self.emoji_average_colors)
        self._ascii_art_matrix = self._pixel_matrix.map(self.pixel_to_ascii)

    def pixel_to_ascii(self, pixel, *args):
        index = self.colors_kd_tree.query([pixel[:3]])[1][0]
        if index >= len(emojis):
            return ' '
        return emojis[index]

__doc__ = u"""
Convert images to aciiart-like text with unicode symbols or emojis.

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
    textart.py [-s=<sc>] [-f=<fs>] [-c=<na>] [-b] [-g=<gs>] [-e] [-i] [-j] [-w=<ws>] <path_to_image>

Options:
    -h --help                       Show this screen
    -w=<ws> --width=<ws>            Width of output
    -s=<sc> --scale=<sc>            Resize image by this value before conversion [default: 1.0]
    -f=<fs> --height_to_width=<fs>  Rescale width by this value to match fonts height to width proportion [default: 1.8]
    -c=<na> --symbols_set=<na>      Name of symbols set to use, possible values: {} [default: small_ascii]
    -b --black_on_white             Reverse symbols set
    -e --edges                      Ascii art is created only from edges
    -i --fill                       Ascii art contains edges
    -j --emoji                      Use emojis
    -g=<gs> --gauss=<gs>            Size of Gauss blur to use when finding edges [default: 0]
""".format(', '.join(AsciiArt.symbols_sets.keys()))


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    image = Image.open(arguments['<path_to_image>'])
    cls = AsciiArt
    if arguments['--edges']:
        cls = EdgeAsciiArt
    if arguments['--fill']:
        cls = FillAsciiArt
    if arguments['--emoji']:
        cls = EmojiArt
    print cls(
        image,
        width=int(arguments['--width'] if arguments['--width'] else 0),
        scale=float(arguments['--scale']),
        height_to_width=float(arguments['--height_to_width']),
        symbols_set_name=arguments['--symbols_set'],
        black_on_white=arguments['--black_on_white'],
        gauss_blur=float(arguments['--gauss'])
    )

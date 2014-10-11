# -*- coding: utf-8 -*-
u"""
Create emoji art (as in ascii art).

                 🍩🏀🏀🏀🏀🏀🍩
              😡😡😡🎃🎃🌞🌞🌞🎃🎃🎃😡😡
           😡😡🎃🌞😛🌟💡💡💡💡💡💡💡🌟🌟🌞🎃😡😡
         😡🎃🌞😊🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟😊🌞🎃🎃
        🏀🍯🌞💛🌟🌟⭐🌟🍞🔓⭐🌟🌟🌟⭐🔓👱🍞⭐🌟⭐💛🌞🌞🎃‼
       🏀🎃😚🔆🌕🌕🌕🌕🍠🍘🚪😷🌕🌕🌕😷🚪🍘🍘🌕🌕🌕🌕🔆😚🌞🎃
      🍩🎃🌞😶🔅🔆🔆💛🔅😻🍘🐅😪💛🔆💛😪🐅🏀🍘🔅🔆🔆🔆🔅😶🌞🌞🍩
      🎃🎃🌞😶😶😶😶😶😶🚤🏀🌻⚠🔥😶🔥⚠🌻🍘🍘😶😶😶😶😶😶😚🌞🎃
      🎃🎃🌞😶😶😶😶😶😶😌🚤⚠🔥😶😶😶🔥⚠🌻🚤😶😶😶😶😶😶😊🌞🎃
      🎃🎃🌞😊😊🌞🌞🔥✨🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🌞🌞🌞😊🌞🌞🎃
     🎼🐞🎃🌞🌞🌞🏀📵🚂🚳🍩🍩🐞🍘🍘🍘🍘🍘🐞🐞🍩🚳🚂🐞🌻🌞🌞🌞🌞🍩
      🎼🏀🎃🌞🌞🚤🐝🐄👟📑🐁💭💭💭💭💭💭💭💭🐁🔪👨🐝🌼🌞🌞🌞🎃🎼
       🎼🏀🌞🌞🌞🌼🌻🏀🍘🐞🍩🍩🍩🍩🍩🍩🍩🍩🐞🏀🌻📒🌞🌞🌞🎃🏀
       🎼🎼🎃🌞🌞🌞🌞🌼🌻🌻🎃🎃🎃🎃🎃🎃🎃🎃🎸📒🌞🌞🌞🌞🎃🍩🎼
         🎼🐞🎃🌞🌞🌞🌞🌞🌼🚤🌻🌻🌻🚤🌼📒🌞🌞🌞🌞🎃🐞🎼🎼
          🎼🎼🎼🍘🎃🌞🌞🌞🌞🌞🌞🌞🌞🌞🌞🌞🎃🍘🎼🎼🎼
            🎼🎼🎼🎼🎼🍩🏀🏀🏀🏀🏀🍩💲🎼🎼🎼🎼

Usage:
    emojiart.py [-s=<sc>] [-f=<fs>] <path_to_image>

Options:
    -h --help                       Show this screen
    -s=<sc> --scale=<sc>            Resize image by this value before conversion [default: 1.0]
    -f=<fs> --height_to_width=<fs>  Rescale width by this value to match fonts height to width proportion [default: 1.8]
"""

from PIL import Image, ImageDraw
import docopt
import scipy.spatial.kdtree as kd
from resources.emojis import emojis
import pickle
from collections import OrderedDict

emojis_image = Image.open('resources/emojis.png')
width, height = emojis_image.size

interval = 47
sy = 0
avgs = []
i = 0


def load_or_create(filename, create):
    try:
        with open(filename) as f:
            return pickle.load(f)
    except (IOError, EOFError):
        with open(filename, 'w') as f:
            creation = create()
            pickle.dump(creation, f)
            return creation


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


def _create_emojis_colors_test_image(colors, width, height, filename):
    im = Image.new('RGBA', (width, len(colors) * height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)
    for i, color in enumerate(colors):
        color = tuple(color)
        draw.rectangle([0, i * height, width, (i + 1) * height], fill=color)
    # im.show()
    im.save('test_images/' + filename, 'PNG')


def convert_emojis_to_colors():
    emojis_image_path = 'resources/emojis.png'
    emojis_image = Image.open(emojis_image_path)
    width, height = emojis_image.size
    emoji_height = 47
    base_y = 0
    processed_emojis_counter = 0
    emoji_colors = []
    emoji_colors_with_alpha = []
    while base_y + emoji_height < height:
        avgs = AvgColor(['red', 'green', 'blue'])
        avgsa = AvgColor(['red', 'green', 'blue', 'alpha'])
        # cut = emojis_image.crop([0, base_y, width, base_y + emoji_height])
        # cut.save('test_images/cuts/{}.png'.format(processed_emojis_counter), 'PNG')
        for x in range(0, width):
            for y in range(base_y, base_y + emoji_height):
                pixel = emojis_image.getpixel((x, y))
                if pixel[3]:
                    avgsa.add(pixel)
                if pixel[3] == 255:
                    avgs.add(pixel)
        emoji_colors.append(avgs.calculate())
        emoji_colors_with_alpha.append(avgsa.calculate())
        processed_emojis_counter += 1
        base_y += emoji_height
    # _create_emojis_colors_test_image(
    #     emoji_colors, width, emoji_height, 'emoji_colors.png')
    # _create_emojis_colors_test_image(
    #     emoji_colors_with_alpha, width, emoji_height, 'emoji_colors_alpha.png')
    return emoji_colors, emoji_colors_with_alpha


def _get_pixels(im):
    width, height = im.size
    pixels = []
    for y in range(0, height):
        for x in range(0, width):
            pixels.append(im.getpixel((x, y)))
    return pixels


def _fix_pixel(p, include_alpha):
    if include_alpha:
        return p
    return p[:3]


def _test_alpha(p):
    if len(p) <= 3:
        return True
    return p[3]


def print_emojis(filename, include_alpha=False, scale=1.0, height_to_width=1.8):
    emoji_colors, emoji_colors_with_alpha = load_or_create(
        'resources/emoji_colors.pickle',
        convert_emojis_to_colors
    )
    if filename.lower().endswith('jpg') or filename.lower().endswith('jpeg'):
        include_alpha = False
    emoji_colors = emoji_colors_with_alpha if include_alpha else emoji_colors

    im = Image.open(filename)
    width, height = im.size
    width, height = int(width * scale * height_to_width), int(height * scale)
    im = im.resize((width, height))

    pixels = _get_pixels(im)
    colors = kd.KDTree(emoji_colors)
    nearest_emoji_indices = colors.query([_fix_pixel(p, include_alpha) for p in pixels])[1]
    no_emojis = len(emojis)
    matched_emojis = [emojis[i] if i < no_emojis else u' ' for i in nearest_emoji_indices]
    # when alpha = 0 use white space
    matched_symbols = [e if _test_alpha(p) else u' ' for e, p in zip(matched_emojis, pixels)]

    for i in range(0, width * height, width):
        print ''.join(matched_symbols[i:i + width]).encode('utf-8')


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    print_emojis(
        arguments['<path_to_image>'],
        scale=float(arguments['--scale']),
        height_to_width=float(arguments['--height_to_width']),
    )

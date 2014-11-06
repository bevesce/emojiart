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


def _load_or_create(filename, create):
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
        # cut = emojis_image.crop([0, base_y, width, base_y + emoji_height])
        # cut.save('test_images/cuts/{}.png'.format(processed_emojis_counter), 'PNG')
        for x in range(0, width):
            for y in range(base_y, base_y + emoji_height):
                pixel = emojis_image.getpixel((x, y))
                if pixel[3] == 255:
                    avgs.add(pixel)
        emoji_colors.append(avgs.calculate())
        processed_emojis_counter += 1
        base_y += emoji_height
    # _create_emojis_colors_test_image(
    #     emoji_colors, width, emoji_height, 'emoji_colors.png')
    # _create_emojis_colors_test_image(
    #     emoji_colors_with_alpha, width, emoji_height, 'emoji_colors_alpha.png')
    return emoji_colors


def get_emoji_average_colors():
    emoji_colors = _load_or_create(
        'resources/emoji_colors.pickle',
        convert_emojis_to_colors
    )
    return emoji_colors


def print_emojis(filename, scale=1.0, height_to_width=1.8):
    emoji_art = gen_emoji_art(filename, scale, height_to_width)
    print emoji_art.encode('utf-8')


def gen_emoji_art(filename, scale=1.0, height_to_width=1.8):
    orginal_size_image = Image.open(filename)
    image = _resize_image(orginal_size_image, scale, height_to_width)
    pixels = _get_pixels(image)
    matched_symbols = _convert_pixels_to_symbols(pixels)
    return _format_symbols_to_size(matched_symbols, image.size)


def _resize_image(image, scale, height_to_width):
    width, height = image.size
    new_width, new_height = int(width * scale * height_to_width), int(height * scale)
    return image.resize((new_width, new_height))


def _get_pixels(image):
    width, height = image.size
    pixels = []
    for y in range(0, height):
        for x in range(0, width):
            pixels.append(image.getpixel((x, y)))
    return pixels


def _convert_pixels_to_symbols(pixels):
    nearest_emojis = _find_nearest_emojis(pixels)
    matched_symbols = [e if _is_visible(p) else u' ' for e, p in zip(nearest_emojis, pixels)]
    return matched_symbols


def _find_nearest_emojis(pixels):
    emoji_colors = get_emoji_average_colors()
    colors_kd_tree = kd.KDTree(emoji_colors)
    nearest_emoji_indices = colors_kd_tree.query([_exclude_alpha(p) for p in pixels])[1]
    nearest_emojis = [emojis[i] if i < len(emojis) else u' ' for i in nearest_emoji_indices]
    return nearest_emojis


def _exclude_alpha(p):
    return p[:3]


def _is_visible(p):
    if len(p) <= 3:
        return True
    return p[3]


def _format_symbols_to_size(matched_symbols, size):
    width, height = size
    rows = []
    for i in range(0, width * height, width):
        rows.append(''.join(matched_symbols[i:i + width]))
    return u'\n'.join(rows)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    print_emojis(
        arguments['<path_to_image>'],
        scale=float(arguments['--scale']),
        height_to_width=float(arguments['--height_to_width']),
    )

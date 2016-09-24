from configuration import config

DEBUG = config.get('DEBUG', False)
if DEBUG:
    import os
    import shutil
    try:
        shutil.rmtree('out/debug')
    except:
        pass
    try:
        os.mkdir('out/debug')
    except:
        pass

debug_counter = 0


def deb(im, name):
    global debug_counter
    if DEBUG:
        print name
        im.save('out/debug/' + str(debug_counter) + ' ' + name + '.png')
        debug_counter += 1


def random_color():
    from random import randint
    return (randint(0, 255), randint(0, 255), randint(0, 255))

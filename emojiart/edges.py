# -*- coding: utf-8 -*-
from PIL import ImageFilter
import math
from pixelmatrix import PixelMatrix


class Operator(object):
    roberts_cross_threshold = (0.33, 0.3)
    sobel_threshold = (30.0, 10.0)
    prewitt_threshold = (30.0, 10.0)

    @staticmethod
    def operator(gradient_function, d, x, y):
        gx, gy = gradient_function(d, x, y)
        g = math.sqrt(gx ** 2 + gy ** 2)
        o = math.atan2(gy, gx)
        return g, o, (gx, gy)

    @staticmethod
    def roberts_cross(v, d, x, y):
        def xy_gradient(A, x, y):
            gx = math.sqrt(A.get(x, y, 0)) - math.sqrt(A.get(x + 1, y + 1, 0))
            gy = math.sqrt(A.get(x + 1, y, 0)) - math.sqrt(A.get(x, y + 1, 0))
            return gx, gy
        return Operator.operator(xy_gradient, d, x, y)

    @staticmethod
    def sobel(v, d, x, y):
        def xy_gradient(A, x, y):
            def a(x, y):
                return A.get(x, y, 0)
            gx, gy = (
                - a(x - 1, y - 1) + a(x + 1, y - 1) +
                - 2 * a(x - 1, y) + 2 * a(x + 1, y) +
                - a(x - 1, y + 1) + a(x + 1, y + 1)
            ), (
                - a(x - 1, y - 1) + a(x - 1, y + 1) +
                - 2 * a(x, y - 1) + 2 * a(x, y + 1) +
                - a(x + 1, y - 1) + a(x + 1, y + 1)
            )
            return gx, gy
        return Operator.operator(xy_gradient, d, x, y)

    @staticmethod
    def prewitt(v, d, x, y):
        def xy_gradient(A, x, y):
            def a(x, y):
                return A.get(x, y, 0)
            gx, gy = (
                - a(x - 1, y - 1) + a(x + 1, y - 1) +
                - a(x - 1, y) + a(x + 1, y) +
                - a(x - 1, y + 1) + a(x + 1, y + 1)
            ), (
                - a(x - 1, y - 1) + a(x - 1, y + 1) +
                - a(x, y - 1) + a(x, y + 1) +
                - a(x + 1, y - 1) + a(x + 1, y + 1)
            )
            return gx, gy
        return Operator.operator(xy_gradient, d, x, y)


class Filter(object):
    @staticmethod
    def non_maximum_suppression(v, d, x, y):
        def o_to_v(o):
            o = abs(o)
            pi8 = math.pi / 8.0
            if o < pi8:
                return (-1, 0), (1, 0)
            elif o < 3 * pi8:
                return (-1, -1), (1, 1)
            elif o < 5 * pi8:
                return (0, -1), (0, 1)
            elif o < 7 * pi8:
                return (-1, 1), (1, -1)
            return (-1, 0), (1, 0)
        g, o, p = v
        (dx1, dy1), (dx2, dy2) = o_to_v(o)
        g1, _, _ = d.get(x + dx1, y + dy1, (0, 0, 0))
        g2, _, _ = d.get(x + dx2, y + dy2, (0, 0, 0))
        if g < g1:
            return 0, 0, 0
        if g < g2:
            return 0, 0, 0
        return g, o, p

    @staticmethod
    def connect_edges(v, d, x, y):
        def neighs(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return (
                (x1 == x2 and abs(y1 - y2) <= 1) or
                (y1 == y2 and abs(x1 - x2) <= 1)
            )
        if v < 255:
            return v
        ns = [
            (d.get(x + i, y + j, 255), (x + i, y + j))
            for i in range(-1, 2) for j in range(-1, 2) if (i, j) != (0, 0)
        ]
        if sum([1 if n < 255 else 0 for n, _ in ns]) == 2:
            p1, p2 = [p for n, p in ns if n < 255]
            if neighs(p1, p2):
                return v
            return 125
        return v

    @staticmethod
    def connect_weak_to_strong_edges(pixel_matrix):
        grays = pixel_matrix.pixels_with_color(125)
        prev_len = 0
        while prev_len != len(grays):
            prev_len = len(grays)
            for x, y in list(grays):
                if Filter.has_strong_neighbour(None, pixel_matrix, x, y):
                    pixel_matrix[x, y] = 0, pixel_matrix[x, y][1]
                    grays.remove((x, y))

    @staticmethod
    def color_if_any(color1, color2, *args):
        def f(v, d, x, y):
            if any([color1 == d[x, y] for d in args if d]):
                return color1
            return color2
        return f

    @staticmethod
    def filter_weak(v, d, x, y):
        if v[0] == 0:
            return 0, v[1]
        else:
            return 255, v[1]

    @staticmethod
    def has_strong_neighbour(v, d, x, y):
        return any([
            d.get(x + i, y + j, (255, None))[0] == 0
            for i in range(-1, 2) for j in range(-1, 2)
        ])

    @staticmethod
    def thresholding(th, tl):
        def f(v, d, x, y):
            if v[0] >= th:
                return 0, v[1]
            if v[0] >= tl:
                return 125, v[1]
            return 255, v[1]
        return f


def find_edges(im, gauss_size=0):
    im = im.convert("L").filter(ImageFilter.GaussianBlur(gauss_size))
    pixs = PixelMatrix.from_image(im)
    s = pixs.map(Operator.sobel).map(Filter.non_maximum_suppression)
    s = s.map(Filter.thresholding(*Operator.sobel_threshold))
    Filter.connect_weak_to_strong_edges(s)
    s = s.map(Filter.filter_weak)
    return s

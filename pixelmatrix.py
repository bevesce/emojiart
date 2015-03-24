class Matrix(object):
    join_symbol = ''

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.data = [[0 for _ in range(width)] for _ in range(height)]

    def __str__(self):
        return u'\n'.join(
            self.join_symbol.join((unicode(e) for e in row))
            for row in self.data
        ).encode('utf-8')

    def __getitem__(self, index):
        x, y = index
        if x < 0 or y < 0:
            raise IndexError
        return self.data[y][x]

    def __setitem__(self, index, value):
        x, y = index
        self.data[y][x] = value

    def get(self, x, y, v=None):
        try:
            return self[x, y]
        except:
            return v

    def map(self, mapper):
        new_matrix = self.empty()
        for x in range(0, self.width):
            for y in range(0, self.height):
                new_matrix[x, y] = mapper(self[x, y], self, x, y)
        return new_matrix

    def empty(self):
        return Matrix(self.width, self.height)


class PixelMatrix(Matrix):
    @classmethod
    def from_image(cls, image):
        pixels = image.load()
        width, height = image.size
        matrix = cls(width, height)
        for x in range(width):
            for y in range(height):
                matrix[x, y] = pixels[x, y]
        matrix.image = image
        return matrix

    def pixels_with_color(self, color):
        s = set()
        for x in range(self.width):
            for y in range(self.height):
                if self[x, y] == color or self[x, y][0] == color:
                    s.add((x, y))
        return s

    def empty(self):
        return PixelMatrix.from_image(self.image)

from point import Point


class Vertex(Point):
    """ A Vertex is an extension of Class Point and takes (x,y) attributes and an n number of field values."""
    def __init__(self, x, y, z):
        Point.__init__(self, x, y)
        self.__field_values = [z]

    def get_c(self, pos):
        if pos in (0, 1):
            return super().get_c(pos)
        else:
            try:
                return self.__field_values[pos-2]
            except IndexError as e:
                raise e

    def set_c(self, pos, c):
        if pos in (0, 1):
            super().set_c(pos, c)
        else:
            try:
                self.__field_values[pos-2] = c
            except IndexError:
                # Instead of raising an exception append the field value to the end of the array
                self.__field_values.append(c)

    def get_fields_num(self):
        return len(self.__field_values)

    def __str__(self):
        return "%s,%s,%s" % (self.get_c(0), self.get_c(1), self.get_c(2))

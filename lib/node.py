from domain import Domain
from point import Point
from cartographic_model import get_carto_symbol
from shapely.geometry import Point as Shapely_Point

# sons legend:
#   ne = 0
#   nw = 1
#   sw = 2
#   se = 3


class Node(object):
    """ Creates Class node """
    def __init__(self):
        self.__vertex_ids = list()  # indices of points
        self.__triangle_ids = list()  # Indices of triangles
        self.__sons = None

    def add_vertex(self, v_id):
        self.__vertex_ids.append(v_id)

    def remove_vertex(self, v_id):
        self.__vertex_ids.remove(v_id)

    def get_vertices(self):
        return self.__vertex_ids

    def get_z_min(self):
        return self.__z_min

    def get_z_max(self):
        return self.__z_max

    def set_z_min(self,z_min):
        self.__z_min = z_min

    def set_z_max(self,z_max):
        self.__z_max = z_max
    
    def get_vertices_num(self):
        return len(self.__vertex_ids)

    def reset_vertices(self):
        self.__vertex_ids = list()

    def add_triangle(self, t_id):
        self.__triangle_ids.append(t_id)

    def get_triangles(self):
        return self.__triangle_ids

    def get_triangles_num(self):
        return len(self.__triangle_ids)

    def init_sons(self):
        self.__sons = [Node() for _ in range(4)]

    def get_son(self, i):
        return self.__sons[i]

    def is_leaf(self):
        return self.__sons is None

    def overflow(self, capacity):
        return len(self.__vertex_ids) > capacity

    @staticmethod
    def compute_son_label_and_domain(son_position, node_label, node_domain, mid_point):
        if son_position == 0:  # "ne":
            return 4*node_label+1, Domain(mid_point, node_domain.get_max_point())
        elif son_position == 1:  # "nw":
            minimum = Point(node_domain.get_min_point().get_c(0), mid_point.get_c(1))
            maximum = Point(mid_point.get_c(0), node_domain.get_max_point().get_c(1))
            return 4*node_label+2, Domain(minimum, maximum)
        elif son_position == 2:  # "sw":
            return 4*node_label+3, Domain(node_domain.get_min_point(), mid_point)
        elif son_position == 3:  # "se":
            minimum = Point(mid_point.get_c(0), node_domain.get_min_point().get_c(1))
            maximum = Point(node_domain.get_max_point().get_c(0), mid_point.get_c(1))
            return 4*node_label+4, Domain(minimum, maximum)
        else:
            return None, None

    def is_duplicate(self, v_index, tin):
        for i in self.get_vertices():
            if tin.get_vertex(i) == tin.get_vertex(v_index):
                return True
        return False

    def carto_model_generalization(self, target_v, point_set, delete_list, scale, h_spacing, v_spacing):
        deletes = {}
        for v_id in self.get_vertices():
            v = point_set.get_vertex(v_id)
            if v != target_v:
                target_symbol = get_carto_symbol(target_v, scale, h_spacing, v_spacing)[1]
                v_symbol = get_carto_symbol(v, scale, h_spacing, v_spacing)[1]
                if target_symbol.intersects(v_symbol) and target_v.get_c(2) <= v.get_c(2):
                    # z-value precision issue: use '<=' to remove initial legibility violations
                    deletes[v_id] = v

        for v_id in deletes:
            delete_list.append(deletes[v_id])
            self.remove_vertex(v_id)

        return

    def radius_based_generalization(self, target_v, point_set, delete_list, radius_lookup):
        radius_length = radius_lookup[target_v.__str__()]
        circle = Shapely_Point(target_v.get_c(0), target_v.get_c(1)).buffer(radius_length)
        deletes = {}
        for v_id in self.get_vertices():
            v = point_set.get_vertex(v_id)
            if v != target_v:
                s_point = Shapely_Point(v.get_c(0), v.get_c(1))
                if circle.intersects(s_point) and target_v.get_c(2) <= v.get_c(2):
                    # z-value precision issue: use '<=' to remove legibility violations
                    deletes[v_id] = v

        for v_id in deletes:
            delete_list.append(deletes[v_id])
            self.remove_vertex(v_id)

        return

    def points_in_polygon(self, polygon, point_set, point_list):
        for v_id in self.get_vertices():
            v = point_set.get_vertex(v_id)
            s_point = Shapely_Point(v.get_c(0), v.get_c(1))
            if polygon.intersects(s_point):
                point_list.append(v)
        return

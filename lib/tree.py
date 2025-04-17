from node import Node
from cartographic_model import *
from shapely.geometry import Point, Polygon


class Tree(object):
    """Creates Class Tree"""
    def __init__(self, c):
        self.__root = Node()
        self.__capacity = c

    def get_root(self):
        return self.__root

    def get_leaf_threshold(self):
        return self.__capacity

    def build_point_tree(self, point_set):
        for i in range(point_set.get_vertices_num()):
            self.insert_vertex(self.__root, 0, point_set.get_domain(), i, point_set)

    def build_tin_tree(self, tin):
        # First insert the vertices of the TIN
        for i in range(tin.get_vertices_num()):
            self.insert_vertex(self.__root, 0, tin.get_domain(), i, tin)
        # Then triangles
        for i in range(tin.get_triangles_num()):
            self.insert_triangle(self.__root, 0, tin.get_domain(), i, tin)
    
    def insert_vertex(self, node, node_label, node_domain, v_index, tin):
        if node_domain.contains_point(tin.get_vertex(v_index), tin.get_domain().get_max_point()):
            if node.is_leaf():
                if node.is_duplicate(v_index, tin):
                    return
                node.add_vertex(v_index)  # update append list
                if node.overflow(self.__capacity):
                    node.init_sons()
                    for i in node.get_vertices():
                        self.insert_vertex(node, node_label, node_domain, i, tin)
                    node.reset_vertices()  # empty the list of the current node

            else:  # Internal
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    self.insert_vertex(node.get_son(i), s_label, s_domain, v_index, tin)

    def insert_triangle(self, node, node_label, node_domain, triangle_id, tin):
        tri = tin.get_triangle(triangle_id)
        if node_domain.contains_triangle(tri, tin):
            if node.is_leaf():
                node.add_triangle(triangle_id)  # Update index list

            else:  # Internal
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    self.insert_triangle(node.get_son(i), s_label, s_domain, triangle_id, tin)
    
    def generalization(self, node, node_label, node_domain, target_v, point_set, delete_list, algorithm, scale=None,
                       h_spacing=None, v_spacing=None, radius_lookup=None):

        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0:
                    pass
                else:
                    if algorithm == 'DCM':
                        node.carto_model_generalization(target_v, point_set, delete_list, scale, h_spacing, v_spacing)
                    else:
                        node.radius_based_generalization(target_v, point_set, delete_list, radius_lookup)

            else:  # Internal
                # Visit the sons in the following order: NE -> NW -> SW -> SE
                mid_point = node_domain.get_centroid()
                if algorithm == 'DCM':
                    search_window = get_carto_symbol(target_v, scale, h_spacing, v_spacing)[0]
                else:
                    radius_length = radius_lookup[target_v.__str__()]
                    search_window = Point(target_v.get_c(0), target_v.get_c(1)).buffer(radius_length)
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    if s_domain.contains_polygon(search_window):
                        self.generalization(node.get_son(i), s_label, s_domain, target_v, point_set, delete_list,
                                            algorithm, scale, h_spacing, v_spacing, radius_lookup)
                        break
                    elif s_domain.intersects_polygon(search_window):
                        self.generalization(node.get_son(i), s_label, s_domain, target_v, point_set, delete_list,
                                            algorithm, scale, h_spacing, v_spacing, radius_lookup)

    def points_in_polygon(self, node, node_label, node_domain, polygon, point_set, point_list):
        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0:
                    pass
                else:
                    node.points_in_polygon(polygon, point_set, point_list)
            else:
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    if s_domain.contains_polygon(polygon):
                        self.points_in_polygon(node.get_son(i), s_label, s_domain, polygon, point_set, point_list)
                        break
                    if s_domain.intersects_polygon(polygon):
                        self.points_in_polygon(node.get_son(i), s_label, s_domain, polygon, point_set, point_list)

    def contour(self,node,node_label,tin,z_values,points,bv):
        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0 and node.get_triangles_num() == 0:
                    pass
                else: #full leaf
                    for z in z_values:
                        if node.get_z_min() <= z <= node.get_z_max():
                            for t_id in node.get_triangles():
                                if bv[z][t_id] == 0:
                                    bv[z][t_id] = 1
                                    tri = tin.get_triangle(t_id)
                                    tri_z_vals = []
                                    for v in range(tri.get_vertices_num()):
                                        v_id = tri.get_tv(v)
                                        tri_z_vals.append(tin.get_vertex(v_id).get_c(2))
                                    if min(tri_z_vals) <= z <= max(tri_z_vals):
                                        above, below = [], []
                                        for v in range(tri.get_vertices_num()):
                                            v_id = tri.get_tv(v)
                                            if tin.get_vertex(v_id).get_c(2) >= z:
                                                above.append(tin.get_vertex(v_id))
                                            else:
                                                below.append(tin.get_vertex(v_id))

                                        Coords = []
                                        if len(above) == 3 or len(below) == 3:
                                            continue

                                        elif len(above) == 2 and len(below) == 1:
                                            #bv[z][t_id] = 1
                                            for point in above:
                                                t = (z - point.get_c(2)) / float(below[0].get_c(2) - point.get_c(2))
                                                x = point.get_c(0) + t * (below[0].get_c(0) - point.get_c(0))
                                                y = point.get_c(1) + t * (below[0].get_c(1) - point.get_c(1))
                                                x = round(x, 3)
                                                y = round(y, 3)
                                                Coords.append([x, y, z])

                                        elif len(above) == 1 and len(below) == 2:
                                            #bv[z][t_id] = 1
                                            for point in below:
                                                t = (z - point.get_c(2)) / float(above[0].get_c(2) - point.get_c(2))
                                                x = point.get_c(0) + t * (above[0].get_c(0) - point.get_c(0))
                                                y = point.get_c(1) + t * (above[0].get_c(1) - point.get_c(1))
                                                x = round(x, 3)
                                                y = round(y, 3)
                                                Coords.append([x, y, z])

                                        points.append(Coords)

                    return points

            else: # Internal
                ### we visit the sons in the following order: NE -> NW -> SW -> SE
                for i in range(4):
                    s_label = 4*node_label+1+i
                    self.contour(node.get_son(i),s_label,tin,z_values,points,bv)
                return

    def set_min_max(self,node,node_label,tin):
        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0 and node.get_triangles_num() == 0:
                    pass
                else: #full leaf
                    z_list = []
                    for t_id in node.get_triangles():
                        t = tin.get_triangle(t_id)
                        for v in range(t.get_vertices_num()):
                            v_id = t.get_tv(v)
                            z_list.append(tin.get_vertex(v_id).get_c(2))
                    node.set_z_min(min(z_list))
                    node.set_z_max(max(z_list))
            else: # Internal
                ### we visit the sons in the following order: NE -> NW -> SW -> SE
                for i in range(4):
                    s_label = 4*node_label+1+i
                    self.set_min_max(node.get_son(i),s_label,tin)
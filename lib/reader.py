import csv
from vertex import Vertex
from pointset import PointSet
from tin import TIN
from triangles import Triangle

class Reader(object):
    @staticmethod
    def read_xyz_list_to_pointset(xyz_list):
        print(f"Start read_xyz_list_to_pointset")
        point_set = PointSet()
        for index, value in enumerate(xyz_list):
            rounded_value = round(value[2], 1)
            v = Vertex(x=float(value[0]), y=float(value[1]), z=float(rounded_value))
            point_set.add_vertex(v)
            if index == 0:
                point_set.set_domain(v, v)
            else:
                point_set.get_domain().resize(v)
        return point_set
        
    @staticmethod
    def read_vertex_list_to_pointset(vertex_list):
        point_set = PointSet()
        for index, vertex in enumerate(vertex_list):
            point_set.add_vertex(vertex)
            if index == 0:
                point_set.set_domain(vertex, vertex)
            else:
                point_set.get_domain().resize(vertex)
        return point_set

    @staticmethod
    def read_xyz_to_vertex_list(url_in):
        vertex_list = list()
        with open(url_in) as infile:
            reader = csv.reader(infile, delimiter=',')
            for point in reader:
                if float(point[2]) < 0:
                    v = Vertex(x=float(point[0]), y=float(point[1]), z=abs(float(point[2])))
                    vertex_list.append(v)
        infile.close()
        return vertex_list

    '''@staticmethod
    def read_triangulation(triangulation_dict, vertex_list):
        vertices = triangulation_dict['vertices']
        triangles = triangulation_dict['triangles']

        v_list = vertex_list[:]
        xy_list = [[float(v.get_c(0)), float(v.get_c(1))] for v in v_list]

        tin = TIN()
        for i, v in enumerate(vertices):
            index = xy_list.index([float(v[0]), float(v[1])])
            sounding_vertex = v_list[index]

            del xy_list[index]
            del v_list[index]

            tin.add_vertex(sounding_vertex)
            if i == 0:
                tin.set_domain(sounding_vertex, sounding_vertex)
            else:
                tin.get_domain().resize(sounding_vertex)

        for tri in triangles:
            t = Triangle(int(tri[0]), int(tri[1]), int(tri[2]))
            tin.add_triangle(t)

        return tin'''

    @staticmethod
    def read_triangulation(triangulation_dict, vertex_list):
        vertices = triangulation_dict['vertices']
        triangles = triangulation_dict['triangles']
    
        v_list = vertex_list[:]
        xy_list = [[float(v.get_c(0)), float(v.get_c(1))] for v in v_list]
    
        tin = TIN()
        added_count = 0
        skipped_vertices = 0
    
        for i, v in enumerate(vertices):
            coords = [float(v[0]), float(v[1])]
            try:
                index = xy_list.index(coords)
                sounding_vertex = v_list[index]
    
                del xy_list[index]
                del v_list[index]
    
                tin.add_vertex(sounding_vertex)
                added_count += 1
    
                if added_count == 1:
                    tin.set_domain(sounding_vertex, sounding_vertex)
                else:
                    tin.get_domain().resize(sounding_vertex)
    
            except ValueError:
                #print(f"[SKIP] Vertex {coords} not found in xy_list")
                skipped_vertices += 1
                continue
    
        print(f"[INFO] Skipped {skipped_vertices} vertices during triangulation vertex assignment.")
    
        # Set of valid vertex indices (after filtering)
        valid_vertex_indices = set(range(len(tin.get_vertices())))
        
        triangle_count = 0
        skipped_triangles = 0
        
        for tri in triangles:
            try:
                idx0, idx1, idx2 = int(tri[0]), int(tri[1]), int(tri[2])
                if {idx0, idx1, idx2}.issubset(valid_vertex_indices):
                    t = Triangle(idx0, idx1, idx2)
                    tin.add_triangle(t)
                    triangle_count += 1
                else:
                    skipped_triangles += 1
            except Exception as e:
                print(f"[WARN] Could not add triangle {tri}: {e}")
                skipped_triangles += 1
                continue
        
        print(f"[INFO] Added {triangle_count} triangles to TIN.")
        print(f"[INFO] Skipped {skipped_triangles} triangles due to missing vertices.")
        
        return tin


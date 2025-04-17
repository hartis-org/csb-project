import math
import triangle
from scipy.spatial import cKDTree
from shapely.geometry import Point, Polygon, MultiLineString, LineString
from shapely.ops import unary_union
from shapely import distance
from vertex import Vertex

def modified_binary_search(sorted_vertices, v):
    """ Modified binary search algorithm to increase performance."""

    right, left = 0, 0
    vertices_num = len(sorted_vertices)

    while right < vertices_num:
        i = (right + vertices_num) // 2
        if v.get_c(2) < sorted_vertices[i].get_c(2):
            vertices_num = i
        else:
            right = i + 1

    vertices_num = right - 1
    while left < vertices_num:
        i = (left + vertices_num) // 2
        if v.get_c(2) > sorted_vertices[i].get_c(2):
            left = i + 1
        else:
            vertices_num = i

    if left == right-1:
        return left
    else:
        for idx in range(left, right):
            if sorted_vertices[idx] == v:
                return idx

def utm_zone_from_wgs84(lat_wgs84, lon_wgs84):
    """Generic function to determine projected coordinate system (UTM)"""
    # Calculate the UTM zone 
    zone_number = int((lon_wgs84 + 180) / 6) + 1
    
    # EPSG code for northern or southern hemisphere
    hemisphere = '326' if lat_wgs84 >= 0 else '327'  # EPSG code prefix for UTM
    
    return f"EPSG:{hemisphere}{zone_number:02d}"

'''def triangulate(sounding_vertex_list, segments=None, segments_idx=None, holes=None):
    """ Uses a Python wrapper of Triangle (Shechuck, 1996) to triangulate a set of points. Triangulation is
        constrained if bounding vertices are provided; otherwise the triangulation is Delaunay. """
    xy_list = [[v.get_c(0), v.get_c(1)] for v in sounding_vertex_list]
    if segments is not None and segments_idx is not None and holes is not None:
        points = [[v.get_c(0), v.get_c(1)] for v in segments]

        points.extend(xy_list)

        # Constrained
        if len(holes) > 0:
            triangulation = triangle.triangulate({'vertices': points,
                                                  'segments': segments_idx,
                                                  'holes': holes},
                                                  'pCSi')
        else:  # Assertion error is raised if empty list passed to triangulate
            triangulation = triangle.triangulate({'vertices': points,
                                                  'segments': segments_idx},
                                                  'pCSi')
        # p: PSLG; C: Exact arithmetic; S_: Steiner point limit; i: Incremental triangulation algorithm

    else:
        # Delaunay
        triangulation = triangle.triangulate({'vertices': xy_list})

    return triangulation'''

def triangulate(sounding_vertex_list, segments=None, segments_idx=None, holes=None):
    """ Uses a Python wrapper of Triangle (Shechuck, 1996) to triangulate a set of points. Triangulation is
        constrained if bounding vertices are provided; otherwise the triangulation is Delaunay. """
    logger.info('Start triangulate')
    try:
        print(f"Starting triangulation with {len(sounding_vertex_list)} sounding vertices.")
        xy_list = [[v.get_c(0), v.get_c(1)] for v in sounding_vertex_list]
        print(f"Preparing triangulation with {len(xy_list)} sounding vertices.")
		
        if segments is not None and segments_idx is not None and holes is not None:
            points = [[v.get_c(0), v.get_c(1)] for v in segments]
            print(f"Using {len(points)} segment vertices for constrained triangulation.")
            points.extend(xy_list)
            print(f"Total points for triangulation: {len(points)}.")

            print(f'segments_idx has {len(segments_idx)} entries.')
            print(f'Holes provided: {len(holes)}')

            # Perform triangulation
            if len(holes) > 0:
                print('Performing constrained triangulation with holes.')
                triangulation = triangle.triangulate({'vertices': points,
                                                      'segments': segments_idx,
                                                      'holes': holes},
                                                      'pCSi')
                print(f"Performed constrained triangulation with {len(holes)} holes.")
            else:
                print('Performing constrained triangulation without holes.')
                triangulation = triangle.triangulate({'vertices': points,
                                                      'segments': segments_idx},
                                                      'pCSi')
                # p: PSLG; C: Exact arithmetic; S_: Steiner point limit; i: Incremental triangulation algorithm
                print("Performed constrained triangulation without holes.")

        else:  # Assertion error is raised if empty list passed to triangulate
            print('Performing Delaunay triangulation.')
	        # Delaunay
            triangulation = triangle.triangulate({'vertices': xy_list})
            print("Performed Delaunay triangulation.")

        if 'triangles' not in triangulation:
            print(f"Triangulation failed. Returned keys: {list(triangulation.keys())}")
            raise ValueError("'triangles' key missing from triangulation result")

            print(f"Triangulation successful. Triangles count: {len(triangulation['triangles'])}.")

    except Exception as e:
        print(f"Error during triangulation: {e}")
        raise

    return triangulation

def get_feature_segments(shoreline_geoms, bathymetric_extent, soundings):
    """ Extracts contour and boundary segments and returns the coordinates as Vertex objects along with the associated
        index list."""

    geometry_dict = dict()
    geom_idx = 0

    tree = cKDTree(soundings)
        
    boundary_lines = list()
    if bathymetric_extent.geom_type == 'MultiPolygon':
        for polygon in bathymetric_extent.geoms:
            boundary = polygon.boundary
            if boundary.geom_type == 'MultiLineString':
                for line in boundary.geoms:
                    boundary_lines.append(line)
            else:
                boundary_lines.append(boundary)

    elif bathymetric_extent.geom_type == 'Polygon':
        boundary = bathymetric_extent.boundary
        if boundary.geom_type == 'MultiLineString':
            for line in boundary.geoms:
                boundary_lines.append(line)
        else:
            boundary_lines.append(boundary)

    for boundary_line in boundary_lines:
        line_x, line_y = boundary_line.coords.xy
        geometry_dict[geom_idx] = list()
        for i in range(len(line_x)):
            distance_to_neighbor, index = tree.query((line_x[i], line_y[i], 0))
            distance_to_shoreline = shoreline_geoms.distance(Point((line_x[i], line_y[i], 0)))
            if distance_to_shoreline < distance_to_neighbor:  # UPDATE THIS TO EXCLUDE BATHYMETRIC CORNERS OF CHART EXTENT
            # if distance_to_shoreline == 0:
                neareast_neighbor_depth = 0
            else:
                neareast_neighbor_depth = soundings[index][2]
            geometry_dict[geom_idx].append(Vertex(line_x[i], line_y[i], neareast_neighbor_depth))
        geom_idx += 1

    segment_vertices, length_list = list(), list()
    for geom_idx in geometry_dict.keys():
        segment_length = len(geometry_dict[geom_idx])
        length_list.append(segment_length)
        for p in geometry_dict[geom_idx]:
            segment_vertices.append(p)

    index_list = list()
    for i in range(len(length_list)):
        if i == 0:
            start = 0
            end = length_list[i]
        else:
            start = sum(length_list[:i])
            end = start + length_list[i]

        starting_point = segment_vertices[start]
        ending_point = segment_vertices[end-1]

        if starting_point == ending_point:
            index_list.extend(create_idx(start, end-1, closed=True))
        else:
            index_list.extend(create_idx(start, end-1, closed=False))

    holes = list()
    if bathymetric_extent.geom_type == 'Polygon':
        for interior in bathymetric_extent.interiors:
            hole_center = Polygon(interior).representative_point()
            holes.append([hole_center.x, hole_center.y])
    elif bathymetric_extent.geom_type == 'MultiPolygon':
        for part in bathymetric_extent.geoms:
            for interior in part.interiors:
                hole_center = Polygon(interior).representative_point()
                holes.append([hole_center.x, hole_center.y])

    return segment_vertices, index_list, holes
    
def create_idx(start, end, closed):
    """ Creates indexes for contour vertices so that segments can be created for a constrained triangulation. """

    if closed is True:
        return [[i, i + 1] for i in range(start, end)] + [[end, start]]
    else:
        return [[i, i + 1] for i in range(start, end)]
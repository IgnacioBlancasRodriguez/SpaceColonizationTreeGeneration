import random
import math
from Renderer import Object
import numpy as np
from pyquaternion import Quaternion
import itertools as it

C2_BSpline_matrix = np.array(np.mat([[1/6, 2/3, 1/6, 0],
                                     [-1/2, 0, 1/2, 0],
                                     [1/2, -1, 1/2, 0],
                                     [-1/6, 1/2, -1/2, 1/6]]))

def vector_magnitude(vec):
    # Produces the magnitude of a vector

    square_sum = 0
    for coord in vec: square_sum += (coord**2)

    return math.sqrt(square_sum)

def dot_product(v1, v2):
    # Produces the dot product of two vectors

    sum = 0
    for i in range(0, len(v1)):
        sum += (v1[i] * v2[i])
    return sum

def quaternion_between_vecs(from_vec, to_vec):
    # Gets the quatertion corresponding to the rotation
    # from the first to the second vector

    axis = np.cross(from_vec, to_vec).tolist()
    axis_magnitude = vector_magnitude(axis)
    axis = [coord / axis_magnitude for coord in axis]
    ang = math.atan(axis_magnitude / dot_product(from_vec, to_vec))

    return Quaternion(axis=axis, angle=ang)

def b_spline(matrix, points):
    return lambda t: np.matmul(np.array([1, t, t**2, t**3]),
                               np.matmul(matrix, points))
def b_spline_deriv(matrix, points):
    return lambda t: np.matmul(np.array([0, 1, 2*t, 3*(t**2)]),
                               np.matmul(matrix, points))
def b_spline_deriv_2(matrix, points):
    return lambda t: np.matmul(np.array([0, 0, 2, 6*t]),
                               np.matmul(matrix, points))

def get_t(n, t):
    # Produces the inner t of the corresponding
    # spline depinding on the number of splines

    return (n - 1) * t

def generate_curve(points, curve_fun):
    # Generates a bspline using the given control points and bspline function
    n = len(points)
    curves = []
    for i in range(-3, n):
        cur_pts = [points[(((i + j) if (i + j) >= 0 else 0)
                    if (i + j) < n else n - 1)]
                        for j in range(0, 4)]
        curve = curve_fun(C2_BSpline_matrix, cur_pts)
        
        curves.append(curve)
    n_curves = len(curves)

    return lambda t: curves[int(get_t(n_curves, t))](
        get_t(n_curves, t) - int(get_t(n_curves, t)))

def generate_circle(radius, i_vec, j_vec,
                    resolution, point) -> list:
    # Consumes two basis vectors, a radius, resolution and point and produces
    # a circle of the given resolution centered on the
    # point and projected on the plane formed by the bais vectors

    if resolution == 0: raise("Given resultion can not be 0")
    verts = []
    i_vec_norm = vector_magnitude(i_vec)
    i_vec_unit = [coord / i_vec_norm for coord in i_vec]
    
    j_vec_norm = vector_magnitude(j_vec)
    j_vec_unit = [coord / j_vec_norm for coord in j_vec]

    for i in range(0, resolution):
        theta = (2 * math.pi / resolution) * i
        x_ij = radius * math.cos(theta)
        y_ij = radius * math.sin(theta)
        
        verts.append([x_ij * i_vec_unit[i] + y_ij * j_vec_unit[i] + point[i]
                      for i in range(0, 3)])
    return verts

def generate_frame(curve, T_curve, t,
                   prev_T, prev_N, prev_B) -> (list, list, list):
    # Generates a frame of basis vectors to render the cricles
    # using quaternions and the previous frame

    T_vec = T_curve(t)
    T_vec_magnitude = vector_magnitude(T_vec)
    delta_t = 0.1
    while T_vec_magnitude == 0 and (t + delta_t) <= 1:
        T_vec = [curve((t) + delta_t)[j] - curve(t)[j]
                    for j in range(0, 3)]
        T_vec_magnitude = vector_magnitude(T_vec)
        delta_t += 0.1
    if T_vec_magnitude == 0:
        T_vec = prev_T
        N_vec = prev_N
        B_vec = prev_B
    else:
        T_vec = [coord / T_vec_magnitude for coord in T_vec]
        if vector_magnitude(np.cross(prev_T, T_vec)) != 0:
            quat = quaternion_between_vecs(prev_T, T_vec)
            N_vec = quat.rotate(prev_N)
            B_vec = quat.rotate(prev_B)
        else:
            N_vec = prev_N
            B_vec = prev_B
    return (T_vec, N_vec, B_vec)

class Node:
    def __init__(self, x : int, y : int, z : int):
        self.x, self.y, self.z = x, y, z
        self.directions = []
        self.prev_direction = None
        self.parent_nodes = []
        self.children_nodes = None
        self.T_vec = []
        self.N_vec = []
        self.B_vec = []
        self.radius = None
    def get_average_direction(self):
        # Gets the average direction from its array of directions
        
        total_dir = [0, 0, 0]
        for dir in self.directions:
            total_dir[0] += dir[0]
            total_dir[1] += dir[1]
            total_dir[2] += dir[2]
        dist = vector_magnitude(total_dir)
        if dist == 0:
            return total_dir
        else:
            return [total_dir[0] / dist, total_dir[1] / dist, total_dir[2] / dist]

class Atractor:
    def __init__(self, x, y, z, atractor_distance, kill_distance):
        self.x, self.y, self.z = x, y, z
        self.atractor_distance = atractor_distance
        self.kill_distance = kill_distance
        self.associated_node = None
        self.prev_distance = math.inf
    def set_node(self, node, prev_dist):
        # Sets a given node to be its associated node

        if isinstance(node, Node):
            self.prev_distance = prev_dist
            self.associated_node = node
        else:
            raise("Given node parameter is not of type Node")
    def get_distance(self, node):
        # Produces the distance to a node

        if isinstance(node, Node):
            dist = vector_magnitude([self.x - node.x,
                                   self.y - node.y,
                                   self.z - node.z])
            return dist
        else:
            raise("Given node parameter is not of type Node")
    def in_kill_distance(self, node):
        # Check if a node is within its kill distance

        return self.get_distance(node) <= self.kill_distance
class AtractorCloud:
    def __init__(self, x_domain, f_y, f_z):
        self.f_y = f_y
        self.f_z = f_z
        self.x_domain = x_domain
        self.atractor_cloud = []
    def generate_cloud(self, n, atractor_distance, kill_distance):
        # Generates a cloud of attractors

        self.atractor_cloud = []
        for i in range(0, n):
            x = self.x_domain[0] + (random.random() * (self.x_domain[1] - self.x_domain[0]))
            y = self.f_y[0](x) + (random.random() * (self.f_y[1](x) - self.f_y[0](x)))
            z = self.f_z[0](x, y) + (random.random() * (self.f_z[1](x, y) - self.f_z[0](x, y)))

            self.atractor_cloud.append(Atractor(x, y, z, atractor_distance, kill_distance))
        return self.atractor_cloud
    def generate_obj(self):
        # Generates an obj from the attractors

        verts = []
        for atractor in self.atractor_cloud:
            verts.append([atractor.x, atractor.y, atractor.z])
        return Object(verts, [])

class Tree:
    def __init__(self):
        self.verts = []
        self.edges = []
        self.faces = []
        self.atractors = []
        self.nodes = []
        self.prev_node_length = 0
        self.n_added_nodes = 1
        self.appending_nodes_indeces = []
        self.n_nodes = 0
        self.r_0 = 0.5
        self.obj = None
        self.segment_length = 0
    def clean_attractors(self):
        # Kills all of the attractors with an assoiciated node within kill distance

        for node in self.nodes:
            for atractor in self.atractors:
                if atractor.in_kill_distance(node):
                    self.atractors.remove(atractor)
    def assign_nodes_to_attractors(self):
        # Assigns each attractor with its closest node

        self.appending_nodes_indeces = []
        for atractor in self.atractors:
            min_dist = atractor.prev_distance
            prev_node = atractor.associated_node
            min_i = (self.nodes.index(prev_node)
                     if prev_node != None else 0)

            n_nodes = len(self.nodes)
            for i in range(n_nodes - self.n_added_nodes, n_nodes):
                if atractor.get_distance(self.nodes[i]) <= min_dist:
                    min_i = i
                    min_dist = atractor.get_distance(self.nodes[i])
                    atractor.set_node(self.nodes[i], min_dist)
            self.appending_nodes_indeces.append(min_i)
    def clean_directions(self):
        # Cleans all of the appending nodes' directions

        for i in self.appending_nodes_indeces:
            self.nodes[i].directions = []
    def set_directions(self):
        # Appends to the appending nodes its corresponding
        # directions to its associated attractors

        for atractor in self.atractors:
            direction = [atractor.x - atractor.associated_node.x,
                        atractor.y - atractor.associated_node.y,
                        atractor.z - atractor.associated_node.z]

            atractor.associated_node.directions.append(direction)
    def create_nodes(self, segment_length):
        # Consumes a segment length and produces a new layer of nodes
        # based on the directions to the attractors

        for i in self.appending_nodes_indeces:
            if len(self.nodes[i].directions) == 0:
                continue
            else:
                dir = self.nodes[i].get_average_direction()

                x = self.nodes[i].x + (dir[0] * segment_length)
                y = self.nodes[i].y + (dir[1] * segment_length)
                z = self.nodes[i].z + (dir[2] * segment_length)
                cycle = ((not self.nodes[i].prev_direction == None)
                         and (self.nodes[i].prev_direction[0] == dir[0]
                         and self.nodes[i].prev_direction[1] == dir[1]
                         and self.nodes[i].prev_direction[2] == dir[2]))
                self.nodes[i].prev_direction = dir
                if not cycle:
                    new_node = Node(x, y, z)
                    
                    new_node.children_nodes = self.nodes[i]
                    self.nodes[i].parent_nodes.append(new_node)

                    self.nodes.append(new_node)
    def generate_tree(self, segment_length, atractors) -> None:
        # Consumes a segment length and a list of attractors and generates
        # a tree using the Space Colonization algorithm

        self.verts = []
        self.nodes = [Node(0, 0, 0)]
        self.atractors = atractors
        self.n_added_nodes = 1
        self.appending_nodes_indeces = []
        self.segment_length = segment_length

        self.prev_node_length = len(self.nodes)
        while len(self.atractors) > 0:
            self.prev_node_length = len(self.nodes)
            self.clean_attractors()
            self.assign_nodes_to_attractors()
            self.clean_directions()
            self.set_directions()
            self.create_nodes(segment_length)
            if self.prev_node_length == len(self.nodes): break
            else: self.n_added_nodes = (len(self.nodes) - self.prev_node_length)
        self.n_nodes = len(self.nodes)
    def get_tree_obj_skeleton(self) -> Object:
        # Generates an obj transforming each node into a vertex

        self.verts = []
        for node in self.nodes:
            vert = [node.x, node.y, node.z]
            self.verts.append(vert)
        self.obj = Object(self.verts, [], [])
        return self.obj
    def generate_branches(self, node, prev_idxs) -> None:
        # Consumes a node and a list of previous indeces and
        # generates all branches starting from that node

        segment = [node]
        segment_positions = [[node.x, node.y, node.z]]
        # Sets the baseline refference frame to the standard basis in R^3
        prev_T = [0, 0, 1]
        prev_N = [1, 0, 0]
        prev_B = [0, 1, 0]

        if node.children_nodes != None:
            # Sets the baseline refference frame to that of the previous branch
            prev_T = node.children_nodes.T_vec
            prev_N = node.children_nodes.N_vec
            prev_B = node.children_nodes.B_vec
            segment = [node.children_nodes] + segment
            segment_positions = [[node.children_nodes.x,
                                 node.children_nodes.y,
                                 node.children_nodes.z]] + segment_positions

        # Creates an array containing all nodes up to a joint node
        cur_node = node
        while len(cur_node.parent_nodes) == 1:
            cur_node = cur_node.parent_nodes[0]
            segment.append(cur_node)
            segment_positions.append([cur_node.x, cur_node.y, cur_node.z])

        n = len(segment_positions)
        step = 1 / (n - 1)
        # Uses bsplines to generate a C^2 continuous curve along all points, including control points
        curve = generate_curve(segment_positions, b_spline)
        # Tangent curve
        T_curve = generate_curve(segment_positions, b_spline_deriv)
        prev_circ = prev_idxs
        
        for i in range(0, n):
            # Gets the new refference frame using the derivative of the curve
            T_vec, N_vec, B_vec = generate_frame(curve, T_curve, i * step,
                                                 prev_T, prev_N, prev_B)
            # Saves the refference frame for the next nodes
            prev_T = T_vec
            prev_N = N_vec
            prev_B = B_vec
            segment[i].T_vec = T_vec
            segment[i].N_vec = N_vec
            segment[i].B_vec = B_vec

            if i != 0:
                # Generate circle vertices
                circ = generate_circle(node.radius, N_vec, B_vec, 20, curve(i * step))
                self.verts.extend(circ)
                last_idx = len(self.verts)
                # Saves the indeces of the previus circle to connect them with the next one
                new_circ = []
                for j in range(0, 20):
                    # Builds the edges of a circle
                    self.edges.append([last_idx - j, last_idx - ((j + 1) % 20)])
                    # Connects the circle to the previous one to create the cylinder
                    if prev_circ != None:
                        self.edges.append([prev_circ[j], last_idx - j])
                        self.faces.append([last_idx - j, prev_circ[j],
                                    last_idx - ((j + 1) % 20)])
                        self.faces.append([prev_circ[j], prev_circ[(j + 1) % 20],
                                        last_idx - ((j + 1) % 20)])
                    new_circ.append(last_idx - j)
                prev_circ = new_circ
        
        # Generate the parent branches recursively
        for parent in cur_node.parent_nodes:
            self.generate_branches(parent, prev_circ)
    def set_radius(self, node) -> float:
        # Consumes a node and sets the radious for each node starting from that one

        # If the radius was not already set it sets it by getting the parents' radius
        if node.radius == None:
            r_sum = 0
            for parent in node.parent_nodes:
                self.set_radius(parent)
                r_sum += (parent.radius)**(2.5)
            r = r_sum**(1/2.5)
            node.radius = r
            return r
    def get_tree_obj_cylinders(self) -> Object:
        # Identify parent nodes
        self.verts = []
        self.edges = []
        self.faces = []
        
        # Set the minimum radius for the terminal nodes
        for node in self.nodes:
            if len(node.parent_nodes) == 0:
                node.radius = self.r_0
        
        # Set cylinder radiuses
        self.set_radius(self.nodes[0])
        # Generate branches
        self.generate_branches(self.nodes[0], None)

        self.obj = Object(self.verts, self.edges, self.faces)
        return self.obj
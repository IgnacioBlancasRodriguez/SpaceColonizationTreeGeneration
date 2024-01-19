import pygame as pg
import numpy as np
import math

class ThreeDimensionRenderer:
    def __init__(self):
        self.tr = np.array([
            [1, math.cos(0 + math.pi/2)*math.cos(0 + math.pi/2),
             math.cos(0 + math.pi/2)*math.cos(0 + math.pi)],
		[0, math.sin(0 + math.pi/2), math.sin(0 + math.pi)]])
    def update(self, alpha, beta, z):
        self.tr = np.array([
            [math.cos(beta), math.cos(beta + math.pi/2)*math.cos(alpha + math.pi/2),
             math.cos(beta + math.pi/2)*math.cos(alpha + math.pi)],
		[0, math.sin(alpha + math.pi/2), math.sin(alpha + math.pi)]])
        self.tr = self.tr * z

class RenderableObj:
    def __init__(self, obj, tr):
        self.vertices = obj.vertices
        self.projected_vertices = []
        self.edges = obj.edges
        self.faces = obj.faces
        for vert in obj.vertices:
            self.projected_vertices.append(np.matmul(tr, vert))
    def update_rotation(self, tr):
        self.projected_vertices = []
        for vert in self.vertices:
            self.projected_vertices.append(np.matmul(tr, vert))
    def drawPrimitive(self, surface, color):
        size = surface.get_size()
        for edge in self.edges:
            vertices = (self.projected_vertices[edge[0] - 1],
                        self.projected_vertices[edge[1] - 1])
            v0 = vertices[0]
            v1 = vertices[1]
            pg.draw.aaline(surface, color,
                            [v0[i] + size[i]/2 for i in range(0, 2)],
                            [v1[i] + size[i]/2 for i in range(0,2)])
    def drawVertex(self, surface, color):
        size = surface.get_size()
        for vert in self.projected_vertices:
            surface.set_at([int(vert[0] + size[0]/2),
                            int(vert[1] + size[1]/2)], color)

class Object:
    def __init__(self, vertices, edges, faces):
        self.vertices = vertices
        self.edges = edges
        self.faces = faces
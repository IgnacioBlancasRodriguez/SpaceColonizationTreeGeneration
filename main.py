import math
import pygame as pg
from TreeGenerator import AtractorCloud, Tree
from Renderer import ThreeDimensionRenderer, Object, RenderableObj
from UIFunctions import *
import ObjLib
import threading
import os
from datetime import datetime

pg.init()
pg.font.init()

pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN])

#Constants
WIDTH, HEIGHT = 1000, 1000
# Manages UI colors using a themeColors json file
themeColors = ThemeColors("themeColors.json")
LOADING_FONT = pg.font.SysFont("Arial", 20)

SPHERE_DOMAIN = AtractorCloud(
				[-100, 100],
				# Generates a circle of radius 100 in the xy-plane
				[lambda x: -math.sqrt(10000 - pow(x, 2)),
				lambda x: math.sqrt(10000 - pow(x, 2))],
				# Generates an ellipsoid that is slightly shorter on the z-axis
				[lambda x, y: 100 - math.sqrt(10000 - pow(x, 2) - pow(y, 2)) / 2,
				lambda x, y: 100 + math.sqrt(10000 - pow(x, 2) - pow(y, 2)) / 2])

TREE = Tree()
TREE_OBJ = RenderableObj(Object([], [], []), [])
TREE_CYLINDER = RenderableObj(Object([], [], []), [])

# Gives information about processes being executed in the backround
loading_text = ""

#UI
generate_tree_btn = Button(30, 80, 150, 50, "Generate tree")
segment_length_slider = Slider(10, 1, 150, 50, 0, 30, 20)
segment_length_label = Label("Segment legnth", 200, 20, 16,
							 "Arial", str(segment_length_slider.get_value()))
number_nodes_label = Label("Number of nodes", 200, 40, 16, "Arial", str(TREE.n_nodes))
export_object_btn = Button(30, 800, 175, 50, "Export cylinders")
cylinder_view_btn = Button(800, 20, 150, 50, "cylinder view")
node_view_btn = Button(800, 80, 150, 50, "node view")
view = True 	# If true it displays the cylinders, otherwise, it displays the skeleton

renderer = ThreeDimensionRenderer()
renderer.update(math.pi/2, 0, 1)

def generate_tree():
	# Modifies the state of data utilized in the main thread
	global TREE
	global TREE_OBJ
	global TREE_CYLINDER
	global loading_text

	loading_text = "Generating tree skeleton"
	TREE.generate_tree(segment_length_slider.get_value(), SPHERE_DOMAIN.generate_cloud(150, 600, 2))
	# Generated the skeleton of the tree using the space colonization algorithm
	TREE_OBJ = RenderableObj(TREE.get_tree_obj_skeleton(),
						  renderer.tr)
	loading_text = "Generating tree cylinders"
	TREE_CYLINDER = RenderableObj (TREE.get_tree_obj_cylinders(),
								renderer.tr)
	loading_text = ""

def export_tree(view):
	global loading_text
	
	cur_tree = TREE_CYLINDER if view else TREE_OBJ
	
	loading_text = "Generating obj"
	filename = "Tree-" + datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + ".obj"
	counter = 1
	while os.path.exists(filename):
		filename = "Tree-" + datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + counter + ".obj"
		counter += 1
	ObjLib.writeOjb(filename, cur_tree.vertices, cur_tree.edges, cur_tree.faces)
	loading_text = ""

w = pg.display.set_mode([WIDTH, HEIGHT])
pg.display.set_caption("Tree generator: Space colonization")

def main():
	clock = pg.time.Clock()								
	clock.tick(144)										#Adujust the frame rate
	t = 0												#Initialize time counter

	alpha = math.pi/2
	beta = 0
	m_pos = m_pos_back = m_pos_new = (0,0)				#Initialize the mouse position buffer
	zoom = 1

	global control_thread, view

	while 1:
		for event in pg.event.get():					#Handel user events
			if event.type == pg.QUIT:
				pg.quit()
				quit()
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_LEFT:
					beta -= math.pi/100
				if event.key == pg.K_RIGHT:
					beta += math.pi/100
				if event.key == pg.K_UP:
					alpha -= math.pi/100
				if event.key == pg.K_DOWN:
					alpha += math.pi/100
				if event.key == pg.K_PLUS and pg.key.get_mods() & pg.KMOD_CTRL:
					zoom += 0.05
					renderer.update(alpha, beta, zoom)
					TREE_OBJ.update_rotation(renderer.tr)
					TREE_CYLINDER.update_rotation(renderer.tr)
				if event.key == pg.K_MINUS and pg.key.get_mods() & pg.KMOD_CTRL:
					zoom -= 0.05
					renderer.update(alpha, beta, zoom)
					TREE_OBJ.update_rotation(renderer.tr)
					TREE_CYLINDER.update_rotation(renderer.tr)
			if event.type == pg.MOUSEBUTTONDOWN:
				mouse_position = pg.mouse.get_pos()
				if (generate_tree_btn.check_hover(mouse_position[0], mouse_position[1])
					and loading_text == ""):
					control_thread = threading.Thread(target=generate_tree, args=())
					control_thread.start()
				if (export_object_btn.check_hover(mouse_position[0], mouse_position[1])
					and loading_text == ""):
					export_tree(view)
				if cylinder_view_btn.check_hover(mouse_position[0], mouse_position[1]):
					view = True
				if node_view_btn.check_hover(mouse_position[0], mouse_position[1]):
					view = False
		if pg.mouse.get_pressed()[0]:
			mouse_position = pg.mouse.get_pos()
			if (segment_length_slider.isPressed == False and
				segment_length_slider.check_hover(mouse_position[0], mouse_position[1])):
				segment_length_slider.isPressed = True
			elif segment_length_slider.isPressed == True:
				segment_length_slider.update(mouse_position[0])
				segment_length_label.update_value(str(round(segment_length_slider.get_value(), 3)))
			else:
				if m_pos_new[0] != -1:
					m_pos_back = m_pos_new
					m_pos_new = mouse_position
					m_pos = (m_pos_back[0] - m_pos_new[0], m_pos_new[1] - m_pos_back[1])
					m_pos = ((m_pos[1]*(math.pi/1.5))/WIDTH, (m_pos[0]*(math.pi/1.5))/HEIGHT)

					alpha -= m_pos[0]								#Update alpha according to the mouse movement
					beta -= m_pos[1]								#Update beta according to the mouse movement
					renderer.update(alpha, beta, zoom)
					TREE_OBJ.update_rotation(renderer.tr)
					TREE_CYLINDER.update_rotation(renderer.tr)
				else:
					m_pos_new = mouse_position
					m_pos = (0,0)
		else:
			m_pos_new = (-1,-1)
			segment_length_slider.isPressed = False

		w.fill(themeColors.getColor("BACKGROUND"))							#Make the backround with black

		# Renderer scene
		if view:
			TREE_CYLINDER.drawPrimitive(w, themeColors.getColor("WHITE"))
		else:
			TREE_OBJ.drawVertex(w, themeColors.getColor("WHITE"))
		generate_tree_btn.render(w)
		export_object_btn.render(w)
		segment_length_slider.render(w)
		segment_length_label.render(w)
		number_nodes_label.update_value(str(TREE.n_nodes))
		number_nodes_label.render(w)
		cylinder_view_btn.render(w)
		node_view_btn.render(w)
		loading_text_surface = LOADING_FONT.render(loading_text, True, themeColors.getColor("WHITE"))
		w.blit(loading_text_surface,
		 ((WIDTH / 2) - (loading_text_surface.get_width() / 2), 600))

		pg.display.update()
		t += 1											#Update time counter with

if __name__ == "__main__":
	try:
		control_thread = threading.Thread(target=generate_tree, args=())
		control_thread.start()

		main()
		control_thread.join()
	except KeyboardInterrupt:
		pg.quit()
		quit()
def writeOjb(url, vertices, edges, faces):
    with open(url, "w") as file:
        file.write("# Tree generated using the space colonization algorithm\n")
        file.write("# Software by Nacho Blancas Rodriguez\n\n")
        for vert in vertices:
            file.write("v " + str(vert[0]) +
                       " " + str(vert[1]) + " " + str(vert[2]) + "\n")
        for edge in edges:
           file.write("l " + str(edge[0]) + " " + str(edge[1]) + "\n")
        for face in faces:
            verts = ""
            for v in face:
                verts += (str(v) + " ")
            file.write("f " + verts + "\n")
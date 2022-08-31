from turtle import position
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

from threading import Thread
from time import sleep

app = Ursina()

# Define a Voxel class.
# By setting the parent to scene and the model to 'cube' it becomes a 3d button.


def normalLookup(normal):
    # print("Normal check = ", normal)
    if normal == (0, 1, 0):
        return (0, -0.85, 0)
    if normal == (0, 0, -1):
        return (0, -0.5, 0.5)
    if normal == (-1, 0, 0):
        return (0.5, -0.5, 0)
    return (0, 0, 0)


def rotateOrientation(entity):
    # print("Orient", entity.world_rotation, entity.position)
    if entity.normalVal == (0, 1, 0):
        if entity.world_rotation == Vec3(0, 90, 0):
            entity.world_rotation = Vec3(0, 0, 0)
            return
        entity.world_rotation = Vec3(0, 90, 0)
    if entity.normalVal == (0, 0, -1):
        if entity.world_rotation == Vec3(0, 0, 90):
            entity.world_rotation = Vec3(0, 0, 0)
            return
        # entity.origin_x = .25
        entity.world_rotation = Vec3(0, 0, 90)
    if entity.normalVal == (-1, 0, 0):
        if entity.world_rotation == Vec3(0, 0, 90):
            entity.world_rotation = Vec3(90, 0, 90)
            return
        # entity.origin_x = .25
        entity.world_rotation = Vec3(0, 0, 90)
        # if entity.rotation_z == -90:
        #    entity.rotation_z = 0
        #    entity.origin_x = 0
        #    return
        # entity.rotation_z = -90
        # entity.origin_x = 0.25


def setWallOrientation(entity, normal):
    if entity.normalVal == normal:
        return
    entity.normalVal = normal
    rotateOrientation(entity)


class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='texture_test',
            color=color.color(0, 0, 0.5),
            shader=lit_with_shadows_shader
        )

    # def input(self, key):
    #     if self.hovered:
    #         if key == 'left mouse down':
    #             voxel = Voxel(position=self.position + mouse.normal)
    #
    #         if key == 'right mouse down':
    #             destroy(self)


class Wire(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            name="straight_wire",
            # origin_y=5.25,
            scale=(1, 0.2, 0.2),
            color=color.rgba(94, 159, 209, 255),
            highlight_color=color.rgba(58, 104, 140, 255),
            shader=lit_with_shadows_shader
        )


width = 16
length = 16
height = 8

for z in range(width):
    for x in range(length):
        voxel = Voxel(position=(x, 0, z))

for x in range(width):
    for y in range(height):
        voxel = Voxel(position=(x, y+1, 0))
        voxel = Voxel(position=(0, y+1, x))
        voxel = Voxel(position=(width, y+1, x))
        voxel = Voxel(position=(x, y+1, width))

for z in range(width):
    for x in range(length):
        if x >= 5 and x <= 8:
            voxel = Voxel(position=(x, height, z))


selectedPart = None
inDrag = 0


def updateDragState():
    global inDrag
    if inDrag > 50:
        inDrag = 0
    inDrag += 1
    return inDrag


def update():
    curDrag = updateDragState()
    lastHit = None

    if curDrag == inDrag:
        hit_info = raycast(camera.world_position, camera.forward, distance=15)

        # print("Trying move", selectedPart, hit_info)

        # if not selectedPart:
        #    print("No selected")
        #    break

        validNormal = '0.707' not in str(hit_info.normal)

        if (selectedPart and hasattr(hit_info.entity, 'position') and lastHit != hit_info.entity and validNormal):
            lastHit = hit_info.entity
            if (hit_info.entity.position != selectedPart.position):
                # print("MOVING WITH NORMAL", str(hit_info.normal))
                # selectedPart.animate(
                #    'position', hit_info.entity.position + hit_info.normal, duration=0.25, curve=curve.linear)
                selectedPart.position = hit_info.entity.position + \
                    hit_info.normal + \
                    normalLookup(hit_info.normal)  # (0, -0.75, 0)
                setWallOrientation(selectedPart, hit_info.normal)


def input(key):
    global selectedPart
    global inDrag
    # print("key=", key)
    if key == "escape":
        application.quit()
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=15)
        if (hasattr(hit_info.entity, 'name') and hit_info.entity.name == "straight_wire"):
            selectedPart = hit_info.entity
            #thrd = Thread(target=dragFunction)
            # thrd.start()
            # print("Selected part created")
            return
        if hit_info.hit:
            w = Wire(position=hit_info.entity.position + hit_info.normal)
            w.normalVal = hit_info.normal
            setWallOrientation(w, hit_info.normal)
            w.position = hit_info.entity.position + \
                hit_info.normal + \
                normalLookup(hit_info.normal)  # (0, -0.75, 0)
    if key == 'left mouse up':
        # print("Selected part removed")
        updateDragState()
        selectedPart = None
    if key == 'r':
        if selectedPart:
            rotateOrientation(selectedPart)
            # selectedPart.rotation_y += 90


player = FirstPersonController()
player.position = (10, 10, 10)
app.run()

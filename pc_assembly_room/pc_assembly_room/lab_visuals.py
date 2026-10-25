"""Local procedural surfaces and lighting. No external assets or dependencies."""
import math
import random
from panda3d.core import (Texture,PNMImage,GeomVertexData,GeomVertexFormat,GeomVertexWriter,
    BitMask32,Material,AmbientLight,DirectionalLight,PointLight,LineSegs)
from .scene import make_box

def surface_box(size,color,texture=None):
    node=make_box('lab_surface',size,color)
    if texture is not None:
        geom=node.modify_geom(0)
        data=GeomVertexData(geom.get_vertex_data().convert_to(GeomVertexFormat.get_v3n3c4t2()))
        writer=GeomVertexWriter(data,'texcoord')
        for face in range(6):
            for uv in ((0,0),(1,0),(1,1),(0,1)):writer.add_data2(*uv)
        geom.set_vertex_data(data)
    return node

def stone_texture():
    rng=random.Random(2701)
    image=PNMImage(256,256,3)
    for y in range(256):
        for x in range(256):
            noise=rng.uniform(-.012,.012)
            cloud=.006*math.sin(x*.08+y*.035)+.004*math.cos(y*.13)
            value=.80+noise+cloud
            image.set_xel(x,y,value,value*1.015,value*1.035)
    texture=Texture('brushed_stone');texture.load(image)
    texture.set_minfilter(Texture.FT_linear_mipmap_linear)
    texture.set_magfilter(Texture.FT_linear)
    return texture

def technical_texture():
    image=PNMImage(512,256,3);image.fill(.035,.075,.13)
    def line(x0,y0,x1,y1,color=(.15,.48,.70)):
        steps=max(abs(x1-x0),abs(y1-y0),1)
        for i in range(steps+1):
            x=round(x0+(x1-x0)*i/steps);y=round(y0+(y1-y0)*i/steps)
            if 0<=x<512 and 0<=y<256:image.set_xel(x,y,*color)
    def rect(x,y,w,h):
        line(x,y,x+w,y);line(x+w,y,x+w,y+h);line(x+w,y+h,x,y+h);line(x,y+h,x,y)
    for x in range(0,512,16):line(x,0,x,255,(.045,.10,.16))
    for y in range(0,256,16):line(0,y,511,y,(.045,.10,.16))
    rect(185,35,140,185);rect(197,46,116,161);rect(235,76,38,38)
    for x in (205,212,219):rect(x,65,4,85)
    for y in (155,171,185):rect(235,y,55,6)
    for y in (65,115,175):
        rect(35,y,65,30);line(100,y+15,150,y+15);line(150,y+15,185,y+30)
        rect(395,y,75,30);line(325,y+15,395,y+15)
    texture=Texture('technical_board');texture.load(image)
    return texture

def material(name,shine=24,color=(1,1,1,1)):
    m=Material(name);m.set_diffuse(color);m.set_ambient(color)
    m.set_specular((.28,.30,.33,1));m.set_shininess(shine)
    return m

def setup_lights(root,render):
    ambient=AmbientLight('lab_ambient');ambient.set_color((.55,.57,.62,1))
    root.set_light(root.attach_new_node(ambient))
    for name,h,p,color in [('key',-35,-65,(.70,.68,.64,1)),('fill',140,-35,(.28,.34,.42,1))]:
        light=DirectionalLight(name);light.set_color(color)
        np=root.attach_new_node(light);np.set_hpr(h,p,0);root.set_light(np)
    # Conventional lighting avoids driver-specific shader requirements.
    for x in (-3.1,3.1):
        light=PointLight('blue_accent');light.set_color((.015,.10,.30,1))
        light.set_attenuation((1,0,.8));np=root.attach_new_node(light);np.set_pos(x,4.5,1)
        root.set_light(np)

def wire_box(size):
    hx,hy,hz=(v/2 for v in size)
    vertices=[(x,y,z) for x in (-hx,hx) for y in (-hy,hy) for z in (-hz,hz)]
    lines=LineSegs('socket_outline');lines.set_thickness(2.5);lines.set_color(1,1,1,1)
    for i,a in enumerate(vertices):
        for b in vertices[i+1:]:
            if sum(a[k]!=b[k] for k in range(3))==1:lines.move_to(*a);lines.draw_to(*b)
    return lines.create()

import cadquery as cq
from cq_warehouse.thread import IsoThread
import cq_warehouse.extensions


cq.Workplane.tryfillet = lambda self,edge,fillet: self if fillet == 0 else self.edges(edge).fillet(fillet)
cq.Workplane.stack = lambda self,item: self.add(
    item.translate([0,0,self.combine().val().BoundingBox().zmax])
).combine()
cq.Workplane.slicex = lambda self,offset=0: self.cut(
    cq.Workplane().box(
        (abs(self.combine().val().BoundingBox().xmax)+abs(self.combine().val().BoundingBox().xmin))*3,
        (abs(self.combine().val().BoundingBox().ymax)+abs(self.combine().val().BoundingBox().ymin))*3,
        (abs(self.combine().val().BoundingBox().zmax)+abs(self.combine().val().BoundingBox().zmin))*3,
        centered=[False,True,True]
    ).translate([offset,0,0])
)
cq.Workplane.slicey = lambda self,offset=0: self.cut(
    cq.Workplane().box(
        (abs(self.combine().val().BoundingBox().xmax)+abs(self.combine().val().BoundingBox().xmin))*3,
        (abs(self.combine().val().BoundingBox().ymax)+abs(self.combine().val().BoundingBox().ymin))*3,
        (abs(self.combine().val().BoundingBox().zmax)+abs(self.combine().val().BoundingBox().zmin))*3,
        centered=[True,False,True]
    ).translate([0,offset,0])
)




def cylinder(diameter,height):
    return cq.Workplane().cylinder(
        height,diameter/2,[0,0,1],centered=[True,True,False]
    )

def tube(outer_diameter,wall_thickness,height):
    return cylinder(outer_diameter,height).cut(
        cylinder(outer_diameter-wall_thickness*2,height)
    )




def threadedCylinder(diameter,height,pitch):
    show_threads = 'thread'
    #show_threads = 'core'
    #show_threads = 'fill'
    thread = IsoThread(diameter,pitch,height)
    core = cylinder(thread.min_radius * 2, height)
    print(f"Die M{diameter}x{pitch} core_diameter={thread.min_radius * 2}")
    if show_threads == 'thread':
        return core.add(thread).combine().rotateAboutCenter([0,0,1],-90)
    elif show_threads == 'core':
        return core
    else:
        return cylinder(diameter,height)
        

def threadedTube(outer_diameter,height,inner_diameter,pitch):
    show_threads = 'thread'
    #show_threads = 'core'
    #show_threads = 'fill'
    thread = IsoThread(inner_diameter,pitch,height,external=False)
    core = cylinder(outer_diameter,height).cut(
        cylinder(inner_diameter,height)
    )
    print(f"Tap M{inner_diameter}x{pitch} drill_diameter={thread.min_radius * 2}")
    if show_threads == 'thread':
        if outer_diameter == inner_diameter:
            return thread
        else:
            return core.add(thread).combine().rotateAboutCenter([0,0,1],90)
    elif show_threads == 'core':
        if outer_diameter == inner_diameter:
            return cq.Workplane()
        else:       
            return core
    else:
        return tube(
            outer_diameter = outer_diameter,
            wall_thickness = outer_diameter/2 - thread.min_radius,
            height = height
        )


def polygon(sides,diameter,height):
    return cq.Workplane().polygon(
        sides,diameter
    ).extrude(
        height
    )

def box(length,width,height):
    return cq.Workplane().box(length, width, height, centered=[True,True,False])

def roundedBox(length,width,height,corner_radius):
    inner_length = length - corner_radius*2
    inner_width = width - corner_radius*2
    wp = cq.Workplane()
    if inner_length == 0 and inner_width == 0:
        wp = wp.add(
            cylinder(corner_radius*2,height)
        )
    elif inner_length == 0:
        wp = wp.add(
            box(
                length = length,
                width = inner_width,
                height = height
            )
        ).add(
            cylinder(corner_radius*2,height).translate(
                [0,inner_width/2,0]
            )
        ).add(
            cylinder(corner_radius*2,height).translate(
                [0,-1*inner_width/2,0]
            )
        )
    elif inner_width == 0:
        wp = wp.add(
            box(
                length = inner_length,
                width = width,
                height = height
            )
        ).add(
            cylinder(corner_radius*2,height).translate(
                [inner_length/2,0,0]
            )
        ).add(
            cylinder(corner_radius*2,height).translate(
                [-1*inner_length/2,0,0]
            )
        )
    else:
        wp = wp.box(
            length, width, height, centered=[True,True,False]
        ).tryfillet(
            "|Z", corner_radius
        )
    return wp
    

original_lip = True
#original_lip = False

plug_thread_height = 5
plug_cap_diameter = 26
plug_cap_height = 3
plug_cap_oring_outer_diameter = 22.4
plug_cap_oring_width = 2.5
plug_cap_oring_depth = 1.5
plug_hex_cap_height = 6
valve_base_height = 5
valve_base_diameter = 22
valve_base_oring_width = 2
valve_base_oring_depth = 0.95
valve_base_oring_offset = 1.5
valve_thread_height = 4 if original_lip else 4
valve_thread_diameter = 21
valve_thread_pitch = 1

valve_face_recess = 2 if original_lip else 4.5
valve_face_inner_diameter = 18
valve_face_lip_thickness = 0.8
valve_face_lip_height = 0.5 if original_lip else 1           
valve_face_thickness = 8

#air_hole_face_diameter = 1
#air_hole_core_diameter = 3
air_hole_face_diameter = 1.5
air_hole_core_diameter = 1.5
air_hole_offset = 5.25
usb_hole_face_length = 3.5
usb_hole_face_width = 9.5
usb_hole_face_corner = 1.5
usb_hole_inner_length = 6
usb_hole_inner_width = 12.2

insert_air_tube_thickness = 0.5
insert_base_height = 2

outer_cap_diameter = 26
outer_cap_thread_offset = 1
outer_cap_height = 18
outer_cap_top_thickness = 2
outer_cap_valve_clearance = 0.3

outer_cap_grip_height = 8
outer_cap_grip_diameter = 20
outer_cap_grip_depth = 1     
outer_cap_grip_grooves = 8
outer_cap_top_chamfer = 0.5
outer_cap_bottom_inner_chamfer_base = 0.5
outer_cap_bottom_inner_chamfer_height = 1



plug_thread = threadedCylinder(
    diameter = 16,
    height = plug_thread_height,
    pitch = 1
)
plug_cap = cylinder(
    diameter = plug_cap_diameter,
    height = plug_cap_height
).cut(
    tube(
        outer_diameter = plug_cap_oring_outer_diameter,
        wall_thickness = plug_cap_oring_width,
        height = plug_cap_oring_depth
    )
)
plug_hex_cap = polygon(
    sides = 6,
    diameter = plug_cap_diameter      ,
    height = plug_hex_cap_height
)
valve_base = cylinder(
    diameter = valve_base_diameter,
    height = valve_base_height
).cut(
    tube(
        outer_diameter = valve_base_diameter,
        wall_thickness = valve_base_oring_depth,
        height = valve_base_oring_width
    ).translate(
        [0,0,valve_base_oring_offset]
    )
)
valve_thread = threadedCylinder(
    diameter = valve_thread_diameter,
    height = valve_thread_height,
    pitch = valve_thread_pitch
)
valve_lip = cylinder(
    diameter = valve_face_inner_diameter + 2*valve_face_lip_thickness,
    height = valve_face_lip_height
)


plug_oring_groove_inside = plug_cap_oring_outer_diameter-2*plug_cap_oring_width
plug_oring_groove_outside = plug_cap_oring_outer_diameter
plug_oring_groove_depth = plug_cap_oring_depth
print(f"Plug O-Ring Groove Outside: {plug_oring_groove_inside}")
print(f"Plug O-Ring Groove Inside: {plug_oring_groove_outside}")
print(f"Plug O-Ring Groove Depth: {plug_oring_groove_depth}")
# Plug O-Ring 21mm OD, 17mm ID, 2mm Width
# https://ceetak.com/o-ring-calculator/
# https://www.amazon.com/uxcell-Rings-Nitrile-Rubber-Diameter/dp/B07GJL9JK5?th=1

valve_oring_bore_diameter = valve_base_diameter + 2*outer_cap_valve_clearance
valve_oring_piston_diameter = valve_base_diameter
valve_oring_groove_diameter = valve_base_diameter - 2*valve_base_oring_depth
valve_oring_groove_width = valve_base_oring_width
print(f"Valve O-Ring Bore Diameter: {valve_oring_bore_diameter}")
print(f"Valve O-Ring Piston Diameter: {valve_oring_piston_diameter}")
print(f"Valve O-Ring Groove Diameter: {valve_oring_groove_diameter}")
print(f"Valve O-Ring Groove Width: {valve_oring_groove_width}")
# Valve O-Ring 22mm OD, 19mm ID, 1.5mm Width
# https://ceetak.com/o-ring-calculator/
# https://www.amazon.com/dp/B00AFX1JCU?th=1


full_stack_height = (    
    plug_thread_height +
    plug_cap_height +
    plug_hex_cap_height +
    valve_base_height +
    valve_thread_height +
    valve_face_lip_height
)
center_hole_height = full_stack_height-valve_face_recess-valve_face_thickness
full_stack_with_cap_height = (    
    plug_thread_height +
    plug_cap_height +
    plug_hex_cap_height +
    outer_cap_height
)

base_cone_height = plug_thread_height + plug_cap_height
mid_cone_height = plug_hex_cap_height + valve_base_oring_offset + valve_base_oring_width 
top_cone_height = valve_base_height-valve_base_oring_offset-valve_base_oring_width+valve_thread_height+valve_face_lip_height




print(f"Full Stack With Cap Height: {full_stack_with_cap_height}")
print(f"Full Stack Height: {full_stack_height}")
print(f"Center Hole Height: {center_hole_height}")
print(f"3D Print Base Section Height: {base_cone_height} Offset: {0}")
print(f"3D Print Mid Section Height: {mid_cone_height} Offset: {base_cone_height}")
print(f"3D Print Top Section Height: {top_cone_height} Offset: {base_cone_height+mid_cone_height}")

valve_recess_hole = cq.Workplane().add(
    cylinder(
        diameter = valve_face_inner_diameter,
        height = valve_face_recess        
    )
).translate(
    [0,0,full_stack_height-valve_face_recess]
)

face_holes = cq.Workplane().add(
    cylinder(
            diameter = air_hole_face_diameter,
            height = valve_face_thickness
    ).translate(
        [air_hole_offset,0,0]
    )
).add(
    cylinder(
            diameter = air_hole_face_diameter,
            height = valve_face_thickness
    ).translate(
        [-1*air_hole_offset,0,0]
    )
).add(
    roundedBox(
        length = usb_hole_face_length,
        width = usb_hole_face_width,
        height = valve_face_thickness,
        corner_radius = usb_hole_face_corner
    )
).translate(
    [0,0,center_hole_height]
)

center_holes = cq.Workplane().add(
    cylinder(
            diameter = air_hole_core_diameter,
            height = center_hole_height
    ).translate(
        [air_hole_offset,0,0]
    )
).add(
    cylinder(
            diameter = air_hole_core_diameter,
            height = center_hole_height
    ).translate(
        [-1*air_hole_offset,0,0]
    )
).add(
    roundedBox(
        length = usb_hole_inner_length,
        width = usb_hole_inner_width,
        height = center_hole_height,
        corner_radius = usb_hole_inner_length/2
    )
)




vacuum_valve_shell = cq.Workplane("XY").add(
    plug_thread
).stack(
    plug_cap
).stack(
    plug_hex_cap
).stack(
    valve_base
).stack(
    valve_thread
).stack(
    valve_lip
).cut(
    valve_recess_hole
).cut(
    face_holes
).cut(
    center_holes
).combine()

outer_cap_bore = valve_base_diameter + 2*outer_cap_valve_clearance
outer_cap_base = cq.Workplane().add(
    tube(
        outer_diameter = outer_cap_diameter,
        wall_thickness = (outer_cap_diameter - outer_cap_bore)/2,
        height = valve_base_height + outer_cap_thread_offset
    )        
)
outer_cap_thread = cq.Workplane().add(
    threadedTube(
        outer_diameter = outer_cap_diameter,
        height = outer_cap_height - outer_cap_top_thickness - outer_cap_thread_offset - valve_base_height,
        inner_diameter = valve_thread_diameter,
        pitch = valve_thread_pitch
    )
)
outer_cap_top = cq.Workplane().add(
    cylinder(
        diameter = outer_cap_diameter,
        height = outer_cap_top_thickness
    )
)
outer_cap_grip = cq.Workplane().polygon(
    outer_cap_grip_grooves,outer_cap_diameter+outer_cap_grip_diameter-2*outer_cap_grip_depth
).vertices().cylinder(
    outer_cap_grip_height,outer_cap_grip_diameter/2,[0,0,1],centered=[True,True,False]
).translate(
    [0,0,full_stack_with_cap_height-outer_cap_grip_height]
)

outer_cap = cq.Workplane().add(
    outer_cap_base
).stack(
    outer_cap_thread
).stack(
    outer_cap_top
).translate(
    [0,0,plug_thread_height+plug_cap_height+plug_hex_cap_height]
).cut(
    outer_cap_grip
).faces('>Z').chamfer(
    outer_cap_top_chamfer
).faces('<Z').edges()[1].chamfer(
    outer_cap_bottom_inner_chamfer_base,
    outer_cap_bottom_inner_chamfer_height
).combine()






usbc_head_length = 3.16
usbc_head_width = 8.94
usbc_head_height = 9.3
usbc_head_corner = 1.3
usbc_pcb_length = 0.7
usbc_pcb_width = 9.5
usbc_module_height = 29.8
usbc_board_bottom_protrusion = 4 if original_lip else 6
usbc_module_mag_cap_width = 12
usbc_module_mag_cap_height = 5.2


usbc_module = cq.Workplane().add(
    roundedBox(
        length = usbc_head_length,
        width = usbc_head_width,
        height = usbc_head_height,
        corner_radius = usbc_head_corner
    )
).stack(
    box(
        length = usbc_pcb_length,
        width = usbc_pcb_width,
        height = usbc_module_height - (2*usbc_head_height)
    )
).stack(
    roundedBox(
        length = usbc_head_length,
        width = usbc_head_width,
        height = usbc_head_height,
        corner_radius = usbc_head_corner
    )
)

"""
usbc_module = usbc_module.stack(
    cylinder(
        diameter = usbc_module_mag_cap_width,
        height = usbc_module_mag_cap_height
    )
)
"""

usbc_module = usbc_module.combine().translate(
        [0,0,-1*usbc_board_bottom_protrusion]
)

print(f"USB-C Module Height: {usbc_module_height}")



flap_base_thickness = 0.8
flap_base_clearance = 0.5
flap_base_edge_trim = 0.75
flap_rim_width = 1.5
flap_rim_clearance = 0.2
flap_rim_thickness = 2.5
flap_rim_squeeze = 0.2

flap_base_diameter = valve_face_inner_diameter - flap_base_clearance*2
flap = cq.Workplane().add(
    cylinder(
            diameter = flap_base_diameter,
            height = flap_base_thickness
    )   
).cut(
    box(
        length = flap_base_diameter,
        width = flap_base_diameter,
        height = flap_base_thickness
    ).translate(
        [flap_base_diameter-flap_base_edge_trim,0,0]
    )
).cut(
    box(
        length = flap_base_diameter,
        width = flap_base_diameter,
        height = flap_base_thickness
    ).translate(
        [-1*(flap_base_diameter-flap_base_edge_trim),0,0]
    )
).cut(
    roundedBox(
        length = usbc_head_length+2*flap_rim_clearance,
        width = usbc_head_width+2*flap_rim_clearance,
        height = flap_base_thickness,
        corner_radius = usbc_head_corner+flap_rim_clearance
    )    
).stack(
    roundedBox(
        length = usbc_head_length+2*flap_rim_width,
        width = usbc_head_width+2*flap_rim_width,
        height = flap_rim_thickness,
        corner_radius = usbc_head_corner+flap_rim_width
    ).cut(
        roundedBox(
            length = usbc_head_length-2*flap_rim_squeeze,
            width = usbc_head_width-2*flap_rim_squeeze,
            height = flap_rim_thickness,
            corner_radius = usbc_head_corner-flap_rim_squeeze
        )    
    ).combine().faces('<Z').edges()[-1].chamfer(
        flap_rim_squeeze+flap_rim_clearance,
        (flap_rim_squeeze+flap_rim_clearance) *2
    )
)


mold_base_thickness = 2
mold_edge_width = 2
mold = cq.Workplane().add(
    cylinder(
        diameter = flap_base_diameter+2*mold_edge_width,
        height = flap_rim_thickness+flap_base_thickness+mold_base_thickness
    )   
).cut(
    flap
)


flap = flap.translate(
    [0,0,full_stack_height-valve_face_recess]
).combine()


brace_outer_clearance = 0.2
brace_magnet_diameter = 3
brace_magnet_height = 3
brace_magnet_offset = 4
brace_magnet_clearance = 0.2
brace_magnet_vertical_offset = 0.6
brace_magnet_inset = 1
brace_wall_width = 2
brace_thickness = 2
brace_connector_clearance = 0.2

def make_magnet_line(magnet_diameter):
    return cq.Workplane().add(
        cylinder(
                diameter = magnet_diameter,
                height = brace_magnet_height
        ).translate(
            [0,0,0]
        )
    ).add(
        cylinder(
                diameter = magnet_diameter,
                height = brace_magnet_height
        ).translate(
            [0,brace_magnet_offset,0]
        )
    ).add(
        cylinder(
                diameter = magnet_diameter,
                height = brace_magnet_height
        ).translate(
            [0,-brace_magnet_offset,0]
        )
    )





gap_inner_diameter = valve_face_inner_diameter - 1
gap_outer_diameter = valve_face_inner_diameter + 2*valve_face_lip_thickness + 2.8
lip_recess_height = 1
base_inner_height = 7
base_plate_height = 2
base_outer_height = base_inner_height + base_plate_height
top_straight_height = 5
top_taper_height = 5
top_total_height = top_straight_height + top_taper_height

valve_face_center_diameter = valve_face_inner_diameter + valve_face_lip_thickness
pump_adapter_lip_wall_thickness = 0.8
pump_adapter = cq.Workplane().add(
    cylinder(
        diameter = gap_outer_diameter + 2*pump_adapter_lip_wall_thickness,
        height = base_inner_height + base_plate_height
    )
).cut(
    tube(
        outer_diameter = gap_outer_diameter,
        wall_thickness = (gap_outer_diameter - gap_inner_diameter)/2,
        height = lip_recess_height
    )
).cut(
    cylinder(
        diameter = gap_inner_diameter - 2*pump_adapter_lip_wall_thickness,
        height = base_inner_height
    )
).add(
    cylinder(
        diameter = 13,
        height = top_straight_height
    ).translate(
        [0,0,base_outer_height]
    )
).add(
    cq.Solid.makeCone(
        13/2, 
        11/2, 
        top_taper_height
    ).translate(
        [0,0,base_outer_height+top_straight_height]
    )
).cut(
    cylinder(
        diameter = 9,
        height = base_outer_height + top_total_height
    )
).combine().translate(
    [0,0,full_stack_height]
)

#show_object(pump_adapter, options={"color": "yellow", "alpha": 0.5})


#show_object(mold)

show_object(flap, options={"color": "purple", "alpha": 0.5})
#show_object(brace, options={"color": "blue", "alpha": 0.75}) 
#show_object(magnet_array, options={"color": "lightblue", "alpha": 1}) 

show_object(vacuum_valve_shell, options={"color": "grey"})
#show_object(vacuum_valve_shell.slicex(), options={"color": "grey"})
#show_object(outer_cap, options={"color": "lightgrey"})
show_object(outer_cap.slicex(), options={"color": "lightgrey"})
show_object(usbc_module, options={"color": "green", "alpha": 0.5})



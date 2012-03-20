#! /usr/bin/python

import math, cmath

# All dimensions in millimetres.
A = 27.6
B = math.sqrt(2*A*A)

deg45 = math.pi / 4

page_offset = complex(6 * 25.4, -4 * 25.4)
no_offset = complex(0, 0)

inner_distance = A * 0.45
outer_distance = A * 0.80

# Distance of border away from holes.
border_standoff = 4

# print "inner_distance=", inner_distance
# print "outer_distance=", outer_distance

# Use cosine law to calculate distance between inner and outer hole.
inner_to_outer_distance = math.sqrt(inner_distance * inner_distance + outer_distance * outer_distance - 2 * inner_distance * outer_distance * math.cos(math.radians(11.25)))
# print "inner_to_outer_distance=", inner_to_outer_distance

# Use sine law to calculate angle between line from centre through inner, and inner to outer.
outer_angle = math.radians(11.25)
# print "outer_angle=", math.degrees(outer_angle), "math.sin(outer_angle)=", math.sin(math.radians(11.25))
centre_inner_outer_angle = math.asin(outer_distance * math.sin(outer_angle) / inner_to_outer_distance)
# print "centre_inner_outer_angle=", math.degrees(centre_inner_outer_angle)
inner_to_outer_deviation_angle = math.pi - centre_inner_outer_angle
# print "inner_to_outer_deviation_angle=", math.degrees(inner_to_outer_deviation_angle)
# assert 1==0

segments = 0

def point_to_kicad(p, origin=page_offset):

    """ Convert a point in mm to a string in thousandths of an inch """
    offset_p = p + origin
    return "%d %d" % (int((offset_p.real / 25.4) * 10000), -int((offset_p.imag / 25.4) * 10000))

def emit_border(f):
    global segments

    # Start from the 3 o'clock position
    prev = cmath.rect(B, 0)
    # Calculate the position of the next point
    odd_point = complex(A, -A + B)
    odd_len = abs(odd_point)
    
    # print "odd_point=", odd_point, "odd_len=", odd_len
    # assert 1 == 0
    for p in xrange(1, 17):
        if p % 2 == 0:
            next = cmath.rect(B, p * deg45 / 2)
        else:
            next = cmath.rect(odd_len, p * deg45 / 2)
        # print "p=", p, "prev=", prev, "next=", next
        # print "p=", p, "prev=", point_to_kicad(prev), "next=", point_to_kicad(next)
        print >>f, "$DRAWSEGMENT\nPo 0 %s %s 150\nDe 28 0 900 0 0\n$EndDRAWSEGMENT" % (point_to_kicad(prev), point_to_kicad(next))
        segments = segments + 1
    
        prev = next

    # Draw inner circle
    middle = complex(0, 0)
    threeoclock = complex(A * 0.24, 0)
    segments = segments + 1
    print >>f, \
"""$DRAWSEGMENT
Po 3 %s %s 150w
De 28 0 900 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(middle), point_to_kicad(threeoclock))

def emit_mounting_holes(f):
    for p in xrange(0, 8):
        hole = cmath.rect(B * 0.81, p * deg45)
# T0 0 -1600 400 400 0 100 N V 21 N "P%d"
        print >>f, \
"""$MODULE mounting-hole
Po %s 0 15 00200000 4F58C9C0 ~~
Li mounting-hole
Cd Mounting hole
Kw DEV
Sc 4F58C9C0
AR /4F58C8C9
Op 0 0 0
T0 0 -1600 400 400 0 100 N V 21 N ""
T1 0 1100 400 400 0 100 N I 21 N ""
DC 0 0 1000 900 150 21
$PAD
Sh "1" C 2350 2350 0 0 0
Dr 1320 0 0
At STD N 00E0FFFF
Ne 0 ""
Po 0 0
$EndPAD
$EndMODULE  mounting-hole""" % point_to_kicad(hole)

def emit_group(f, group):
    global segments
    # print "group=", group, "about to do inner hole and symbol"
    angle_from_centre_to_inner_hole = (group + 0.5) * deg45
    innerhole = cmath.rect(inner_distance, angle_from_centre_to_inner_hole)
    symbol = cmath.rect(abs(innerhole) * 1.45, cmath.phase(innerhole))
    symboldiff = symbol - innerhole
    if group % 2 == 0:
        part = group * 3 + 1
        sign = "+"
        net = '1 "N-000001"'
    else:
        part = group * 3 + 1
        sign = "-"
        net = '2 "N-000009"'
# T0 0 -1600 400 400 0 100 N V 21 N ""
# DC 0 0 1000 800 150 21
    print >>f, \
"""$MODULE power-hole
Po %s 0 15 00200000 4F58C9C4 ~~
Li power-hole
Cd Input/Output hole
Kw DEV
Sc 4F58C9C4
AR /4F583B52
Op 0 0 0
T0 0 0 400 400 0 100 N V 21 N "P%d"
T1 %s 1000 1000 0 250 N I 21 N "%s",
$PAD
Sh "1" C 2200 2400 0 0 0
Dr 1000 0 0
At STD N 00E0FFFF
Ne %s
Po 0 0
$EndPAD
$EndMODULE  power-hole""" % \
(point_to_kicad(innerhole), part, point_to_kicad(symboldiff, no_offset), sign, net)

    outerhole = {}
    for outerholeid in range(0, 2):
        outerpart = part + outerholeid + 1
        # print "group=", group, "part=", part, "outerholeid=", outerholeid, "outerpart=", outerpart, "about to do an outer hole"
        angle = (group * 2 + outerholeid + 0.5) * deg45 / 2
        # print "angle=", math.degrees(angle)
        outerhole[outerholeid] = cmath.rect(outer_distance, angle)

        # symbol = cmath.rect(abs(hole) * 1.25, cmath.phase(hole))
        # symboldiff = symbol - hole
# T0 0 -1600 400 400 0 100 N V 21 N "%s"
# T1 %s 1000 1000 0 100 N I 21 N "%s"
# DC 0 0 1100 800 150 21
        print >>f, \
"""$MODULE power-hole
Po %s 0 15 00200000 4F58C9C4 ~~
Li power-hole
Cd Input/Output hole
Kw DEV
Sc 4F58C9C4
AR /4F583B52
Op 0 0 0
T0 0 0 400 400 0 100 N V 21 N "P%d"
$PAD
Sh "1" C 2400 2400 0 0 0
Dr 1000 0 0
At STD N 00E0FFFF
Ne %s
Po 0 0
$EndPAD
$EndMODULE  power-hole""" % (point_to_kicad(outerhole[outerholeid]), outerpart, net)
 
    # Calculate points needed for inner arc
    # print "angle_from_centre_to_inner_hole=", math.degrees(angle_from_centre_to_inner_hole)
    angle_from_inner_hole_to_start_of_inner_arc = angle_from_centre_to_inner_hole - math.radians(120)
    angle_from_inner_hole_to_end_of_inner_arc = angle_from_centre_to_inner_hole + math.radians(120)
    # print "angle_from_inner_hole_to_start_of_inner_arc=", math.degrees(angle_from_inner_hole_to_start_of_inner_arc)
    vector_to_inner_arc_start = cmath.rect(border_standoff, angle_from_inner_hole_to_start_of_inner_arc)
    vector_to_inner_arc_end = cmath.rect(border_standoff, angle_from_inner_hole_to_end_of_inner_arc)
    inner_arc_start = innerhole + vector_to_inner_arc_start
    inner_arc_end = innerhole + vector_to_inner_arc_end

    # print "vector_to_inner_arc_start=", vector_to_inner_arc_start
    # print "inner_arc_start=", inner_arc_start

    print >>f, \
"""$DRAWSEGMENT
Po 2 %s %s 150
De 21 0 1200 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(innerhole), point_to_kicad(inner_arc_start))
    segments = segments + 1

f = open("segment.inc", "w")
emit_border(f)

f = open("mounting-holes.inc", "w")
emit_mounting_holes(f)

f = open("power-holes.inc", "w")
for group in range(0, 8):
    emit_group(f, group)

f = open("ndraw.inc", "w")
print >>f, "Ndraw %d" % segments

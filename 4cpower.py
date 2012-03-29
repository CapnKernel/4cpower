#! /usr/bin/python
# coding: utf-8

import math, cmath

# All dimensions in millimetres.
A = 27.6
B = math.sqrt(2*A*A)

deg45 = math.pi / 4

groups = 8
page_offset = complex(6 * 25.4, -4 * 25.4)
no_offset = complex(0, 0)

inner_distance = A * 0.45
outer_distance = A * 0.80

# How much the whole board should be rotated by
board_rotation = math.radians(0)

# Distance of border away from holes.
border_standoff = 4
# Distance between carrier and board
carrier_standoff = 2
# Distance between snap-off drill holes
snapoff_dist = 0.5

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
last_seg = None
group_text_pos = {}

def as_polar_string(p):
    return "(r=%f,θ=%f°)" % (abs(p), math.degrees(cmath.phase(p)))

def point_to_kicad(p, origin=page_offset):
    """ Convert a point in mm to a string in thousandths of an inch """
    rotated_p = cmath.rect(abs(p), cmath.phase(p) + board_rotation)
    offset_p = rotated_p + origin
    return "%d %d" % (int((offset_p.real / 25.4) * 10000), -int((offset_p.imag / 25.4) * 10000))

# Emit a segment for the edge of the board
# Takes two or three arguments.  Args two and
# three are the coords of the segment.  If there
# are only two arguments, previous is the next
# from last time.
# Note this has a strange side effect: It mirrors
# to all four quadrants of the board.
def pcb_edge(f, prev, next=None):
    global segments, last_seg
    if next == None:
        next = prev
        prev = last_seg
    for ymult in [-1, 1]:
        for xmult in [-1, 1]:
            print >>f, "$DRAWSEGMENT\nPo 0 %s %s 150\nDe 28 0 900 0 0\n$EndDRAWSEGMENT" % (point_to_kicad(complex(prev.real * xmult, prev.imag * ymult)), point_to_kicad(complex(next.real * xmult, next.imag * ymult)))
            segments = segments + 1
    last_seg = next

def emit_snapoff(snapgap_lh, snapgap_rh):
    snapgap_diff = snapgap_rh - snapgap_lh
    snapgap_holes = (abs(snapgap_diff) / snapoff_dist)
    snapgap_step = snapgap_diff / snapgap_holes
    # snapgap_half = snapgap_diff / 2
    # snapgap_mid = snapgap_lh + snapgap_half
    print "snapgap=", snapgap_lh, snapgap_rh, snapgap_diff, snapgap_holes, snapgap_step
    #snapgap_half, snapgap_mid
    snapgap_cursor = snapgap_lh
    while True:
        snapgap_cursor = snapgap_cursor + snapgap_step
        error_term = abs(snapgap_cursor - snapgap_rh)
        print "snapgap_cursor=", snapgap_cursor, "error_term=", error_term
        if error_term < snapoff_dist / 2:
            break
        print >>f, \
"""$MODULE snap-hole
Po %s 0 15 4F73C4C3 4F73C4A4 ~~
Li snap-hole
Cd Snap hole
Kw DEV
Sc 4F73C4A4
AR /4F583B52
Op 0 0 0
$PAD
Sh "" C 157 157 0 0 900
Dr 157 0 0
At HOLE N 00E0FFFF
Ne 0 ""
Po 0 0
$EndPAD
$EndMODULE  snap-hole""" % (point_to_kicad(snapgap_cursor))

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
        # Get the rough points for this segment
        if p % 2 == 0:
            next = cmath.rect(B, p * deg45 / 2)
        else:
            next = cmath.rect(odd_len, p * deg45 / 2)

        # Now there's lots of special-casing to do
        if p == 9:
            pcb_edge(f, prev, next)
        if p == 10:
            next1 = next + complex(0, -carrier_standoff)
            pcb_edge(f, prev, next1)
            next2 = complex(-B, next1.imag)
            pcb_edge(f, next2)
            pcb_edge(f, complex(-B, -B))
            # Snap-off drill holes
            # next is the left-hand edge of the snap gap
            # emit_snapoff(next, next + complex(carrier_standoff, 0))
        elif p == 11:
            prev1 = complex(prev.real + carrier_standoff, prev.imag)
            pcb_edge(f, prev1, next)
            prev2 = prev1 - complex(0, carrier_standoff)
            pcb_edge(f, prev1, prev2)
            diag_carrier_standoff_x_off = math.tan(math.radians(67.5)) / carrier_standoff
            # print "diag_carrier_standoff_x_off=", diag_carrier_standoff_x_off
            diag_carrier_standoff = complex(diag_carrier_standoff_x_off, carrier_standoff)
            # print "diag_carrier_standoff=", diag_carrier_standoff
            # print "next=", next
            next1 = next - diag_carrier_standoff
            # print "next1=", next1
            pcb_edge (f, next1)
        elif p == 12:
            # print "prev=", prev, "next=", next
            p12_vec = next - prev
            # print "p12_vec=", p12_vec, as_polar_string(p12_vec)
            p12_vec_60 = p12_vec * 0.6
            # print "p12_vec_60=", p12_vec_60, as_polar_string(p12_vec_60)
            p12_vec_70 = p12_vec * 0.7
            # print "p12_vec_70=", p12_vec_70, as_polar_string(p12_vec_70)
            pcb_edge(f, prev, prev + p12_vec_60)
            diag_carrier_standoff = cmath.rect(carrier_standoff, 5 * deg45)
            # print "diag_carrier_standoff=", diag_carrier_standoff
            pcb_edge(f, prev + p12_vec_60 + diag_carrier_standoff)
            pcb_edge(f, next1)
            pcb_edge(f, next, prev + p12_vec_70)
            pcb_edge(f, prev + p12_vec_70 + diag_carrier_standoff);
            diag_carrier_offset = next - (cmath.rect(carrier_standoff, deg45) + cmath.rect(carrier_standoff, -deg45))
            pcb_edge(f, complex(-B, -B), diag_carrier_offset)
            pcb_edge(f, prev + p12_vec_70 + diag_carrier_standoff);
        else:
            # pcb_edge(f, prev, next)
            # silly = []
            pass
    
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

def emit_simple_border(f):
    global segments
    borders = [[B, B], [B, -B], [-B, -B], [-B, B], [B, B]]
    # print borders
    for border in range(0, len(borders) - 1):
        print borders[border], borders[border + 1]
        print >>f, "$DRAWSEGMENT\nPo 0 %s %s 150\nDe 28 0 900 0 0\n$EndDRAWSEGMENT" % (point_to_kicad(complex(borders[border][0], borders[border][1])), point_to_kicad(complex(borders[border + 1][0], borders[border + 1][1])))
        segments = segments + 1

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
$PAD
Sh "1" C 2350 2350 0 0 0
Dr 1340 0 0
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
T1 %s 1000 1000 0 250 N I 21 N "%s"
$PAD
Sh "1" C 2500 2500 0 0 0
Dr 1000 0 0
At STD N 00E0FFFF
Ne %s
Po 0 0
$EndPAD""" % (point_to_kicad(innerhole), part, point_to_kicad(symboldiff, no_offset), sign, net)

    # Save the symbol position for later.
    group_text_pos[group] = {}
    group_text_pos[group]['text'] = sign
    group_text_pos[group]['position'] = symbol

    for smallholeid in range(0, 9):
        angle = 2 * math.pi / 9 * smallholeid
        smallhole = cmath.rect(2.17, angle)
        print >>f, \
"""$PAD
Sh "%d" C 394 394 0 0 900
Dr 250 0 0
At STD N 00E0FFFF
Ne %s
Po %s
$EndPAD""" % (1, net, point_to_kicad(smallhole, no_offset))

    print >>f, "$EndMODULE  power-hole"

    outerhole = {}
    standoff_ih_to_oh_vec = {}
    for outerholeid in range(0, 2):
        outerpart = part + outerholeid + 1
        multiplier = outerholeid * 2 - 1
        # print "group=", group, "part=", part, "outerholeid=", outerholeid, "outerpart=", outerpart, "about to do an outer hole"
        outer_angle = (group * 2 + outerholeid + 0.5) * deg45 / 2
        # print "angle=", math.degrees(angle)
        outerhole[outerholeid] = cmath.rect(outer_distance, outer_angle)

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
$EndPAD""" % (point_to_kicad(outerhole[outerholeid]), outerpart, net)
        for smallholeid in range(0, 9):
            angle = 2 * math.pi / 9 * smallholeid
            smallhole = cmath.rect(2.17, angle)
            print >>f, \
"""$PAD
Sh "%d" C 394 394 0 0 900
Dr 250 0 0
At STD N 00E0FFFF
Ne %s
Po %s
$EndPAD""" % (1, net, point_to_kicad(smallhole, no_offset))

        print >>f, "$EndMODULE  power-hole"

        # print "innerhole=", innerhole, as_polar_string(innerhole)
        # print "outerhole[outerholeid]=", outerhole[outerholeid], as_polar_string(outerhole[outerholeid])
        ih_to_oh = outerhole[outerholeid] - innerhole
        # print "ih_to_oh=", ih_to_oh, as_polar_string(ih_to_oh)
        standoff_ih_to_oh_vec[outerholeid] = cmath.rect(border_standoff, cmath.phase(ih_to_oh) + multiplier * 2 * deg45)
        # print "standoff_ih_to_oh_vec[outerholeid]=", standoff_ih_to_oh_vec[outerholeid], as_polar_string(standoff_ih_to_oh_vec[outerholeid])
        
        ih_to_oh_line_start = innerhole + standoff_ih_to_oh_vec[outerholeid]
        ih_to_oh_line_end = outerhole[outerholeid] + standoff_ih_to_oh_vec[outerholeid]
        segments = segments + 1
        print >>f, \
"""$DRAWSEGMENT
Po 0 %s %s 150
De 21 0 900 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(ih_to_oh_line_start), point_to_kicad(ih_to_oh_line_end))

    # Calculate points for segment on boundary between two outer holes
    # print "outerhole[0]=", outerhole[0], as_polar_string(outerhole[0])
    # print "outerhole[1]=", outerhole[1], as_polar_string(outerhole[1])
    oh0_to_oh1 = outerhole[1] - outerhole[0]
    # print "oh0_to_oh1=", oh0_to_oh1, as_polar_string(oh0_to_oh1)

    standoff_oh0_to_oh1_vec = cmath.rect(border_standoff, cmath.phase(oh0_to_oh1) - 2 * deg45)
    # print "standoff_oh0_to_oh1_vec=", standoff_oh0_to_oh1_vec, as_polar_string(standoff_oh0_to_oh1_vec)
    oh0_to_oh1_line_start = outerhole[0] + standoff_oh0_to_oh1_vec
    oh0_to_oh1_line_end = outerhole[1] + standoff_oh0_to_oh1_vec
    segments = segments + 1
    print >>f, \
"""$DRAWSEGMENT
Po 0 %s %s 150
De 21 0 900 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(oh0_to_oh1_line_start), point_to_kicad(oh0_to_oh1_line_end))

    # Draw arc around bottom of inner circle
    inner_arc_angle = 2 * math.pi - (cmath.phase(standoff_ih_to_oh_vec[1]) - cmath.phase(standoff_ih_to_oh_vec[0]))
    # Normalise to -pi .. pi
    if inner_arc_angle > math.pi:
        inner_arc_angle = inner_arc_angle - 2 * math.pi

    # print "inner_arc_angle=", math.degrees(inner_arc_angle)
    print >>f, \
"""$DRAWSEGMENT
Po 2 %s %s 150
De 21 0 %d 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(innerhole), point_to_kicad(ih_to_oh_line_start), -int(math.degrees(inner_arc_angle) * 10))
    segments = segments + 1

    # Easy to calculate the angles of the other two arcs, as they are identical, and
    # will use the angle not used by the inner arc.
    outer_arc_angle = (2 * math.pi - inner_arc_angle) / 2
    # print "outer_arc_angle=", math.degrees(outer_arc_angle)

    print >>f, \
"""$DRAWSEGMENT
Po 2 %s %s 150
De 21 0 %d 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(outerhole[1]), point_to_kicad(ih_to_oh_line_end), int(math.degrees(outer_arc_angle) * 10))
    segments = segments + 1

    print >>f, \
"""$DRAWSEGMENT
Po 2 %s %s 150
De 21 0 %d 0 0
$EndDRAWSEGMENT""" % (point_to_kicad(outerhole[0]), point_to_kicad(oh0_to_oh1_line_start), int(math.degrees(outer_arc_angle) * 10))
    segments = segments + 1

def emit_zones(f):
    zonemult = 0.99
    TL = complex(-B * zonemult, B * zonemult)
    TR = complex(B * zonemult, B * zonemult)
    BL = complex(-B * zonemult, -B * zonemult)
    BR = complex(B * zonemult, -B * zonemult)

    zoneparams = \
"""ZClearance 200 I
ZMinThickness 100
ZOptions 0 16 F 200 200
ZSmoothing 0 0
ZCorner %s 0
ZCorner %s 0
ZCorner %s 0
ZCorner %s 0
ZCorner %s 1
$endCZONE_OUTLINE""" % (point_to_kicad(TL), point_to_kicad(TR), point_to_kicad(BR), point_to_kicad(BL), point_to_kicad(TL))

    print >>f, \
"""$CZONE_OUTLINE
ZInfo 4F6834F0 1 "N-000001"
ZLayer 15
ZAux 5 E"""
    print >>f, zoneparams
    print >>f, \
"""$CZONE_OUTLINE
ZInfo 4F68396B 2 "N-000009"
ZLayer 0
ZAux 4 E"""
    print >>f, zoneparams

def emit_text(f):
    for group in range(0, groups):
        for layer in (20, 21):
            print >>f, \
"""$TEXTPCB
Te "%s"
Po %s 1000 1200 200 0
De %d 1 0 Normal C
$EndTEXTPCB""" % (group_text_pos[group]['text'], point_to_kicad(group_text_pos[group]['position']), layer)

    # TODO: Parameterise text position in terms of A and B.

    print >>f, \
"""$TEXTPCB
Te "Want cheap PCBs?"
Po 68307 52559 403 721 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "http://hackvana.com/pcbs"
Po 68504 54528 403 721 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "CC-BY-SA 3.0"
Po 53937 53543 403 721 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "https://github.com/CapnKernel/4cpower/"
Po 51575 54528 403 721 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "power board v1.0"
Po 52362 27165 472 787 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "n"
Po 49213 25590 472 787 101 0
De 21 1 0 Italic L
$EndTEXTPCB
$TEXTPCB
Te "copter-compatible"
Po 53150 25590 472 787 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "Check out Good Luck Buy for"
nl "the best hobby products!"
nl "http://goodluckbuy.com/"
Po 69094 25394 403 721 101 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "http://goodluckbuy.com/index.php?target=products&mode=search&q=76666"
Po 59843 50394 276 512 69 0
De 21 1 0 Normal C
$EndTEXTPCB
$TEXTPCB
Te "Open Source Hardware"
Po 52165 52559 403 721 101 0
De 21 1 0 Normal C
$EndTEXTPCB"""

## MAIN
f = open("segment.inc", "w")
emit_border(f)
# emit_simple_border(f)

f = open("mounting-holes.inc", "w")
emit_mounting_holes(f)

f = open("power-holes.inc", "w")
for group in range(0, groups):
    emit_group(f, group)

f = open("zones.inc", "w")
emit_zones(f)

f = open("text.inc", "w")
emit_text(f)

f = open("ndraw.inc", "w")
print >>f, "Ndraw %d" % segments

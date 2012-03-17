#! /usr/bin/python

import math, cmath

# All dimensions in millimetres.
A = 27.6
B = math.sqrt(2*A*A)

deg45 = math.pi / 4

page_offset = complex(6 * 25.4, -4 * 25.4)
no_offset = complex(0, 0)

def point_to_kicad(p, origin=page_offset):

    """ Convert a point in mm to a string in thousandths of an inch """
    offset_p = p + origin
    return "%d %d" % (int((offset_p.real / 25.4) * 10000), -int((offset_p.imag / 25.4) * 10000))

def emit_border(f):
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
    
        prev = next

    # Draw inner circle
    middle = complex(0, 0)
    threeoclock = complex(A * 0.24, 0)
    print >>f, \
"""$DRAWSEGMENT
Po 3 %s %s 150
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
    # print "group=", group, "about to do inner hole and symbol"
    hole = cmath.rect(A * 0.45, (group + 0.5) * deg45)
    symbol = cmath.rect(abs(hole) * 1.45, cmath.phase(hole))
    symboldiff = symbol - hole
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
(point_to_kicad(hole), part, point_to_kicad(symboldiff, no_offset), sign, net)

    for outerholeid in range(0, 2):
        outerpart = part + outerholeid + 1
        # print "group=", group, "part=", part, "outerholeid=", outerholeid, "outerpart=", outerpart, "about to do an outer hole"
        hole = cmath.rect(A * 0.80, (group * 2 + outerholeid + 0.5) * deg45 / 2)
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
$EndMODULE  power-hole""" % (point_to_kicad(hole), outerpart, net)

f = open("segment.inc", "w")
emit_border(f)

f = open("mounting-holes.inc", "w")
emit_mounting_holes(f)

f = open("power-holes.inc", "w")
for group in range(0, 8):
    emit_group(f, group)


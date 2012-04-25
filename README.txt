Hello and welcome to 4cpower.

4cpower is a project to create a PCB which can be used to distribute
power for quadcopters, and other similar flying machines.  I'm not
sure how much current this board can handle, but similar boards carry
100A with no problems.

The board is designed in KiCad, which is a free cross-platform
board design program.  

  http://kicad.sourceforge.net/wiki/

The design contains four snap-off sections at the corners.  Snap them
off before using the board.

This board is licensed under the Creative Commons "Attribution-
ShareAlike 3.0 Unported License":

  http://creativecommons.org/licenses/by-sa/3.0/

You are welcome to share and alter the board design, to sell and
use it for commercial purposes, and to contribute suggestions and
improvements back to me.  You must leave the lower left hand corner
(with my name on it) as it is.

My name is Mitch Davis <mjd@afork.com>.  I live in Melbourne Australia
and Shenzhen China.  I make affordable PCBs for hobbyists:

  http://www.hackvana.com/pcbs

You are welcome to ask me to make this board for you, to make it yourself,
or to buy it from a reputable supplier, such as Good Luck Buy:

  http://goodluckbuy.com/index.php?target=products&mode=search&q=80949

This board contains a lot of symmetry, and it would be infeasible to
place all the parts and holes by hand.  So instead, a small Python script
generates the positions of everything, and emits the .brd file for KiCad
to read.

The final board file is 4cpower.brd.  How is it made?  Well, run "make".
Make calls the python script, 4cpower.py.

4cpower.py makes:
  logo.inc
  power-holes.inc
  mounting-holes.inc
  text.inc
  zones.inc
  segment.inc
 
Then "make" calls "cpp", which reads 4cpower-master.brd, which includes
these, plus nets.inc, to make 4cpower.brd

You can load this file into KiCad like this:

  kicad 4cpower.pro

Then double-click on 4cpower.brd.

You are welcome to send me suggestions or improvements.

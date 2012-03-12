TARGET:=4cpower.brd
INCLUDES:=nets.inc input-holes.inc output-holes.inc mounting-holes.inc segment.inc

all: $(TARGET)

$(TARGET): 4cpower-master.brd $(INCLUDES)
# I found a bug in fedora cpp: https://bugzilla.redhat.com/show_bug.cgi?id=787345
# Workaround is to force the pipeline to leave with true.
	(cpp -P $<; true) | sed -e 's/井/#/g' > $@

$(INCLUDES): 4cpower.py
	./$<

.PHONY: clean
clean:
	-rm -f $(TARGET)

TARGET:=4cpower.brd
INCLUDES:=power-holes.inc mounting-holes.inc segment.inc ndraw.inc zones.inc text.inc logo.inc
RUBBISH=$$4cpower.brd *.000 *-cache.lib *.bak

all: $(TARGET)

$(TARGET): 4cpower-master.brd $(INCLUDES)
# I found a bug in fedora cpp: https://bugzilla.redhat.com/show_bug.cgi?id=787345
# Workaround is to force the pipeline to leave with true.
	(cpp -P $<; true) | sed -e 's/井/#/g' > $@

$(INCLUDES): 4cpower.py
	./$<

.PHONY: clean
clean:
	-rm -f $(TARGET) $(INCLUDES)
	-rm -f $(RUBBISH)

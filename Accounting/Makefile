#
# build a jar for the accounting app
#
SRCDIR=src
OUTDIR=bin

JAR=Accounting.jar
MANIFEST=Accounting.mf

SOURCES = $(wildcard $(SRCDIR)/accounting/*.java)
CLASSES = $(patsubst $(SRCDIR)/accounting/%.java,$(OUTDIR)/accounting/%.class,$(SOURCES))

.PHONY: rebuild clean clobber lint

$(JAR): rebuild $(CLASSES)
	cd bin; jar -cvfm ../$(JAR) ../$(MANIFEST) accounting/*.class accounting/images

#
# I tried building a per-file rule to do this, but the individual compiles
#   failed for want of other classes in the same package:
#	$(OUTDIR)/accounting/%.class: $SRCDIR)/accounting/%.java
#		javac -d $(OUTDIR) $<
#
# So I just wrote this simple rule to recompile everything
rebuild: $(SOURCES)
	mkdir -p $(OUTDIR)/accounting/images
	javac -d $(OUTDIR) $(SRCDIR)/accounting/*.java
	cp $(SRCDIR)/accounting/images/*.png $(OUTDIR)/accounting/images

clean:
	rm -f $(CLASSES) $(OUTDIR)/accounting/images/*.png

clobber:
	rm -f $(JAR) $(CLASSES)

lint:	makeledger.py
	pycodestyle $<
	pylint $<

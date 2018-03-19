#! /bin/sh
# This script automatically creates UML class diagrams for each modules
# in the specified path. (No diagram will be made for modules that don't
# include classes.)

DPATH="/Users/geomando/Dropbox/github/DESaster/desaster"

pyreverse -o png -p entities $DPATH/entities 
pyreverse -o png -p structures $DPATH/structures
pyreverse -o png -p technical $DPATH/technical
pyreverse -o png -p financial $DPATH/financial
pyreverse -o png -p visualize $DPATH/visualize
pyreverse -o png -p policies $DPATH/policies
pyreverse -o png -p hazus $DPATH/hazus
pyreverse -o png -p io $DPATH/io
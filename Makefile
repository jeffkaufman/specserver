#
# Makefile for string mangler client/server 
# to build client and server programs:
#  % make
# to clean up all stuff that can be re-built:
#  % make clean
#


.PHONY: clean

all: specserver.o
	gcc -g -Wall -o specserver -L/scratch/jkaufman/lib\
  specserver.c -lsndfile -lfftw3 -lm
clean:
	$(RM) *.o *~ *.dat core specserver


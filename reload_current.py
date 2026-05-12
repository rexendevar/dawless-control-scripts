import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import load_set
import sys

if len(sys.argv) > 1:
    load_set.load("current.sav", sys.argv[1])
else:
    load_set.load("current.sav")
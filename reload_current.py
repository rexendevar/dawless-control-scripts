import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is
import load_set

load_set.load("current.sav")
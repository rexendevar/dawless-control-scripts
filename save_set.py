import shutil
import sys
import os
os.chdir(os.path.dirname(os.path.realpath(__file__))) # set cwd to where the script is

if len(sys.argv) > 1:
    shutil.copy( "current.sav", ('saves/'+sys.argv[1]+'.sav') )
else:
    shutil.copy( "current.sav", ('saves/'+input("Enter save name: ")+'.sav') )
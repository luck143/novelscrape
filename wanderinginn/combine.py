import shutil
import time, glob
import os


#path = os.getcwd()+'\\downloads\\ninestar' 
path = os.getcwd()+'\\downloads\\wandering_inn\\' 
print(path)

outfilename = os.getcwd()+'\\downloads\\wandering_inn_' + str((int(time.time()))) + ".txt"

files = list(filter(os.path.isfile, glob.glob(path + "*.txt")))
files.sort(key=lambda x: os.path.getmtime(x))
print(files)


with open(outfilename, 'w') as outfile:
    for fname in files:
        filename=os.path.basename(fname)
        print (filename)
        name=filename.rsplit('.', 1)[0] 
        print (name)
        with open(fname, 'r') as readfile:
            outfile.write("#Chapter "+str(name)+" : "+str(name)+"\n"+readfile.read() + "\n\n")
            #outfile.write("--*-- \n\n\n\n #Chapter "+str(name)+" : "+"\n"+readfile.read() + "\n\n")
            #outfile.write("#"+readfile.read() + "\n\n")


# with open(outfilename, 'w') as outfile:
#     for fname in glob.glob(path +'/*.txt'):
#         filename=os.path.basename(fname)
#         name=filename.rsplit('.', 1)[0] 
#         print (name)
#         with open(fname, 'r') as readfile:
#             #outfile.write("#Chapter "+str(name)+" : "+str(name)+"\n"+readfile.read() + "\n\n")
#             #outfile.write("#Chapter "+str(name)+" : "+"\n"+readfile.read() + "\n\n")
#             outfile.write("#"+readfile.read() + "\n\n")

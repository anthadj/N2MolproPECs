#
#  createFolderStructure.py
#
#  Created by Antonis Hadjipittas on 13/07/2023.
#  Copyright © 2023 AHadjipittas. All rights reserved.
#

import sys
import os
import shutil

inputs='../inputs'
outputs='../outputs'
molden = 'molden'
potSur = 'potentialSurfaces'
xml = 'folder_xml'

#--------------------------------------------
#-----Create Folder Structure in 1st run-----
#--------------------------------------------
def createFolderStructure():

    try:
        os.mkdir(inputs)
        os.mkdir(outputs)
        
        os.mkdir(outputs+"/"+xml)
        os.mkdir(outputs+"/"+potSur)
        os.mkdir(outputs+"/"+molden)
        
    except OSError:
        pass
    else:
        print ("folders successfully created")

    pathMolden = outputs+"/"+molden+"/"

    for i in range(0,3):
        for j in range(0,3):
            for k in range(0,3):
                for ii in range(0,3):
                    for jj in range(0,3):
                        for kk in range(0,3):
                            for iii in range(0,3):
                                if (i+j+k+ii+jj+kk+iii > 9):
                                    config=str(i)+str(j)+str(k)+str(ii)+str(jj)+str(kk)+str(iii)

                                    dirConfig = os.path.join(pathMolden, config)
                                    print ("Creating: ", config)

                                    try:
                                        os.mkdir(dirConfig)
                                    except OSError:
                                        pass
                                    else:
                                        print ("molden folder successfully created")

        
    

#----------------------------------------------
#------Move Outputs Files To Right Folder------
#----------------------------------------------
def moveOutputFilesToFolders():
    path= "../outputs"
    allfiles= os.listdir(path)
    for file in allfiles:
        #if (file.endswith(".molden")):
        if (file.endswith(".molden")) and len(file.split("_"))<6:
            config=file.split('_')[2][:-7]
            destination=path+"/"+molden+"/"+config
            shutil.move(os.path.join(path, file), os.path.join(destination,file)) #By writing full path for both source and target
                                              #means that shutil.move() overwrites the file if it
                                                  #alredy exists
            print ("Moved ", file, " to ", destination)


        elif (file.endswith(".molden")) and len(file.split("_"))==6:
            config=file.split('_')[-1][:7]
            destination=path+"/"+molden+"/"+config
            shutil.move(os.path.join(path, file), os.path.join(destination,file)) #By writing full path for both source and target
                                                                                  #means that shutil.move() overwrites the file if it
                                                                                          #alredy exists
            print ("Moved ", file, " to ", destination)

#        elif (file.startswith("r_")):
#            destination=path+"/"+o_e
            #shutil.move(file, destination)
#            shutil.move(os.path.join(path, file), os.path.join(destination,file)) #By writing full path for both source and target
                                                                                  #means that shutil.move() overwrites the file if it
                                                                                  #alredy exists
#            print ("Moved ", file, " to ", destination)

        elif (file.endswith(".dat")):
            destination=path+"/"+potSur
            #shutil.move(file, destination)
            shutil.move(os.path.join(path, file), os.path.join(destination,file)) #By writing full path for both source and target
                                                                                  #means that shutil.move() overwrites the file if it
                                                                                  #alredy exists
            print ("Moved ", file, " to ", destination)

        elif (file.endswith(".xml")):
            destination=path+"/"+xml
            shutil.move(os.path.join(path, file), os.path.join(destination,file))
            
            print ("Moved ", file, " to ", destination)



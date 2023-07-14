#
#  main.py
#
#  Created by Antonis Hadjipittas on 13/07/2023.
#  Copyright © 2023 AHadjipittas. All rights reserved.
#

import sys
import os

import testConfigsRun as test		    #methods used for testing
import createFolderStructure as folders     #methods to create folder structure and
                                            #tidy up outpus after run
import makeMolproInputs_CASSCF as makeM     #methods to create initial molpro input files
import analyseOutputs as analyse            #after we run outputs, we use methods from
                                            #here to generate inputs for inner and core-inner

#------Running the main algorithm------
def main():
    inputsPath='../inputs/'
    outputsPath='../outputs/'

    files=os.listdir('..')

    firstRun=False
    for file in files:
        if file == 'inputs':
            firstRun=True
        
    #First time the code runs, it creates the necessary folder
    #structure and creates all input files
    if firstRun==False:
        print ("Running first time, creating file structure and generating input files")
        folders.createFolderStructure()
        makeM.createMolproInputs('../inputs')
        
    #If the code already ran once, the user must run all input files into the directory 'outputs' with the ending .out
    else:
        #1st test. Check the number of input files
        #(step 2 and 3 respectively)
        checkInputFiles,step=test.testNumberOfInputs(inputsPath)
        if checkInputFiles==False: exit(0)   #Check that all input files were created succesfully
       
        #2nd test. Check that the user has successfully ran all the input files
        if test.testAllInputsRunSuccesfully(inputsPath, outputsPath)==False: exit(0)
      
        #We move to step 2 if all input files have successfully ran.
        #We open the txt files ConfigData and ConfigInnerCoreData in the folder inputs
        #and read the configurations for each set of molpro variables (read report)
        #We then open all the .out files in the outputs folder ending in I.out, or IC.out,
        #find those configurations and find the biggest coefficient, which corresponds to
        #the root we are looking for.
        if step==2:
            print ("Step 2")
            #We first  move all the files in the output folder to
            #their respective folder i.e. potential curve data are moved to
            #'outputs/potentialSurfaces' and xml files are moved to 'outputs/folder_xml'
            # This is done to clear up the files in the folder
            folders.moveOutputFilesToFolders()

            print ("Moved files to folders in outputs folder")
        
            #---------------------------------------------------------------------------------
            #----Analyse inner (SA-CASSCF) and inner-core (SA-TS-CASSCF) technique outputs----
            #---------------------------------------------------------------------------------

            #Open output files ending with I.out (inner or SA-CASSCF) and IC.out (inner-core or SA-TS-CASSCF)  
            #Then find the root corresponding to each configuration of interest (stored in
            # "../inputs/ConfigData" for inner and "../inputs/ConfigsInnerCoreData" for inner-core.
            #Finally create a new input file in the "../inputs" directory for each configuration of interest
            print ("---Analysing I.out files---")
            analyse.analyseOutputs_CreateNewInputs_I(outputsPath,inputsPath)
            print ("---Analysing IC.out files---")
            analyse.analyseOutputs_CreateNewInputs_IC(outputsPath,inputsPath)

            #---------------------------------------------------------------------------------
            #---------------------------------------------------------------------------------
            #---------------------------------------------------------------------------------

            makeM.outputNumberOfInputFiles(inputsPath,2) #Store new number of input files

        #We enter here if we have successfully ran the code twice. Here we just tidy up the outputs
        if step==3:
            print ("Step 3")
            print ("Moving files in outputs folder to their respective directory")
            folders.moveOutputFilesToFolders()

if __name__ == "__main__":
    print ("Running code")
    main()


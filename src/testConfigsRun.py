#
#  testConfigsRun.py
#
#  Copyright 2023 Antonis Hadjipittas
#

import os

def testNumberOfInputs(inputsPath):
    with open(inputsPath+'InputFilesCreated', 'r') as inNumFiles:
        lines = inNumFiles.readlines()
        numOfFiles = int(lines[-1].split(':')[-1])

    inFiles=0
    dataFiles=0
    allInFiles = os.listdir(inputsPath)
    for file in allInFiles:
        if file.endswith(".in"):
            inFiles+=1
        elif file.endswith("Data"):
            dataFiles+=1
 
    if inFiles==numOfFiles and len(lines)==1:
        print ("There are ", numOfFiles, " input files. The code proceeds to step 2")
        print ("")
        print ("")
        return True,2
        
    elif inFiles==numOfFiles and len(lines)==2:
        print ("There are ", numOfFiles, " input files. The code proceeds to step 3")
        print ("")
        print ("")
        return True,3

    else:
        print ("Something is wrong with the number of input files.")
        print ("There are: ", len(allInFiles), " files. Is that correct?")
        return False,0

#Check there are equal number of inputs and outputs
#Also check that all outputs run all the way to the end
def testAllInputsRunSuccesfully(inPath,outPath):
    
    allinfiles= os.listdir(inPath)

    alloutfiles= os.listdir(outPath)
    
    #Scan over all input files
    inFiles=0
    allInFiles=list()
    for file in allinfiles:
        if file.endswith(".in"):
            inFiles=inFiles+1
            allInFiles.append(file[:-3])    #List with all input files

    #Scan over all output files
    #Create two lists, one to find the input files that didn't even run,
    #and one to find the output files that ran but didn't finish successfully.
    count=0
    outFiles=0
    allOutFiles=list()
    failedOutRuns=list()
    for file in alloutfiles:
        if file.endswith(".out"):
            outFiles=outFiles+1
            allOutFiles.append(file[:-4])   #List with all output files
            
            with open(outPath+file) as f:
                lines=f.readlines()
                if "Molpro calculation terminated" not in lines[-1]:
                    count=count+1
                    failedOutRuns.append(file)  #List with all failed output files
                   
    #Check if there are as many output files, as input files
    inputsThatDidntRunCounter = 0
    inputsThatDidntRun = list()
    if outFiles!=inFiles:
        for entry in allInFiles:
            if entry not in allOutFiles:
                inputsThatDidntRun.append(entry)
                inputsThatDidntRunCounter=inputsThatDidntRunCounter+1
                
        print (inputsThatDidntRunCounter, " inputs didn't run and didn't create a .out file")
        print ("These are the following: ")
        print (inputsThatDidntRun)
        return False

    if count!=0:
        print (count, " out of ", inFiles, " runs have't run to the end")
        print ("These are the following: ", failedOutRuns)
        return False
    else:
        return True



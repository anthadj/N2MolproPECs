#
#  analyseOutputs.py
#
#  Created by Antonis Hadjipittas on 13/07/2023.
#  Copyright © 2023 AHadjipittas. All rights reserved.
#

import os
import random
from os.path import exists

#NOT USED
def findEquilibriumDistance(enList):
    lowestEn=enList[0]
    lowestEnIndex=0
    for i in range(0,len(enList)):
        if enList[i]<lowestEn:
            lowestEn=enList[i]
            lowestEnIndex=i

    if lowestEnIndex>19:
        lowestEnIndex=11

    return lowestEnIndex

#NOT USED
#Check if the configuration of interest, appears in the CI coefficients of all the 29 distances
#The 29 distances were originally hard coded. It needs to be changed.
def checkConfigAppearsForAllDistances(dataIndices,lines,f):
    appeared=0
    for k in range(0,len(dataIndices),2):
        for p in range(dataIndices[k],dataIndices[k+1]):
            line=lines[p].split('        ')
            if conStr in line[0]:
                appeared+=1
                break

    if appeared<29:
        print ("Config appears in less than 29 distance. It appears in ", appeared, " counts.")

        name='./innFilesWithMissingConfigs' if f=="inner" else './innCoreFilesWithMissingConfigs'

        with open(name, 'a') as f:
            f.write(file)
            f.write(" Config ")
            f.write(str("".join(con)))
            f.write(" appeared in this many counts out of 30 total: ")
            f.write(str(appeared))
            f.write("\n\n")

        repeatAndIncreaseStates.append(file)
    else:
        print ("Config appeared in ", appeared, " counts")
    
#Open file containing information, about which new inputs must be produced.
#File called 'ConfigData' which was created when the input files were initially created
def findInputsToCreate_I(inputsPath):
    allInputFiles=os.listdir(inputsPath)
    
    varsList=list()
    configsList=list()
    for file in allInputFiles:
        if file == "ConfigData":
            print ("Opening file", file)
            with open(inputsPath+"/"+file) as g:
                lines=g.readlines()
        
            for line in lines:
                if len(line.split('_')) == 3:
                    varsList.append(line)
                    empty=list()
                    configsList.append(empty)

                if len(line.split(',')) == 8:
                    configsList[-1].append(line.split(','))
    
    #Clean up the two lists of data from unessecary before returning them
    #Remove /n from end of entry
    for i in range(0,len(varsList)):
        varsList[i]=varsList[i][0:-1]

    #Remove last entry
    for i in range(0,len(configsList)):
        for j in range(0,len(configsList[i])):
            configsList[i][j].pop(-1)

    return varsList,configsList
    
    
    
def findInputsToCreate_IC(inputsPath):
    allInputFiles=os.listdir(inputsPath)
    
    varsList=list()
    restrictList=list()
    configsList=list()
    for file in allInputFiles:
        if file == "ConfigInnerCoreData":
            print ("Opening file", file)
            with open(inputsPath+"/"+file) as g:
                lines=g.readlines()
        
            for line in lines:
                if len(line.split('_')) == 3:
                    varsList.append(line)
                    empty=list()
                    configsList.append(empty)

                if len(line.split(',')) == 8:
                    configsList[-1].append(line.split(','))
                    
                if line[0] == "[":
                    line = line[2:-3]
                    rnum = len(line.split("', '"))
            
                    empty=list()
                    restrictList.append(empty)

                    if rnum > 1:
                        for i in range(0,rnum):
                            restrictList[-1].append(line.split("', '")[i])
                    else:
                        restrictList[-1].append(line)
    for i in range(0,len(restrictList)):
        for j in range(0,len(restrictList[i])):
            restrictList[i][j] = restrictList[i][j][-3:]
    
    #Clean up the two lists of data from unessecary before returning them
    #Remove /n from end of entry
    for i in range(0,len(varsList)):
        varsList[i]=varsList[i][0:-1]

    #Remove last entry
    for i in range(0,len(configsList)):
        for j in range(0,len(configsList[i])):
            configsList[i][j].pop(-1)

    return varsList,configsList,restrictList
    
    
    
def findDataIndices_I(lines):
    recording=False
    multiBool=False
    multiFirst=False
    dataIndices=list()
    for i,line in enumerate(lines): #Scan through line of output file

        #First time we encounter word string, record that we encountered it and continue without saving data
        #First time we encounter it is for the neutral N2 case
        if "Direct Multiconfiguration SCF" in line and multiFirst==False:
            multiFirst=True
            continue

        #Second time we encounter it record that these data need to be recorded
        #Second time we encounter it is data for the N2 ion of interest
        if "Direct Multiconfiguration SCF" in line and multiFirst==True:
            multiBool=True

        #Record the line index of where the data starts
        if "CI Coefficients of state" in line and multiBool==True:
            dataIndices.append(i)
            recording=True

        #Record the line index of where the data ends
        if recording==True:
            if " Energy:      " in line:
                dataIndices.append(i+1)
                recording=False
                multiBool=False
                multiFirst=False
   
    return dataIndices

#Find equilibrium distance specified in first line of input file. 
#It is also specified in the first line of the output file
def findEquilDist(lines):
    for line in lines:
        if "***" in line:
            equilDist = line.split("_")[-1].strip("\n")
            print ("Equilibrium Distance Used: ", equilDist)
            return equilDist
    return 0

#This method returns the number of distances used in the input file, as well as
#the index of the equilibrium distance. If the equilibrium distance is not found
#the code ends with an error
def findNumOfDistances_findEquilibriumDistIndex(lines,equil):
    for line in lines:
        if "len=[" in line and "]" in line:
            line = line.replace("len=[","")
            line = line.replace("]","")
            distLine = line.split(",")
            for i,dist in enumerate(distLine):
                if dist == equil:
                    return len(distLine), i
                    
            print ("No equilibrium distance found, exiting")
            exit(0)
    
def findDataIndices_IC(lines,multiCounter):
    multiCounter=0
    dataIndices=list()
    for i,line in enumerate(lines):

        if "Direct Multiconfiguration SCF" in line:
            multiCounter+=1

        #Record the line index of where the data starts
        if "CI Coefficients of state" in line and multiCounter==5:
            dataIndices.append(i)

        #Record the line index of where the data ends
        if multiCounter==5:
            if " Energy:      " in line:
                dataIndices.append(i+1)
                multiCounter=0
    
    return dataIndices
    
    
#Create initial guess for configuration we are looking for.
#Guess is of the form 222 2 2 220 0 0. This function returns character a in place
#of any open orbitals, i.e. 2aa 2 a 2a0 0 0
def createConfigForCIcoefficients(con):
    conStr=""
    
    conStr+=con[0] if (con[0] == '0' or con[0] == '2') else "a"
    conStr+=con[2] if (con[2] == '0' or con[2] == '2') else "a"
    conStr+=con[6] if (con[6] == '0' or con[6] == '2') else "a"
    conStr+=" "
    conStr+=con[4] if (con[4] == '0' or con[4] == '2') else "a"
    conStr+=" "
    conStr+=con[5] if (con[5] == '0' or con[5] == '2') else "a"
    conStr+="  "
    conStr+=con[1] if (con[1] == '0' or con[1] == '2') else "a"
    conStr+=con[3] if (con[3] == '0' or con[3] == '2') else "a"
    conStr+="0 0 0"
    return conStr

def findMaxCoeffIndex(line):
    maxNum=0
    maxNumIndex=0
    for j in range(1,len(line)):
        line[j] = float(line[j])
        
        if abs(line[j]) > maxNum:
            maxNum=abs(line[j])
            maxNumIndex=j
    return maxNumIndex,maxNum
    
def findSecondMaxCoeffIndex(line,maxNum):
    maxNum2=0
    for j in range(1,len(line)):
        line[j] = float(line[j])

        if abs(line[j])==maxNum:
            continue

        if abs(line[j]) > maxNum2:
            maxNum2=abs(line[j])
            maxNumIndex=j
            
    return maxNumIndex

#Takes in a configuration of the form 22a 0 b 220 0 0 and randomly change the a and b to a,b,\ or /
def randomlyChangeConfigurationString(conStr):
    #print ("Before: ", conStr)
    for i in range(0,len(conStr)):
        if conStr[i] == "a" or conStr[i] =="b" or conStr[i] =="/" or conStr[i] =="\\":
            decide = random.uniform(0, 1)
            if decide>=0 and decide<0.25:
                conStr=conStr[0:i]+"a"+conStr[i+1:]
            elif decide>=0.25 and decide<0.5:
                conStr=conStr[0:i]+"b"+conStr[i+1:]
            elif decide>=0.5 and decide<0.75:
                conStr=conStr[0:i]+"/"+conStr[i+1:]
            elif decide>=0.75 and decide<=1:
                conStr=conStr[0:i]+"\\"+conStr[i+1:]
    #print ("After: ", conStr)

    return conStr
    
def outputData_I(configColumn,configCorresponsingToColumn,file,outPath):
    with open (outPath+'/columnsDataInner', 'a') as f:
        f.write(file)
        f.write("\nColumns corresponding to each config: \n")
        f.write(str(configColumn))
        f.write("\nThe configs: \n")
        for i in range(0,len(configCorresponsingToColumn)):
            f.write("".join(configCorresponsingToColumn[i]))
            f.write("\n")
        f.write("\n\n")
        f.close()

def outputData_IC(configColumn,configCorresponsingToColumn,file,outPath):
    with open (outPath+'/columnsDataInnerCore', 'a') as f:
        f.write(file)
        f.write("\nColumns corresponding to each config: \n")
        f.write(str(configColumn))
        f.write("\nThe configs: \n")
        for i in range(0,len(configCorresponsingToColumn)):
            f.write("".join(configCorresponsingToColumn[i]))
            f.write("\n")
        f.write("\n\n")
        f.close()
        
def createNewFile_I(configColumn,configCorresponsingToColumn,file,inPath):
    for i in range(0, len(configColumn)):
        newFilename=file[0:-5]+"".join(configCorresponsingToColumn[i])+"_I.in"
        #print newFilename

        generalInFile = file[0:-4]+".in"
        #print generalInFile

        if os.path.exists(newFilename):
            print ("File exists: ", newFilename)
            continue

        print ("Creating: ", newFilename)

        with open(inPath+'/'+generalInFile, 'r') as f:
            data=f.read()

            #Find the line where the table is printed out. This needs to be replaced
            tableReplaceList=""
            recordBool = False
            for j in range(0,len(data)):
                if data[j]=="{" and data[j+1]=="t":
                    recordBool = True

                if data[j] == ";":
                    recordBool = False

                if recordBool:
                    tableReplaceList+=data[j]

            vars=file[3:-6]#The three varibles used to distinguish inner valence

            sym = data.split('wf,')[3][3]
    
            data = data.replace("!Input natorb,state=8.1; before orbital, for orbital you want to find","")
            data = data.replace("!Input configuration before ' element","")
            data = data.replace('!moldenname','moldenname')
            data = data.replace('!put,','put,')
            data = data.replace('$rad$_','$rad$_'+vars+'_'+''.join(configCorresponsingToColumn[i]))
            data = data.replace('orbital,2141.2', 'natorb,state='+str(configColumn[i])+'.'+sym+';orbital,2141.2')
            data = data.replace(tableReplaceList, '{table,r,cas'+str(configColumn[i]))
            data = data.replace('save,N2_'+vars+'.dat','save,N2_'+vars+'_'+''.join(configCorresponsingToColumn[i])+'.dat')

            with open(inPath+'/'+newFilename, 'w') as g:
                g.write(data)
                g.close()
                print ("Created new file: ", newFilename)
                
def createNewFile_IC(configColumn,configCorresponsingToColumn,file,inPath):
    for i in range(0, len(configColumn)):
        newFilename=file[0:-6]+"".join(configCorresponsingToColumn[i])+"_IC.in"
        #print newFilename

        generalInFile = file[0:-4]+".in"
        #print generalInFile

        if os.path.exists(newFilename):
            print ("File exists: ", newFilename)
            continue

        print ("Creating: ", newFilename)

        with open(inPath+'/'+generalInFile, 'r') as f:
            data=f.read()

            #Find the line where the table is printed out. This needs to be replaced
            tableReplaceList=""
            recordBool = False
            for j in range(0,len(data)):
                if data[j]=="{" and data[j+1]=="t":
                    recordBool = True

                if data[j] == ";":
                    recordBool = False

                if recordBool:
                    tableReplaceList+=data[j]

            vars=file.split("-")[0][3:]#The three varibles used to distinguish inner valence

            sym = data.split('wf,')[3][3]
    
            data = data.replace("!Input natorb,state=8.1; before orbital, for orbital you want to find","")
            data = data.replace("!Input configuration before ' element","")
            data = data.replace('!moldenname','moldenname')
            data = data.replace('!put,','put,')
            data = data.replace('$rad$_','$rad$_'+vars+'_'+''.join(configCorresponsingToColumn[i]))
            data = data.replace('orbital,2144.2', 'natorb,state='+str(configColumn[i])+'.'+sym+';orbital,2144.2')
            data = data.replace(tableReplaceList, '{table,r,cas'+str(configColumn[i]))
            data = data.replace('IC.dat',''.join(configCorresponsingToColumn[i])+'.dat')

            with open(inPath+'/'+newFilename, 'w') as g:
                g.write(data)
                g.close()
                print ("Created new file: ", newFilename)

def analyseOutputs_CreateNewInputs_I(outputsPath,inputsPath):
    
    allOutFiles= os.listdir(outputsPath)

    #varsList, is a list of the three molpro variables, electron number, symmetry, spin
    #configsList is a list of the configurations for each of these three variables
    #i.e.   varsList[1]=[11,2,1]
    #       configsList[1]=[[2,2,2,0,1,2,2],[2,2,2,2,1,0,2],[2,2,2,2,1,2,0]]
    #The variables 11,2,1 are used to produce all the three configurations above
    varsList,configsList = findInputsToCreate_I(inputsPath)

    try:
        os.remove(outputsPath+"/columnsDataInner")
        os.remove(outputsPath+"/innFilesWithMissingConfigs")
    except:
        pass

    multiCollumnslist=list()
    repeatAndIncreaseStates=list()
    #Scan over all output files
    for file in allOutFiles:
        multiFirst=False
        multiBool=False
        recording=False
        dataIndices=list()
        configColumn=list()
        configCorresponsingToColumn=list()
    
        #Find the files we are looking for, that end with _I.out
        if file.endswith("_I.out") and len(file.split("_")) < 6:

            print (file)
		
            #Get the three molpro variables for the file (nelec,sym,spin) from file title i.e. 13,1,1
            varsFile=file.split('_')[1:4]
            varsFile=str('_'.join(varsFile))

        else: continue
	
        #Open output file and read lines
        with open(outputsPath+'/'+file, 'r') as f:
            lines=f.readlines()
	
        #--------------------------------------------------------------------------------------
        #--------------Record indices of data in output file + carry out tests-----------------
        #--------------------------------------------------------------------------------------
    
        #Pass the lines in method. The method finds the indices where the data
        #starts and ends for each distance accounted for.
        #e.g. dataIndices=[14,36,105,127,250,272,...] 14-36 is the indices of the first
        #nuclear distance data, 105-127 is the indices of the second nuc distance data.
        dataIndices=findDataIndices_I(lines)
        
        #Find how many distances were used to check if the dataIndices are the right dimensions
        #It should be the case that dataIndices = 2 x len(distancesArray)
        equilDistUsed = findEquilDist(lines)
        numOfDistances, equilIndex = findNumOfDistances_findEquilibriumDistIndex(lines, equilDistUsed)

        #Test that all dataIndices have been recorded by checking they have the correct size.
        if len(dataIndices) != numOfDistances*2 :
            print ("Data Indices not the right size, exiting ", len(dataIndices))
            exit(0)

        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------

        #Record the energy values for each nuclear distance
        eqEnergyList=list()
        for i in range(1,len(dataIndices),2):
            eqEnergy=lines[dataIndices[i]-1].split('      ')
            eqEnergyList.append(float(eqEnergy[2]))

        #Equilibrium nuclear distance relabelled
        eqDistanceIndex=equilIndex



        #Reminder: orbitals for N2 are given in molpro 1.1, 1.5, 2.1, 2.5, 1.2, 1.3, 3.1
        #However, when they are given as CI coefficients they are outputted
        #in a different form. That is is:
        #222 2 2  220 0 0 is the ground state
        #22a 2 2  220 0 0 is the first excited state, etc.
        
        #First 3 numbers represent orbitals 1.1, 2.1, 3.1
        #Fourth number represents orbital 1.2
        #Fifth number represents orbital 1.3
        #Six, seven and eight, represents orbitals 1,5, 2.5 and 3.5
        #The final two represent the orbitals 1.6 and 1.7.
        #These are all the orbitals in our active space, 10 in total.
        #If user changes active space these need to be adjusted
        
        #It is also the case, that orbitals with one electron, might be shown with
        #one of the following four characters: a, b, \, /. We don't always know which
        #We therefore migh be looking for configuration 2aa 2 a  220 0 0, or 2/\ 2 /  220 0 0 etc.
        
        #We need to transform each configuration from 2222222 to 222 2 2  220 0 0
        #We need to take into account the different possibilities for open orbitals
        #where each character a, b, \, / might be used. Finally we need to find the
        #configuration we want and get its coefficients at the neutral N2
        #equilibrium position.
        #From there we will find the biggest coefficient

        #--------------------------------------------------------------------------------------
        #---------------Loop through equilibrium data and find config of interest--------------
        #--------------------------------------------------------------------------------------
        
        for i in range(0,len(varsList)):
            if varsList[i] == varsFile:
                
                #Create an initial guess for the configuration. In place of every open
                #orbital, the character "a" is placed.
                #e.g. 2112211 beomes 2aa 2 a a20 0 0
                for con in configsList[i]:

                    conStr=createConfigForCIcoefficients(con)
            
                    count=0
                    conFound=False

                    #Look for config in equilibrium nuclear position of .out file.
                    #If you find it exit while loop, if you don't find it, randomly change
                    #the "a" characters to another character b, / or \. Repeat 1000 times,
                    #until you find it. If you don't find it there must be an error
                    while conFound==False:
                        #Loop over data at neutral N2 nuclear distance
                        for i in range(dataIndices[2*eqDistanceIndex],dataIndices[2*eqDistanceIndex+1]):
                            
                            line=lines[i].split('        ')
                
                            #If config is found in .out file, exit:
                            if conStr in line[0]:
                                conFound=True
                                
                                maxNumIndex,maxNum=findMaxCoeffIndex(line) #Find index of the biggest coefficient

                                #Degenerate configurations are found to have the same index.
                                #Therefore, if this occurs we reassign the index value of
                                #the second largest coefficient to be the column of data we want
                                if maxNumIndex in configColumn:
                                    #Take second largest coefficient. This is for degenerate cofnigurations
                                    maxNumIndex=findSecondMaxCoeffIndex(line,maxNum)
                                
                                configColumn.append(maxNumIndex)
                                configCorresponsingToColumn.append(con)

                                #Method NOT USED CURRENTLY
                                #Once found, check that this configuration appears in all distances used 
                                #checkConfigAppearsForAllDistances(dataIndices,lines,"inner")
                                
                        #If config is not found, randomly change the a's and b's around. Then the while loop will rerun
                        #and you will recheck with the new configuration.
                        #This is needed because sometimes Molpro writes orbitals with 1 electron with either a, b, \, or /
                        #but we don't know which one
                        if conFound ==False:
                            print ("Config was not found, changing it randomly from ", conStr)
                            conStr = randomlyChangeConfigurationString(conStr)
                            print ("To: ", conStr)
                                
                        #If we try 1000 random variations and none of them work, there must be an error. Exit code
                        if count==1000:
                            print ("Error, config was not found after 1000 iterations")
                            print ("Config not found: ", con)
                            print ("Last string used: ", conStr)
                            print ("Looking in file: ", file)
                            repeatAndIncreaseStates.append(file)
                            break
                                
                        count+=1

                    print ("Exited while loop, last config used: ", conStr)
                    empty=""
                    conStr=empty
                  
        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
  
        print ("")
        print ("Position of each configuration: ", configColumn, " for configs: ", configCorresponsingToColumn)

	#Output data regarding which index represents each configuration:
        outputData_I(configColumn,configCorresponsingToColumn,file,outputsPath)
	
        #NOT USED
	#Check if an index represents two or more configs
        #if len(configColumn) != len(set(configColumn)):
	#    print ("A column represents two or more configs. Exiting")
	#    multiCollumnslist.append(file)
	#    multiCollumnslist.append(eqDistanceIndex)
	#    multiCollumnslist.append(configColumn)
	#    multiCollumnslist.append(configCorresponsingToColumn)
	    #exit(0)

        #Create the new .in files for the configurations found
        createNewFile_I(configColumn,configCorresponsingToColumn,file,inputsPath)

def analyseOutputs_CreateNewInputs_IC(outputsPath,inputsPath):
    
    allOutFiles= os.listdir(outputsPath)

    #varsList, is a list of the three molpro variables, electron number, symmetry, spin
    #configsList is a list of the configurations for each of these three variables
    #i.e.   varsList[1]=[11,2,1]
    #       configsList[1]=[[2,2,2,0,1,2,2],[2,2,2,2,1,0,2],[2,2,2,2,1,2,0]]
    #The variables 11,2,1 are used to produce all the three configurations above
    varsList,configsList,restrictList = findInputsToCreate_IC(inputsPath)

    try:
        os.remove(outputsPath+"/columnsDataInnerCore")
        os.remove(outputsPath+"/innCoreFilesWithMissingConfigs")
    except:
        pass


    multiCollumnslist=list()
    repeatAndIncreaseStates=list()
    #Scan over all output files
    for file in allOutFiles:
        multiCounter=0
        dataIndices=list()
        configColumn=list()
        configCorresponsingToColumn=list()
    
        #Find the files we are looking for, that end with I.out
        if file.endswith("IC.out") and len(file.split("_")) < 5:

            print (file)
        
            #Find the variables that distinguish each set of configurations
            varsFile=file.split('-')[0][3:]
            
            restrictFile=file.split("-")[1:-1]
   
        else: continue
 
        #Open output file and read lines
        with open(outputsPath+'/'+file, 'r') as f:
            lines=f.readlines()
       
        #--------------------------------------------------------------------------------------
        #--------------Record indices of data in output file + carry out tests-----------------
        #--------------------------------------------------------------------------------------
 
        #Pass the lines in method. The method finds the indices where the data
        #starts and ends for each distance accounted for.
        #e.g. dataIndices=[14,36,105,127,250,272,...] 14-36 is the indices of the first
        #nuclear distance data, 105-127 is the indices of the second nuc distance data.
        dataIndices=findDataIndices_IC(lines,multiCounter)
        
        #Find how many distances were used to check if the dataIndices are the right dimensions
        #It should be the case that dataIndices = 2 x len(distancesArray)
        equilDistUsed = findEquilDist(lines)
        numOfDistances, equilIndex = findNumOfDistances_findEquilibriumDistIndex(lines, equilDistUsed)

        #Make sure the dataIndices have the correct size.
        #In default case it is fixed to 58.
        if len(dataIndices) != numOfDistances*2 :
            print ("Data Indices not the right size, exiting ", len(dataIndices))
            exit(0)

        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------

        #Record the energy values for each nuclear distance
        eqEnergyList=list()
        for i in range(1,len(dataIndices),2):
            eqEnergy=lines[dataIndices[i]-1].split('      ')
            eqEnergyList.append(float(eqEnergy[2]))

        #Equilibrium nuclear distance relabelled
        eqDistanceIndex=equilIndex



        #Reminder: orbitals for N2 are given in molpro 1.1, 1.5, 2.1, 2.5, 1.2, 1.3, 3.1
        #However, when they are given as CI coefficients they are outputted
        #in a different form. That is is:
        #222 2 2  220 0 0 is the ground state
        #22a 2 2  220 0 0 is the first excited state, etc.
        
        #First 3 numbers represent orbitals 1.1, 2.1, 3.1
        #Fourth number represents orbital 1.2
        #Fifth number represents orbital 1.3
        #Six, seven and eight, represents orbitals 1,5, 2.5 and 3.5
        #The final two represent the orbitals 1.6 and 1.7.
        #These are all the orbitals in our active space, 10 in total.
        #If user changes active space these need to be adjusted
        
        #It is also the case, that orbitals with one electron, might be shown with
        #one of the following four characters: a, b, \, /. We don't always know which
        #We therefore migh be looking for 2aa 2 a  220 0 0, or 2/\ 2 /  220 0 0 etc.
        
        #We need to transform each configuration from 2222222 to 222 2 2  220 0 0
        #We need to take into account the different possibilities for open orbitals
        #where each character a, b, \, / might be used. Finally we need to find the
        #configuration we want and get its coefficients at the neutral N2
        #equilibrium position.
        #From there we will find the biggest coefficient
        
        #--------------------------------------------------------------------------------------
        #---------------Loop through equilibrium data and find config of interest--------------
        #--------------------------------------------------------------------------------------

        for i in range(0,len(varsList)):
            if varsList[i] == varsFile and restrictList[i]==restrictFile:
                
                #Create an initial guess for the configuration. In place of every open
                #orbital, the character "a" is placed.
                #e.g. 2112211 beomes 2aa 2 a a20 0 0
                for con in configsList[i]:

                    conStr=createConfigForCIcoefficients(con)
            
                    count=0
                    conFound=False
                    #Look for config in equilibrium nuclear position of .out file.
                    #If you find it exit while loop, if you don't find it, randomly change
                    #the "a" characters to another character b, / or \. Repeat 1000 times,
                    #until you find it. If you don't find it there must be an error
                    while conFound==False:
                        #Loop over data at neutral N2 nuclear distance
                        for i in range(dataIndices[2*eqDistanceIndex],dataIndices[2*eqDistanceIndex+1]):
    
                            line=lines[i].split('        ')
                
                            #If config is found in .out file, exit:
                            if conStr in line[0]:
                                conFound=True
                                
                                maxNumIndex,maxNum=findMaxCoeffIndex(line) #Find index of the biggest coefficient

                                #Degenerate configurations are found to have the same index.
                                #Therefore, if this occurs we reassign the index value we therefore asign
                                #the second largest coefficient to be the column of data we want
                                if maxNumIndex in configColumn:
                                    #Take second largest coefficient. This is for degenerate cofnigurations
                                    maxNumIndex=findSecondMaxCoeffIndex(line,maxNum)
                                
                                configColumn.append(maxNumIndex)
                                configCorresponsingToColumn.append(con)

                                #Once found, check that this configuration appears in all 29 distances
                                #checkConfigAppearsForAllDistances(dataIndices,lines,"coreinner")
                               
                        #If config is not found, randomly change the a's and b's around. Then the while loop will rerun
                        #and you will recheck with the new configuration.
                        #This is needed because sometimes Molpro writes orbitals with 1 electron with either a, b, \, or /
                        #but we don't know which one
                        if conFound ==False:
                            #print ("Config was not found, changing it randomly from ", conStr)
                            conStr = randomlyChangeConfigurationString(conStr)
                            #print ("To: ", conStr)
                                
                        #If we try 1000 random variations and none of them work, there must be an error. Exit code
                        if count==1000:
                            print ("Error, config was not found after 1000 iterations")
                            print ("Config not found: ", con)
                            print ("Last string used: ", conStr)
                            print ("Looking in file: ", file)
                            repeatAndIncreaseStates.append(file)
                            exit(0)
                                
                        count+=1

                    print ("Exited while loop, last config used: ", conStr)
                    empty=""
                    conStr=empty
                
        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------
    
        print ("")
        print ("Position of each configuration: ", configColumn, " for configs: ", configCorresponsingToColumn)

        #Output data regarding which index represents each configuration:
        outputData_IC(configColumn,configCorresponsingToColumn,file,outputsPath)
    
        #NOT USED
        #Check if a index represents two or more configs
        #if len(configColumn) != len(set(configColumn)):
        #    print ("A column represents two or more configs. Exiting")
        #    multiCollumnslist.append(file)
        #    multiCollumnslist.append(eqDistanceIndex)
        #    multiCollumnslist.append(configColumn)
        #    multiCollumnslist.append(configCorresponsingToColumn)
            #exit(0)

        #Create the new .in files for the configurations found
        createNewFile_IC(configColumn,configCorresponsingToColumn,file,inputsPath)

#
#  makeMolproInputs_CASSCF.py
#
#  Copyright 2023 Antonis Hadjipittas
#

import sys
import os
from copy import deepcopy

#The orbitals of N2
orbs=[1.1,1.5,2.1,2.5,1.2,1.3,3.1]
IrrRepsNumbering=[1,5,1,5,2,3,1]

#The orbitals of the N2 active space we employ
allOrbs=[1.1,1.5,2.1,2.5,1.2,1.3,3.1,1.6,1.7,3.5]
allIrrRepsNumbering=[1,5,1,5,2,3,1,6,7,5]

#Return number of electrons
def getElectronNumber(config):
    return sum(config)
    
def getOcc(config):
    n1n1Occ=1 if config[0]!=0 else 0
    n1n5Occ=1 if config[1]!=0 else 0
    n2n1Occ=1 if config[2]!=0 else 0
    n2n5Occ=1 if config[3]!=0 else 0
    n1n2Occ=1 if config[4]!=0 else 0
    n1n3Occ=1 if config[5]!=0 else 0
    n3n1Occ=1 if config[6]!=0 else 0

    Occ1=n1n1Occ+n1n2Occ+n1n3Occ
    Occ5=n1n5Occ+n2n5Occ

    Occ = [Occ1,n1n2Occ,n1n3Occ,0,Occ5,0,0,0]

    return Occ

#Return orbitals with 1 electron (open orbitals)
def getOpenOrbitals(config):

    n1n1Open=1.1 if config[0]==1 else 0
    n1n5Open=5.1 if config[1]==1 else 0
    n2n1Open=2.1 if config[2]==1 else 0
    n2n5Open=2.5 if config[3]==1 else 0
    n1n2Open=1.2 if config[4]==1 else 0
    n1n3Open=1.3 if config[5]==1 else 0
    n3n1Open=3.1 if config[6]==1 else 0
    
    Open=[n1n1Open, n1n5Open, n2n1Open, n2n5Open, n1n2Open, n1n3Open, n3n1Open]
    
    return Open
    
# The numbers below represent the irreducible representations of D2h as Molpro reads them
# (see: https://www.molpro.net/info/2015.1/doc/manual/node36.html) When 2 irr. 
#representations are added together they give another irr. representation. 
#These additions are shown according to how molpro reads them (numbers 1 to 8) below:
#   1+1=1, 1+2=2, 2+2=1 (cancel out), 1+3=3, 3+3=1, 3+2=4, 5+1=5, 5+5=1, 5+2=6, 5+3=7, 2+3+5=8
def getSymmetry(config):
    symList=list()
    for i in range(0,len(config)):
        if config[i]==1:
            symList.append(IrrRepsNumbering[i])
    
    symmetry=1
    if (len(symList)>0):
        #Remove duplicate values since they cancel out, i.e. 5+5=1, 3+3=1, 2+2=1
        symList=removeDuplicateSym(symList)
        
        #Remove number 1 from symmetries as it doesn't have effect (like identity operator)
        for x in symList:
            if x==1:
                symList.remove(1)
        
        total=sum(symList) if (len(symList)>0) else 0

        if total==2 : symmetry=2 #symmetry x
        if total==3 : symmetry=3  #symmetry y
        if (total==5 and len(symList)==2) : symmetry=4  #symmetry xy (2+3)
        if (total==5 and len(symList)==1) : symmetry=5  #symmetry z
        if total==7 : symmetry=6 #symmetry xz (2+5)
        if total==8 : symmetry=7  #symmetry yz (3+5)
        if total==10 : symmetry=8 #symmetry xyz (2+3+5)
        
    return symmetry

def checkCoreAndInnerCoreManually(core,innercore,extraCoreBool):
    allGoodBool=True
    for l in range(0,len(core)):
        for k in range(1,len(core[l])):
            for m in range(0,len(innercore)):
                if extraCoreBool == False:
                    if core[l][k] in innercore[m][2:]:
                        allGoodBool=False
                        return allGoodBool
                if extraCoreBool == True:
                    if core[l][k] in innercore[m][2:-1]:
                        allGoodBool=False
                        return allGoodBool
    return allGoodBool

def removeDuplicateConfig(core,innercore,extraCoreCheck):
    for l in range(len(core)-1,-1,-1):
        for k in range(len(core[l])-1,0,-1):
            for m in range(0,len(innercore)):
                for n in range(2,len(innercore[m])):
                    if extraCoreCheck==True:
                        if core[l][k] == innercore[m][n] and n!=len(innercore[m])-1: 
                            core[l].pop(k)
                            return removeDuplicateConfig(core,innercore,extraCoreCheck)
                    elif extraCoreCheck==False:
                        if core[l][k] == innercore[m][n]: 
                            core[l].pop(k)
                            return removeDuplicateConfig(core,innercore,extraCoreCheck)  
    return core,innercore

def removeEntriesWithNoConfig(myList):
    for i in range(len(myList)-1,-1,-1):
        if len(myList[i]) == 1:
            myList.pop(i)

    return myList

def removeDuplicateListEntry(myList):
    for i in range(0,len(myList)):
        for j in range(1,len(myList[i])-1):
            for k in range(j+1,len(myList[i])):
                if myList[i][j]==myList[i][k]:
                    myList[i].pop(k)
                    return removeDuplicateListEntry(myList)

    return myList

def removeDuplicateSym(symList):
    for i in range(0,len(symList)):
        for j in range(i+1,len(symList)):
            if (symList[i] == symList[j]):
                symList.pop(j)
                symList.pop(i)
                if (len(symList)==2):
                    removeDuplicateSym(symList)
                break
    return symList
               

def manualAdjustments(var,text):

    #13_1_1_I.in file: Config 2212222 is the 11th root, so we add one more state     
    if var[0]==13 and var[1]==1 and var[2]==1:
        text = text.replace('state,10','state,11')
        text = text.replace('cas10(i)=energy(10);','cas10(i)=energy(10),cas11(i)=energy(11);')
        text = text.replace('cas10;','cas10,cas11;')

    #Change distances for config 1211221
    if var[0]==10 and var[1]==5 and var[2]==4:
        text = text.replace('1.13,1.17,1.20,1.25,1.30,1.35,1.40,1.60','1.13,1.15,1.20,1.25,1.30,1.35,1.40,1.50,1.60')

    return text

#Number of open orbitals = Spin
#If 2 electrons missing from different orbitals = triplet state
#If 3 electrons missing from different orbitals = quartet state etc.
#Code by default removes elecetrons from different orbitals with the same spin
#To calculate for example the case where two electrons missing from different 
#orbitals have opposite spin this function needs to be altered.
def getSpin(openList):
    spin=0
    for i in openList:
        if (i!=0):
            spin+=1
    return spin
    
def getFreeze(config):
   
    #Create 2 lists. 1 for freeze in step 1 and another for freeze in step 2
    if (1):
        freeze1=list()
        freeze2=deepcopy(orbs)
        
        #Dealing with the freezing of the core orbitals (1.1, 1.5).
        #If any core electron is missing we freeze both core orbitals 
        #in step 1 and optimise in step 2
        if (config[0]!=2) or (config[1]!=2):
            freeze1.append(orbs[0])
            freeze2.remove(orbs[0])

            freeze1.append(orbs[1])
            freeze2.remove(orbs[1])
       
        #If orbital 1simga_u (1.5) is missing an electron 
        #freeze virutal orbital 3sigma_u (3.5) in second step
        #to avoid orbital rotations
        if config[1]!=2: 
            freeze2.append(allOrbs[-1])
     
        #Dealing with the freezing of the inner valence orbital 2sigma_g (2.1)
        #If inner valence is missing an electron freeze it in first step 
        #and optimise it in second step
        if (config[2]!=2):
            freeze1.append(orbs[2])
            freeze2.remove(orbs[2])

    #If none of the above if statements holds freeze1 has no orbitals freeze2 has 
    #all orbitals (minus virutal). This means that all orbitals are optimised in 
    #a single step.

    #Turn data to strings
    freeze1str=""
    for i in range(0,len(freeze1)):
        freeze1str+=str(freeze1[i])
        if i<(len(freeze1)-1):
            freeze1str+=","
        
    freeze2str=""
    for i in range(0,len(freeze2)):
        freeze2str+=str(freeze2[i])
        if i<(len(freeze2)-1):
            freeze2str+=","
    
    return freeze1str, freeze2str
    
def getRestrict(config):
    restrict=list()
    for i in range(0,2): #Only taking into account core and innner valence orbitals.
        if (config[i]!=2):
            restrict.append(str(config[i])+","+str(config[i])+","+str(orbs[i]))
    if config[2] == 0:
        restrict.append("0,0,2.1")
    elif config[2] == 1:
        restrict.append("0,1,2.1") 
 
    return restrict
    
def getWFIC(config):
    if config[2]!='2':
        return "wf,14,1,0;wf,14,5,0;orbital,2140.2}"
        #return "wf,14,1,0;orbital,2140.2}"
    else:
        return "wf,14,1,0;orbital,2140.2}"

#Returns wavefunctions to average over for N2 neutral
def getWFC(config):
    if config[2]!='2':
        return "wf,14,1,0;wf,14,5,0;orbital,2140.2}"
    else:
        return "wf,14,1,0;wf,14,5,0;wf,14,4,0;orbital,2140.2}"

#Returns basis set aug-cc-pVQZ only
def getBasisSet_augccpVQZ():
    return "aug-cc-pVQZ"

#If core electron is missing return aug-cc-pCVQZ. Else return aug-cc-pVQZ
def getBasisSet(config):
    for i in range(2):
        if config[i]!="2":
            return "aug-cc-pCVQZ" 
    return "aug-cc-pVQZ"

#Same as above, but if 2 or more electrons are missing return cc-pV5Z for valence
#electrons or aug-cc-pCV5Z if one or more electorn is from core orbital.
#This function is not used since molpro cannot print the wavefunctions in molden
#files when these two basis sets are used
def getBasisSetAccurate(config):
    missingEl=0
    for el in config:
        if el!="2":
            missingEl += 1

    if missingEl>1:
        for i in range(2):
            if config[i]!="2":
                return "aug-cc-pCV5Z"
        return "cc-pV5Z"

    else:
        for i in range(2):
            if config[i]!="2":
                return "aug-cc-pCVQZ"
        return "aug-cc-pVQZ"

def checkCoreANdInnerCoreSize(core,innerCore,bothAfter,bothBefore,extraCoreBool):
    #TODO Check these work correctly 
    if extraCoreBool == True:
        if core+innerCore == bothBefore+bothAfter:
            return True
        else:
            return False

    elif extraCoreBool == False:
        if core+innerCore == bothBefore: 
            return True
        else:
            return False
    
    else:
        print ("Error in checking core and inner core, exiting")
        exit(0)

#This function should be used as a way to check your work. All inputs using TS-CASSCF are state averaged and printed
#This way you can compare the state averaged state with non-state averaged state for testing purposes
#After the file is created, it is not picked up by the second step of the code for analysis. It also has no way
#of outputing the wavefunctions in molden file since it is not analysed in the second step. 
#It will output the state averaged data in a file that ends with StateAv.dat
def createStateAvforCfile(title,fileContents,path):
    title = title.replace('_C.in','_StateAv.in')

    fileContents = fileContents.replace('***,','***,StateAveragedRunFor-')
    fileContents = fileContents.replace('accuracy,','state,10;accuracy,')
    fileContents = fileContents.replace('cas(i)=energy','cas1(i)=energy(1),cas2(i)=energy(2),cas3(i)=energy(3),cas4(i)=energy(4),cas5(i)=energy(5),cas6(i)=energy(6),cas7(i)=energy(7),cas8(i)=energy(8),cas9(i)=energy(9),cas10(i)=energy(10);')
    fileContents = fileContents.replace('cas;','cas1,cas2,cas3,cas4,cas5,cas6,cas7,cas8,cas9,cas10;') 
    fileContents = fileContents.replace('moldenname=','!moldenname=')
    fileContents = fileContents.replace('put,molden,','!put,molden,')
    fileContents = fileContents.replace('.dat}','stateAv.dat}') 
   
    inputFile = open(path+'/'+title, 'w+')
    inputFile.write(fileContents)
    inputFile.close()

def outputInnerData(path,allInnerAndOuter):
    inputFile = open(path+'/ConfigData', 'w+')
    for i in range(0,len(allInnerAndOuter)):
        inputFile.write(str(allInnerAndOuter[i][0][0])+"_"+str(allInnerAndOuter[i][0][1])+"_" +str(allInnerAndOuter[i][0][2])+"\n")
        for j in range(1,len(allInnerAndOuter[i])):
            for k in range(0,len(allInnerAndOuter[i][j])):
                inputFile.write(str(allInnerAndOuter[i][j][k])+",")
            inputFile.write("\n")
        inputFile.write("\n")
    inputFile.close()

def outputInnerCoreData(path,allInnerCore): 
    inputFile = open(path+'/ConfigInnerCoreData', 'w+')
    for i in range(0,len(allInnerCore)):
        inputFile.write(str(allInnerCore[i][0][0])+"_"+str(allInnerCore[i][0][1])+"_" +str(allInnerCore[i][0][2])+"\n")
        inputFile.write(str(allInnerCore[i][1])+"\n")
        for j in range(2,len(allInnerCore[i])):
            for k in range(0,len(allInnerCore[i][j])):
                inputFile.write(str(allInnerCore[i][j][k])+",")
            inputFile.write("\n")
        inputFile.write("\n")
    inputFile.close()

def outputNumberOfInputFiles(path,step):
    inFiles=0
    allInFiles = os.listdir(path)
    for file in allInFiles:
        if file.endswith(".in"):
            inFiles+=1
    fileName = open(path+'/InputFilesCreated', 'a')
    if step==1:
        fileName.write("Number of input files after 1st run: "+str(inFiles))
    elif step==2:
        fileName.write("\nNumber of input files after 2nd run: "+str(inFiles))
    fileName.close()

def MolproCASSCFInputPrint(inputconfig,core,coreInner,inner,outer,path):
    print ("Configuration: ",inputconfig)
    nElec = getElectronNumber(inputconfig)
    print ("Elec Num: ",nElec)
    Occ = getOcc(inputconfig)
    print ("Occupation: ", Occ)
    Open = getOpenOrbitals(inputconfig)
    print ("Open Orbitals: ",Open)
    Spin = getSpin(Open)
    print ("Spin: ", Spin)
    Symmetry = getSymmetry(inputconfig)
    print ("Symmetry: ", Symmetry)
    Freeze1,Freeze2= getFreeze(inputconfig)
    print ("Frozen Orbitals: ", Freeze1)
    print ("Frozen Orbitals 2: ", Freeze2)
    Restrict=getRestrict(inputconfig)
    print ("Restrict Line: ",Restrict)
 
    print (inputconfig)
    entry=[nElec,Symmetry,Spin]
    
    #Check if config will be uses core, inner-core, inner, or outer technique.
    #e.g. if core method to be used, coreBool = True. 
    #Note, that all configs that use outer technique are also produced with inner technique (outerBool=innerBool=True)
    #The same goes for some cofnigs that use core technique as well as inner-core technique (coreBool=coreInnerBool=True)
    coreBool = any(inputconfig in cons for cons in core)
    coreInnerBool = any(inputconfig in cons for cons in coreInner)
    innerBool = any(inputconfig in cons for cons in inner)
    outerBool = any(inputconfig in cons for cons in outer)
    
    if coreInnerBool==False and coreBool==False and innerBool==False and outerBool==False:
        print ("Config not found, exiting")
        exit(0)

    numStates=10 #number of states to average over in SA-CASSCF (inner) and SA-TS-CASSCF (inner-core)

    #Writing config as a string
    config=""
    for i in inputconfig:
        config+=str(i)

    #Start Printing data to file. The _1.10378 is the equilibrium distance
    #It is needed for the program to carry out the analysis in the second run.
    #In the second run the code finds this distance in the len and stores its index.
    #It then goes to this distance in the output files of the first run and finds the
    #correct root for the configuration we want. This number needs to be the exact same
    #as the one in "len=[0.70,0.80,...]" a few lines down in the input file. If you want to find the root at a different
    #index or a different molecule you need to change this manually.
    header = "***,N2_"+ str(config) + "_1.10378\n"

    headerInner = "***,N2_"+ str(entry[0]) + "_" + str(entry[1]) + "_" + str(entry[2]) + "_1.10378\n"

    wavefunction= "wf,14,1,0;orbital,2140.2}"
    wavefunctionFreeze=getWFC(config)
    wavefunctionInnerCore=getWFC(config)
    #wavefunctionInnerCore=getWFIC(config)

    #Different methods to call in order to get different basis sets
    #basisSet=getBasisSetAccurate(config)
    #basisSet=getBasisSet(config)
    basisSet=getBasisSet_augccpVQZ()

    intro = '''
print,orbitals,civector,basis

symmetry,x,y,z !use D2h symmetry
angstrom,
basis = '''+basisSet+''';
geometry={N;N1,N,r(i)}

len=[0.70,0.80,0.90,1.00,1.05,1.07,1.09,1.10378,1.11,1.13,1.17,1.20,1.25,1.30,1.35,1.40,1.60,1.80,2.00,2.25,2.50,2.75,3.00,3.50,4.00]

i=0
do ir=1,#len
i=i+1
r(i)=len(ir)

rad=len(ir)

{hf;closed,0;wf,14,1,0;save,2100.2}
{multi;closed,0;occ,3,1,1,0,3,1,1,0;start,2100.2;'''

    #Create lquant string
    inner_lquant=""
    for i in range(0,numStates-1):
        inner_lquant+=str(Symmetry-1)+","

    inner_lquant="lquant,"+inner_lquant+str(Symmetry-1)

    casRecordStr="" #Create string to record casscf energies for inner and core-inner
    casTableStr=""  #Create string to output table values
    for i in range(0,numStates):
        casRecordStr+="cas"+str(i+1)+"(i)=energy("+str(i+1)+"),"
        casTableStr+="cas"+str(i+1)+","
     
    #Remove last comma from both
    casRecordStr=casRecordStr[:-1]
    casTableStr=casTableStr[:-1]
      
    #Add a semicolon at the end of both
    casRecordStr+=";"
    casTableStr+=";"

    innerValence_Info= '''

{multi;closed,0;occ,3,1,1,0,3,1,1,0;start,2140.2;wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';state,'''+str(numStates)+''';accuracy,econv=1.d-5;orbital,2141.2}    !Input natorb,state=8.1; before orbital, for orbital you want to find
'''+casRecordStr+'''

!moldenname='N2_$rad$_'    !Input configuration before ' element
!put,molden,$moldenname.molden;orb,2141.2; 

enddo

{table,r,'''+casTableStr+'''
save,N2_'''+str(entry[0])+'_'+str(entry[1])+'_'+str(entry[2])+'''.dat}

---
'''

    outerValecne_Info= '''
    
{multi;closed,0;occ,3,1,1,0,3,1,1,0;start,2140.2;wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';accuracy,econv=1.d-5;orbital,2141.2}
cas(i)=energy;

moldenname='N2_$rad$_'''+str(config)+''''
put,molden,$moldenname.molden;

enddo

{table,r,cas;
save,N2_'''+str(config)+'''.dat}

---
'''
    
    core_restrict_info = ""
    for i in Restrict:
        core_restrict_info+="restrict,"+i+";"

    core_Info='''
    
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2140.2;freeze,'''+Freeze1+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''accuracy,econv=1.d-5;orbital,2141.2;}
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2141.2;freeze,'''+Freeze2+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''accuracy,econv=1.d-5;orbital,2142.2;}
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2142.2;freeze,'''+Freeze1+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''accuracy,econv=1.d-5;orbital,2143.2;}
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2143.2;freeze,'''+Freeze2+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''accuracy,econv=1.d-5;orbital,2144.2;}
cas(i)=energy

moldenname='N2_$rad$_'''+str(config)+''''
put,molden,$moldenname.molden; 

enddo

{table,r,cas;
save,N2_'''+str(config)+'''.dat}

---
'''

    restrictString = "_-_"
    restrictStringMolden="-"
    for i in Restrict:
        restrictElems=i.split(",")
        restrictStringMolden += restrictElems[-1]
        restrictStringMolden += "-"
        for j in restrictElems:
            restrictString += j+"_"
            #restrictStringMolden += j+"_"
        restrictString += "-_"
	#   restrictStringMolden = restrictStringMolden[:-1] + "-"
    restrictString+="IC"
    
    innerCore_Info='''

{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2140.2;freeze,'''+Freeze1+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''state,'''+str(numStates)+''';accuracy,econv=1.d-5;orbital,2141.2;}
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2141.2;freeze,'''+Freeze2+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''state,'''+str(numStates)+''';accuracy,econv=1.d-5;orbital,2142.2;}
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2142.2;freeze,'''+Freeze1+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''state,'''+str(numStates)+''';accuracy,econv=1.d-5;orbital,2143.2;}
{multi;config;closed,0;occ,3,1,1,0,3,1,1,0;start,2143.2;freeze,'''+Freeze2+''';wf,'''+str(nElec)+''','''+str(Symmetry)+''','''+str(Spin)+''';'''+core_restrict_info+'''state,'''+str(numStates)+''';accuracy,econv=1.d-5;orbital,2144.2;}
'''+casRecordStr+'''

!moldenname='N2_$rad$_'
!put,molden,$moldenname.molden;orb,2144.2;

enddo

{table,r,'''+casTableStr+'''
save,N2_'''+str(entry[0])+'_'+str(entry[1])+'_'+str(entry[2])+restrictStringMolden+'''IC.dat}

---
'''
    
    #Core and Inner valence
    if coreBool: 

        if inputconfig[:] == [1, 2, 1, 1, 2, 2, 1]:
            intro = manualAdjustments(entry,intro)           
 
        fileContents = header + intro + wavefunctionFreeze + core_Info

        title='_'.join(['N2',str(config),'C'])+'.in'
        inputFile = open(path+'/'+title, 'w+')
        inputFile.write(fileContents)
        inputFile.close()
        print ("Printing Core", title)

        #This function creates the state averaged input for the above configuraiton
        #It only outputs the PECs of 10 states and can't be used to generate molden
        #wavefunctions. Uncomment it to use it. Ideally used for testing purposes
        #createStateAvforCfile(title,fileContents,path)

    #Outer valence
    if outerBool:
        fileContents = header + intro + wavefunction + outerValecne_Info
    
        title='_'.join(['N2',str(config),'O'])+'.in'
        inputFile = open(path+'/'+title, 'w+')
        inputFile.write(fileContents)
        inputFile.close()
        print ("Printing Outer", title)

    if innerBool:
        new_innerValence_Info = manualAdjustments(entry,innerValence_Info)

        fileContents = headerInner + intro + wavefunction + new_innerValence_Info

        title='_'.join(['N2',str(entry[0]),str(entry[1]),str(entry[2])])+'_I.in'
        inputFile = open(path+'/'+title, 'w+')
        inputFile.write(fileContents)
        inputFile.close()
        print ("Printing Inner ", title)

    if coreInnerBool:
        fileContents = headerInner + intro + wavefunctionInnerCore + innerCore_Info

        title='_'.join(['N2',str(entry[0]),str(entry[1]),str(entry[2])])+str(restrictStringMolden)+'IC.in'
        inputFile = open(path+'/'+title, 'w+')
        inputFile.write(fileContents)
        inputFile.close()
        print ("Printing Inner-Core ", title)
    
    print ("")
	

def findAllStates(configs,path):

    allInfo=list()
    allFreezeInfo=list()
    for inputconfig in configs:
        nElec = getElectronNumber(inputconfig)
        Open = getOpenOrbitals(inputconfig)
        Spin = getSpin(Open)
        Symmetry = getSymmetry(inputconfig)
        variables = [nElec,Symmetry,Spin]

        Freeze1,Freeze2 = getFreeze(inputconfig)
        Restrict = getRestrict(inputconfig)
        
        #print (inputconfig, nElec, Open, Spin, Symmetry, variables, Freeze1, Freeze2, Restrict)

        #Create allInfo. A list of configs separated according to the three primary variables that 
        #Molpro needs nElec, spin, symetry, to find the right configuration. 
        #i.e. The next two loops create:
        #allInfo = [[[14,1,0],[2,2,2,2,2,2,2,2]],[[13,1,1],[2,2,2,2,2,2,1],[2,2,1,2,2,2,2],[1,2,2,2,2,2,2]],...]
        #allFreezeInfo is the same (for all configs) but also includes frozen and restricted data. i.e.
	#allFreezeInfo = [[[14, 1, 0], [[2, 2, 2, 2, 2, 2, 2], '', '1.1,1.5,2.1,2.5,1.2,1.3,3.1', []]],...,
	# [[11, 3, 3], [[1, 2, 1, 2, 2, 1, 2], '1.1,1.5,2.1', '2.5,1.2,1.3,3.1', ['1,1,1.1', '0,1,2.1']], 
        #              [[1, 2, 2, 2, 2, 1, 1], '1.1,1.5', '2.1,2.5,1.2,1.3,3.1', ['1,1,1.1']],...]]
	# for above example, 11,3,3 are the three variables of nElec, spin and symmetry.
	# 1212212 is the configuration '1.1,1.5,2.1' are the orbitals to freeze in step 1
	# '2.5,1.2,1.3,3.1' are the orbitals to freeze in step 2 and ['1,1,1.1', '0,1,2.1'] are the electron restrictions in 
	# orbitals 1.1 (restricted to 1) and 2.1 (restricted between 0 and 1). If no orbitals will be frozen look at 14,1,0 case

        check=False
        for i,element in enumerate(allInfo):
            if variables==element[0]:
                allInfo[i].append(inputconfig)
        
                empty4=list()
                allFreezeInfo[i].append(empty4)
                allFreezeInfo[i][-1].append(inputconfig)
                allFreezeInfo[i][-1].append(Freeze1)
                allFreezeInfo[i][-1].append(Freeze2)
                allFreezeInfo[i][-1].append(Restrict)

                check=True
 
        if check==False:
            empty=list()
            allInfo.append(empty)
            allInfo[-1].append(variables)
            allInfo[-1].append(inputconfig)

            empty2=list()
            allFreezeInfo.append(empty2)
            allFreezeInfo[-1].append(variables)

            empty3=list()
            allFreezeInfo[-1].append(empty3)
            allFreezeInfo[-1][-1].append(inputconfig)
            allFreezeInfo[-1][-1].append(Freeze1)
            allFreezeInfo[-1][-1].append(Freeze2)
            allFreezeInfo[-1][-1].append(Restrict)

    #-----------------------------------------------------------------------------
    #------Separate all configs that use inner-core (SA-TS-CASSCF) technique------
    #-----------------------------------------------------------------------------
    pList=list()
    for i in range(0,len(allFreezeInfo)):

        #Add three variables nElec, spin and symmetry to pList
        pList.append([allFreezeInfo[i][0]])

        #Scan through all configs for each set of the three variables nElec, spin, symmetry
        #If 2 configs have the same freeze and restrict specifications add them to the list
        for j in range(1,len(allFreezeInfo[i])-1):
            for k in range(j+1,len(allFreezeInfo[i])):

                if j != k and (allFreezeInfo[i][j][0][0]!=2 or allFreezeInfo[i][j][0][1]!=2 or allFreezeInfo[i][j][0][2]!=2) and allFreezeInfo[i][j][1:] == allFreezeInfo[i][k][1:]:
                    pList[-1].append(allFreezeInfo[i][j])
                    pList[-1].append(allFreezeInfo[i][k])

    #Remove duplicate entries
    pList = removeDuplicateListEntry(pList)

    #Remove single entries, i.e. entries with no configurations
    pList = removeEntriesWithNoConfig(pList) 

    #Clean the pList further, by removing uneccessary info 
    #Remove data of orbitals to be frozen in step 1 and 2. Keep only configs and orbital electrons restrictions.
    for i in range(0,len(pList)):
        for j in range(1,len(pList[i])):
            pList[i][j].pop(2)
            pList[i][j].pop(1)

    #Sort pList according to orbital electron restrictions. 
    for i in range(0,len(pList)):
        pList[i][1:] = sorted(pList[i][1:], key=lambda x: (x[-1]))

    #From pList separate configs that will use inner-core (SA-TS-CASSCF) and core (TS-CASSCF) technique.
    #Store the configs that will use inner-core to the allInnerCore list 
    c=0 
    allInnerCore=list()   
    for i in range(0,len(pList)):

        allInnerCore.append([pList[i][0]])	    #Add three variables
        allInnerCore[i+c].append(pList[i][1][1])    #For each set of variables add first set of electron restrictions

        for j in range(1,len(pList[i])):
            if allInnerCore[i+c][1] != pList[i][j][-1]:
                c+=1
                allInnerCore.append([pList[i][0]])
                allInnerCore[i+c].append(pList[i][j][-1])
                allInnerCore[i+c].append(pList[i][j][0])
            else:
                allInnerCore[i+c].append(pList[i][j][0])

    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------

    #From allInfo separate configs according to technique used.
 
    allOuter=list()		#Configs that use outer (CASSCF) technique
    allInnerAndOuter=list()	#Configs that use inner (SA-CASSCF) technique
    allCore=list()		#Configs that use either the core (TS-CASSCF) or the inner-core (SA-TS-CASSCF) technique

    for i in range(0,len(allInfo)):
        empty1=list()
        empty2=list()
        empty3=list()
        allOuter.append(empty1)
        allInnerAndOuter.append(empty2)
        allCore.append(empty3)
        allOuter[-1].append(allInfo[i][0])
        allInnerAndOuter[-1].append(allInfo[i][0])
        allCore[-1].append(allInfo[i][0])
        for j in range(1,len(allInfo[i])):
            totalCharge=sum(allInfo[i][j])
            if allInfo[i][j][0]!=2 or allInfo[i][j][1]!=2 or allInfo[i][j][2]==0 or (allInfo[i][j][2]==1 and totalCharge<13):
                allCore[-1].append(allInfo[i][j])
            else:
                allInnerAndOuter[-1].append(allInfo[i][j])
   
        if len(allInnerAndOuter[-1])>1:
            allOuter[-1].append(allInnerAndOuter[i][-1])

    #Remove all entries without any configs for inner (SA-CASSCF)
    for l in range(len(allInnerAndOuter)-1,-1,-1):
        if len(allInnerAndOuter[l])==1:
            allInnerAndOuter.pop(l)

    #Remove all entries without any configsi for outer (CASSCF)
    for l in range(len(allOuter)-1,-1,-1):
        if len(allOuter[l])==1:
            allOuter.pop(l)
 
    #Remove all entries without any configs for core (TS-CASSCF)
    for l in range(len(allCore)-1,-1,-1):
        if len(allCore[l])==1:
            allCore.pop(l)

    #-----------------------------------------------------------------------------
    #---------Separate core (TS-CASSCF) and inner-core (SA-TS-CASSCF)-------------
    #-----------------------------------------------------------------------------

    configsCoreOrInnerCore = sum(len(i) for i in allCore) - len(allCore) #Configs in allCore (core + inner-core)

    createExtraCoreBool=False
    #allCore contains configs that use either core (TS-CASSCF) or inner core (SA-TS-CASSCF) technique.
    #allCoreInner only contains configs that use the inner-core (SA-TS-CASSCF) technique.
    #We compare the two and remove from allCore, the configs that appear in allInnerCore
    allCore,allInnerCore=removeDuplicateConfig(allCore,allInnerCore,createExtraCoreBool)

    configsCore = sum(len(i) for i in allCore) - len(allCore) #Configs in allCore after adjustment (core only)
    configsInnerCore = sum(len(i) for i in allInnerCore) - 2*len(allInnerCore) #Configs in allInnerCore after adjustment (inner-core only)
    configsInBoth = len(allInnerCore)

    #Test if the separation of core and inner-core was done correctly
    if checkCoreANdInnerCoreSize(configsCore,configsInnerCore,configsInBoth,configsCoreOrInnerCore,createExtraCoreBool) == False:
        print ('Error in separating core and inner core. Exiting.')
        exit(0)

    #Another check to make sure separation of configs was successful  
    if(checkCoreAndInnerCoreManually(allCore,allInnerCore,createExtraCoreBool) == False):
        print ("Error in the configurations of allCore and allInnerCore. Exiting")
        exit(0)

    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------
 
    #Create file ConfigData, which contains information about which configurations belong to which set of variables
    outputInnerData(path,allInnerAndOuter)
    
    #Create file ConfigInnerCoreData, which contains information about which conifugrations belong to which set of variables and 
    #frozen orbitals.
    outputInnerCoreData(path,allInnerCore)

    return allCore, allInnerCore, allInnerAndOuter, allOuter


def createMolproInputs(path):
    path=path[:-1]
    #Generate and store all possible electron configurations up to charge 4+
    allConfigs=list()
    for i1 in range(0,3):
        for i2 in range(0,3):
            for i3 in range(0,3):
                for i4 in range(0,3):
                    for i5 in range(0,3):
                        for i6 in range(0,3):
                            for i7 in range(0,3):
                                if i1+i2+i3+i4+i5+i6+i7>=10:
                                    config = [i1,i2,i3,i4,i5,i6,i7]
                                    allConfigs.append(config)

    print ("Separating the configs according to what technique (out of 4) to be used.")
    print (len(allConfigs))
    #outer = CASSCF, inner = SA-CASSCF, core = TS-CASSCF, coreInner = SA-TS-CASSCF
    core,coreInner,inner,outer=findAllStates(allConfigs,path)

    for config in allConfigs:
        MolproCASSCFInputPrint(config,core,coreInner,inner,outer,path)

    #Write to a file how many input files were created in first run
    outputNumberOfInputFiles(path,1)
     

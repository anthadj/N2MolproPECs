# N2MolproPECs
A python script that automatically creates the Molpro input files necessary to generate the PECs 
of all N2 ions with up to four electrons missing

# Description 

# Dependencies
Python3.8.6           - Needed to run the code
MOLPRO2020.1					- Needed to run the input files once created

Once the above dependencies have been installed proceed to the execution

# How to execute
- python main.py     																				(Code step 1: Creates file structure + initial inputs)
- molpro < N2_*.in > ../outputs/N2_*.out          					(Run all input files from input folder. Output results into outputs folder)
- python main.py																						(Code step 2: Checks all inputs ran successfully. Cleans outputs directory.
																								  					 Analyses SA-CASSCF and SA-TS-CASSCF. Produce new specific
  																													 SA-CASSCF and SA-TS-CASSCF input files that produce wavefunctions)
- molpro < N2_*_IC.in > ../outputs/N2_*_IC.out						  (Run all new SA-TS-CASSCF input files)
- molpro < N2_*_*_*_*_I.in > ../outputs/N2_*_*_*_*_I.out	  (Run all new SA-CASSCF input files)
- python main.py																						(Code step 3: Check all inputs from above two lines ran successfully.
  																													 Clean outputs directory)

# Help and collaboration
For any help running/understanding the code or possible collaborations please email:
antonis.hadjipittas@gmail.com
	

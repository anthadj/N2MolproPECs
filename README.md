# N2MolproPECs 
A python script that automatically creates the Molpro input files necessary to generate the PECs 
of all N2 ions with up to four electrons missing

# Description 
Using three pre-existing techniques along with a fourth one, we generate the potential energy curves (PECs) of nitrogen molecule ions with up to four electrons missing. The code produces the inputs files necessary to generate the PECs using the quantum chemistry package Molpro. The code can also be adjusted to produce PECs for nitrogen molecules with more electrons, as well as generate the PECs for different molecules.

# Dependencies 
- Python3.8.6        (Needed to run code)
- MOLPRO2020.1	     (Needed to run the input files once created)

Once the above dependencies have been installed proceed to the execution

# How to execute 
- python main.py   (Code step 1, run from "src" directory: Creates file structure + initial inputs)
- molpro < N2_\*.in > ../outputs/N2_\*.out   (Run all input files from "inputs" directory. Output results into outputs folder)
- python main.py   (Code step 2, run from "src" directory: Checks all inputs ran successfully. Cleans outputs directory. Analyses SA-CASSCF and SA-TS-CASSCF. Produce new specific SA-CASSCF and SA-TS-CASSCF input files that produce wavefunctions)
- molpro < N2_\*\_IC.in > ../outputs/N2_\*\_IC.out   (Run all new SA-TS-CASSCF input files from "inputs" directory)
- molpro < N2_\*\_\*\_\*\_\*\_I.in > ../outputs/N2_\*\_\*\_\*\_\*\_I.out   (Run all new SA-CASSCF input files from "inputs" directory)
- python main.py   (Code step 3, run from "src" directory: Check all inputs from above two lines ran successfully. Clean outputs directory)

# Help and Collaborations 
For any help or for possible collaborations (adjusting for different molecule or other similar issues) please email:
antonis.hadjipittas@gmail.com

# License 



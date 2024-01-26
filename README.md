# N2MolproPECs 
A python script that automatically creates the Molpro input files necessary to generate the PECs 
of N2 ions with up to four electrons missing

# Description 
Using three pre-existing techniques along with a fourth one, we generate the potential energy curves (PECs) of nitrogen molecule ions with up to four electrons missing. The code produces the inputs files necessary to generate the PECs using the quantum chemistry package Molpro. The code can also be adjusted to produce PECs for nitrogen molecules with more electrons missing, as well as generate the PECs for different molecules.

# Dependencies 
- `Python3.9`        (Needed to run code)
- `MOLPRO2020.1`	   (Needed to run the input files once created)

Once the above dependencies have been installed proceed to the execution

# How to execute 
Download whole "src" directory. Then follow steps below.

1. Code step 1, run command below from "src" directory. Creates file structure + initial inputs
```
python main.py 
```

2. Run all input files from "inputs" directory. Output results into outputs folder. \* represents all possible strings found on inpit files starting with N2_ and ending with .in 
```
molpro < N2_*.in > ../outputs/N2_*.out 
```

3. Code step 2, run from "src" directory: Checks all inputs ran successfully. Cleans outputs directory. Analyses SA-CASSCF and SA-TS-CASSCF. Produce new specific SA-CASSCF and SA-TS-CASSCF input files that produce wavefunctions
```
python main.py 
```

4. Run all new SA-TS-CASSCF input files from "inputs" directory. \* represents all possible strings found on inpit files starting with N2_ and ending with _IC.in 
```
molpro < N2_*_IC.in > ../outputs/N2_*_IC.out 
```

5. Run all new SA-CASSCF input files from "inputs" directory. \* represents all possible strings found on inpit files starting with N2_ and ending with _I.in 
```
molpro < N2_*_*_*_*_I.in > ../outputs/N2_*_*_*_*_I.out 
```

6. Code step 3, run from "src" directory: Check all inputs from above two lines ran successfully. Clean outputs directory.
```
python main.py 
```

# Help and Collaborations 
For any help or collaborations please email:
antonis.hadjipittas@gmail.com

# License 
Apache License 2.0


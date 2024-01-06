<img src="https://github.com/TusharRakheja/mgen/raw/main/merge/title.png" width="auto" height="100px" />

___

**merge** is a tool to merge a raw data file into a Plink-style or Eigenstrat-style set.

### Dependencies

- [Plink 1.90](https://www.cog-genomics.org/plink2/)
- Python 3.10 (if running on Linux or MacOS)
- [AdmixTools](https://github.com/DReichLab/AdmixTools) like `convertf` in your path

### Usage

- Download this repo and add the root directory to PATH.

- You either need to have your set in Plink format (.fam, .bim, .bed files), or in Eigestrat format (.ind, .snp, .geno files).

- If your set is in Plink format, use the `--fam`, `--bim` and `--bed` options to provide the paths to your set's files.

- If your set is in Eigenstrat format, use the `--ind`, `--snp` and `--geno` options instead.

- If you want the resulting set with the raw data file merged in to be in Eigenstrat format, then you need to use the `--ind` option and provide an .ind file, even if your original set is **not** in Eigenstrat format.

- The tool will create a directory in your current directory called `working`, and at the end of the process the merged set will be inside the `working` directory. Copy the merged set to where you want it, and delete the `working` directory before attempting another merge.

### Examples

**Note**: In the examples below, I assume you're a) running the tool on Windows, b) have Plink on Windows and c) have AdmixTools on WSL. Please see the [`Options`](#options) section for what to change in other cases.

- To merge a raw data file - say a 23andMe file - into your Plink set, and keep the result in Plink format, do:
```
$ mgen merge --fam [path to .fam] file --bim [path to .bim] --bed [path to .bed] -p plink -c convertf -d [path to raw data file] -n [name for the new sample] --sex [M|F|U] -ft 23andMe
```

- To merge a raw data file - say an AncestryDNA file - into your Plink set, and get the result in Eigenstrat format, do:
```
$ mgen merge --fam [path to .fam] file --bim [path to .bim] --bed [path to .bed] -p plink -c convertf -d [path to raw data file] -n [name for the new sample] --sex [M|F|U] -ft Ancestry --convert-to-eigenstrat --ind [path to .ind]
```

- To merge a raw data file - say a Mapmygenome file - into your Eigenstrat set, and get the result in Eigenstrat format, do:
```
$ mgen merge --ind [path to .ind] file --snp [path to .snp] --geno [path to .geno] -p plink -c convertf -d [path to raw data file] -n [name for the new sample] --sex [M|F|U] -ft Mapmygenome --convert-to-eigenstrat
```

- To merge a raw data file - say you don't know the testing company - into your Eigenstrat set, and get the result in Plink format, do:
```
$ mgen merge --ind [path to .ind] file --snp [path to .snp] --geno [path to .geno] -p plink -c convertf -d [path to raw data file] -n [name for the new sample] --sex [M|F|U]
```

### Options
```
$ mgen merge -h
usage: merge [-h] [-i IND] [-s SNP] [-g GENO] [-f FAM] [-bi BIM] [-be BED] -d
             DATA -p PLINK -n NAME -c CONVERTF [--convert-to-eigenstrat] -se
             SEX [-ft FILE_TYPE] [--turn-on-wsl-for-plink]
             [--turn-on-wsl-for-admix-tools]

Merge a raw data file into a Plink or Eigenstrat set

optional arguments:
  -h, --help            show this help message and exit
  -i IND, --ind IND     Path of the .ind file (e.g "./set.ind")
  -s SNP, --snp SNP     Path of the .snp file (e.g "./set.snp")
  -g GENO, --geno GENO  Path of the .geno file (e.g "./set.geno")
  -f FAM, --fam FAM     Path of the .fam file (e.g "./set.fam")
  -bi BIM, --bim BIM    Path of the .bim file (e.g "./set.bim")
  -be BED, --bed BED    Path of the .bed file (e.g "./set.bed")
  -d DATA, --data DATA  Path of the raw data file (e.g "./23andMe.txt")
  -p PLINK, --plink PLINK
                        Command used to invoke plink on your machine (e.g.
                        "plink")
  -n NAME, --name NAME  A name for your sample to be used in the merged
                        dataset (e.g. "tony23andMe")
  -c CONVERTF, --convertf CONVERTF
                        Command used to invoke convertf on your machine (e.g.
                        "convertf")
  --convert-to-eigenstrat
  -se SEX, --sex SEX    Sex of the sample ('M', 'F' or 'U')
  -ft FILE_TYPE, --file-type FILE_TYPE
                        Type of the raw data file ('Ancestry', '23andMe', or
                        'Mapmygenome')
  --turn-on-wsl-for-plink
                        (If running on Windows) Use Plink via WSL
  --turn-on-wsl-for-admix-tools
                        (If running on Windows) Use AdmixTools like convertf
                        via WSL

Copyright (c) 2023 Tushar Rakheja (The MIT License)
```

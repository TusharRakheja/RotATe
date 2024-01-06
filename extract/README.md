<img src="https://github.com/TusharRakheja/mgen/raw/main/extract/title.png" width="auto" height="100px" />

___

**extract** is a tool to extract a raw data file from a Plink- or Eigenstrat-style set.

### Dependencies

- [Plink 1.90](https://www.cog-genomics.org/plink2/)
- Python 3.10 (if running on Linux or MacOS)

### Usage

- Download this repo and add the root directory to PATH.

- Get the ID of the sample you want to extract. This is the first column value in an .ind file, and the second column in a .fam file.

- Let's assume your set is the [`v54`](https://reichdata.hms.harvard.edu/pub/datasets/amh_repo/curated_releases/V54/V54.1.p1/SHARE/public.dir/) set, and is also called that locally (i.e. its files are named v54.ind, v54.bim etc)

- You might, for example, try to extract the sample `I6186` (labeled "Romania_MLBA"), like this:
```
mgen extract -s v54 -p plink -c convertf -id I6186 -n Romania_MLBA_I6186 --path [path to the folder containing the local v54 set]
```

- You'll get a raw data txt file called `Romania_MLBA_I6186.txt`.

### Options

```
$ mgen extract -h
usage: extract [-h] -s SET -p PLINK -c CONVERTF [--convert-to-plink] -id ID
               [-n NAME] --path PATH

Extract a raw data file from a Plink or Eigenstrat set

optional arguments:
  -h, --help            show this help message and exit
  -s SET, --set SET     Name of your set
  -p PLINK, --plink PLINK
                        Command used to invoke plink on your machine (e.g.
                        "plink")
  -c CONVERTF, --convertf CONVERTF
                        Command used to invoke convertf on your machine (e.g.
                        "convertf")
  --convert-to-plink    Is the set in Eigenstrat format (.ind, .snp, .geno)?
                        If yes, use this option
  -id ID, --id ID       Name of your sample id (second column of the row in
                        the .fam file)
  -n NAME, --name NAME  Name of your extracted raw data file (defaults to the
                        name of the smaple id)
  --path PATH           Path to the folder in which your set lives (e.g. './',
                        '/usr/bin/' etc)

Copyright (c) 2023 Tushar Rakheja (The MIT License)
```

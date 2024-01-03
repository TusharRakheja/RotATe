import subprocess
import os
import argparse
import sys

CT_TO_PLINK = './ct_to_plink'

N_FILE = 'N.txt'

args = None


def gen_ct_to_plink():
    global CT_TO_PLINK

    with open(CT_TO_PLINK, 'w') as outfile:
        outfile.write("genotypename: {}.geno\n".format(args.set))
        outfile.write("snpname: {}.snp\n".format(args.set))
        outfile.write("indivname: {}.ind\n".format(args.set))
        outfile.write("outputformat: PACKEDPED\n")
        outfile.write("genotypeoutname: {}.bed\n".format(args.set))
        outfile.write("snpoutname: {}.bim\n".format(args.set))
        outfile.write("indivoutname: {}.fam\n".format(args.set))


def convert_to_plink():
    global CT_TO_PLINK

    subprocess.call(['wsl', args.convertf, '-p', CT_TO_PLINK])


def make_nfile():
    global N_FILE

    with open('./{}.fam'.format(args.set), 'r') as infile:
        l = infile.readlines()
    
    found = False

    for line in l:
        line = line.strip()
        if not line:
            continue
    
        if line.split()[1] == args.id:
            found = True
            with open('./{}'.format(N_FILE), 'w') as outfile:
                outfile.write(line)
    
    if not found:
        print("Sample id {} not found in {}.fam, please check and retry with the correct sample id.".format(args.id, args.set))
        sys.exit(1)


def make_custom_set():
    global N_FILE

    subprocess.call([args.plink, '--bfile', args.set, '--keep', N_FILE, '--make-bed', '--out', 'A'])
    os.remove(N_FILE)


def get_raw_data():
    subprocess.call([args.plink, '--bfile', 'A', '--recode', '23', '--out', args.name])


def cleanup():
    global N_FILE
    prob = False
    try:
        os.remove('./A.bed')
    except:
        prob = True
    
    try:
        os.remove('./A.bim')
    except:
        prob = True
    
    try:
        os.remove('./A.fam')
    except:
        prob = True
    
    try:
        os.remove('./A.hh')
    except:
        prob = True
    
    try:
        os.remove('./A.log')
    except:
        prob = True
    
    try:
        os.remove('./A.nosex')
    except:
        prob = True
    
    try:
        os.remove('./{}.hh'.format(args.name))
    except:
        prob = True
    
    try:
        os.remove('./{}.log'.format(args.name))
    except:
        prob = True
    
    if prob:
        print("Some problem when cleaning up files that are no longer needed. But your sample should be extracted by now.")


def parse_args():
    global args    

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--set', dest='set', type=str, help='Name of your set', required=True)
    parser.add_argument('-p', '--plink', dest='plink', type=str, help='Command used to invoke plink on your machine (e.g. "plink")', required=True)
    parser.add_argument('-c', '--convertf', dest='convertf', type=str, help='Command used to invoke convertf on your machine (e.g. "convertf")', required=True)
    parser.add_argument('-ctp', '--convert-to-plink', dest='convert_to_plink', type=str, default='no', help='Is the set in Eigenstrat format (.ind, .snp, .geno)? (yes or no, default: no)', required=False)
    parser.add_argument('-id', '--id', dest='id', type=str, help='Name of your sample id (second column of the row in the .fam file)', required=True)
    parser.add_argument('-n', '--name', dest='name', type=str, default=None, help='Name of your extracted raw data file (defaults to the name of the smaple id)', required=False)

    args, _ = parser.parse_known_args()

    if args.name is None:
        args.name = args.id


def main():
    global CT_TO_PLINK

    parse_args()
    
    if args.convert_to_plink == 'yes':
        gen_ct_to_plink()
        convert_to_plink()
        os.remove(CT_TO_PLINK)
    
    make_nfile()
    make_custom_set()
    get_raw_data()
    cleanup()


if __name__ == '__main__':
    main()
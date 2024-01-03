import subprocess
import argparse
import errno
import shutil
import time
import sys
import os

from functools import cmp_to_key
from queue import Queue

WORKING = './working'
CT_TO_PLINK = './ct_to_plink'
CT_TO_EIGENSTRAT = './ct_to_eigenstrat'

IND_CACHE = {}

RESULTS_QUEUE = Queue()

TYPE = None

parser = argparse.ArgumentParser(
    prog='merge',
    description='Merge a raw data file into a Plink or Eigenstrat set',
    epilog='Copyright (c) 2023 Tushar Rakheja (The MIT License)'
)

args = None
PREFIX = None
DATAFILE = None

PLINK_MISS = './plink.imiss'

d3 = {}
d4 = {}
d5 = {}


def sort_genos(a, b):
    ch_a = a[1]
    ch_b = b[1]

    if ch_a == 'X':
        ch_a = 23
    elif ch_a == 'Y':
        ch_a = 24
    elif ch_a == 'XY':
        ch_a = 25
    elif ch_a == 'MT':
        ch_a = 26
    
    if ch_b == 'X':
        ch_b = 23
    elif ch_b == 'Y':
        ch_b = 24
    elif ch_b == 'XY':
        ch_b = 25
    elif ch_b == 'MT':
        ch_b = 26

    ch_a = int(ch_a)
    ch_b = int(ch_b)

    if ch_a < ch_b:
        return -1
    elif ch_a > ch_b:
        return 1

    loc_a = int(a[2])
    loc_b = int(b[2])

    if loc_a < loc_b:
        return -1
    elif loc_a > loc_b:
        return 1
    else:
        return 0


def clean_and_convert_ancestry(datalist):
    global DATAFILE

    with open(DATAFILE, 'w') as outfile:
        for line in datalist:
            parts = line.split()
            if parts[-1] == '0' and parts[-2] == '0':
                pass
            else:
                outfile.write("\t".join(parts[:-1]) + parts[-1] + "\n")


def clean_and_convert_mapmygenome(datalist):
    global DATAFILE

    genos = []

    for line in datalist:
        if '--' in line:
            continue

        genos.append(line.split())

    genos.sort(key=cmp_to_key(sort_genos))

    with open(DATAFILE, 'w') as outfile:
        for geno in genos:
            outfile.write('\t'.join([geno[0], geno[1], geno[2], geno[3]]) + '\n')


def clean_23_and_me(datalist):
    global DATAFILE

    with open(DATAFILE, 'w') as outfile:
        for line in datalist:
            if '--' not in line:
                outfile.write(line + '\n')


def clean_and_convert_file():
    global DATAFILE

    print("[merge] Cleaning and converting file...")

    format = args.file_type if args.file_type is not None else '23andMe'

    with open(DATAFILE, 'r') as infile:
        l = infile.readlines()

    l2 = []

    for line in l:

        linestrp = line.strip()

        if not linestrp:
            continue

        if linestrp.startswith('#'):
            continue

        if linestrp == 'rsid	chromosome	position	allele1	allele2':
            if args.file_type is None:
                format = 'Ancestry'
            continue
    
        if linestrp == 'rsid	chromosome	position	genotype' or linestrp == 'Rsid	Chromosome	Position	Genotype':
            if args.file_type is None:
                format = 'Mapmygenome'
            continue
    
        if 'hromosome' in linestrp or 'osition' in linestrp or 'llele' in linestrp or 'enotype' in linestrp:
            continue

        l2.append(linestrp)
    
    l = l2

    if format == 'Ancestry':
        print("[merge] Format of raw file discovered to be AncestryDNA")
        clean_and_convert_ancestry(l)
    elif format == 'Mapmygenome':
        print("[merge] Format of raw file discovered to be Mapmygenome")
        clean_and_convert_mapmygenome(l)
    else:
        print("[merge] Format of raw file defaulting to 23andMe")
        assert format == '23andMe'
        clean_23_and_me(l)


def create_working_directory():
    global WORKING

    print("[merge] Creating working directory...")
    try:
        os.mkdir(WORKING)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            print("\t[merge] ERROR! The working directory already exists, please delete it before starting a new merge.")
        sys.exit(1)


def copy_eigenstrat_or_plink_files():
    global WORKING, TYPE

    print("[merge] Copying over Eigenstrat or Plink files...")
    
    if args.convert_to_eigenstrat == 'yes' or TYPE == 'eigenstrat':
        shutil.copy(args.ind, WORKING)

    if TYPE == 'eigenstrat':
        shutil.copy(args.snp, WORKING)
        shutil.copy(args.geno, WORKING)
    else:
        shutil.copy(args.bim, WORKING)
        shutil.copy(args.bed, WORKING)
        shutil.copy(args.fam, WORKING)

    shutil.copy(args.data, WORKING)


def gen_ct_to_plink():
    global CT_TO_PLINK, PREFIX

    with open(CT_TO_PLINK, 'w') as outfile:
        outfile.write("genotypename: {}\n".format(args.geno.split('/')[-1]))
        outfile.write("snpname: {}\n".format(args.snp.split('/')[-1]))
        outfile.write("indivname: {}\n".format(args.ind.split('/')[-1]))
        outfile.write("outputformat: PACKEDPED\n")
        outfile.write("genotypeoutname: {}.bed\n".format(PREFIX))
        outfile.write("snpoutname: {}.bim\n".format(PREFIX))
        outfile.write("indivoutname: {}.fam\n".format(PREFIX))


def convert_to_plink():
    global CT_TO_PLINK

    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_admix_tools else []), args.convertf, '-p', CT_TO_PLINK])


def call_plink_on_file():
    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--23file', args.data.split('/')[-1], '--out', args.name])


def prune_dataset():
    global PREFIX
    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', PREFIX, '--write-snplist'])


def extract_snp_list():
    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', args.name, '--extract', 'plink.snplist', '--make-bed', '--out', 'B1'])


def replace_content_of_fam():
    fam = './B1.fam'
    with open(fam, 'r') as infile:
        l = infile.readlines()
    
    lines = []
    for line in l:
        line = line.strip()
        if not line:
            continue

        lines.append(line)
    
    assert len(lines) == 1

    target_line = lines[0]
    target_line = target_line.replace('-9', '1')

    target_line_parts = target_line.strip().split()

    if args.sex == 'M':
        target_line_parts[4] = '1'
    elif args.sex == 'F':
        target_line_parts[4] = '2'
    elif args.sex == 'U':
        target_line_parts[4] = '0'

    target_line = ' '.join(target_line_parts) + '\n'
    target_line = target_line.replace('ID001', args.name)

    with open(fam, 'w') as outfile:
        outfile.write(target_line)


def attempt_merge():
    global PREFIX
    call = None
    try:
        call = subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', PREFIX, '--bmerge', 'B1.bed', 'B1.bim', 'B1.fam', '--indiv-sort', '0', '--allow-no-sex', '--make-bed', '--out', args.name])
    except:
        call = 1

    return call


def flip_snps():
    global PREFIX
    print("[merge] Flipping SNPs...")
    call = None

    try:
        call = subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', 'B1', '--flip', '{}-merge.missnp'.format(args.name), '--make-bed', '--out', 'B1_flip'])
        if call == 0:
            call = subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', PREFIX, '--bmerge', 'B1_flip.bed', 'B1_flip.bim', 'B1_flip.fam', '--indiv-sort', '0', '--allow-no-sex', '--make-bed', '--out', args.name])
        else:
            print("[merge] Flip res = " + str(call))
    except:
        call = 1
    
    return call


def skip_snps():
    global PREFIX
    print("[merge] Skipping SNPs...")
    call = None

    try:
        call = subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', 'B1_flip', '--exclude', '{}-merge.missnp'.format(args.name), '--make-bed', '--allow-no-sex', '--out', 'B1_tmp'])
        if call == 0:
            call = subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', PREFIX, '--bmerge', 'B1_tmp.bed', 'B1_tmp.bim', 'B1_tmp.fam', '--indiv-sort', '0', '--allow-no-sex', '--make-bed', '--out', args.name])
        else:
            print("[merge] Skip res = " + str(call))
    except:
        call = 1
    
    return call


def gen_ct_to_eigenstrat():
    global CT_TO_EIGENSTRAT, PREFIX

    with open(CT_TO_EIGENSTRAT, 'w') as outfile:
        outfile.write("genotypename: {}.bed\n".format(args.name))
        outfile.write("snpname: {}.bim\n".format(args.name))
        outfile.write("indivname: {}.fam\n".format(args.name))
        outfile.write("outputformat: PACKEDANCESTRYMAP\n")
        outfile.write("familynames: NO\n")
        outfile.write("genotypeoutname: {}.geno\n".format(PREFIX))
        outfile.write("snpoutname: {}.snp\n".format(PREFIX))
        outfile.write("indivoutname: {}.ind\n".format(PREFIX))


def convert_to_eigenstrat():
    global CT_TO_EIGENSTRAT

    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_admix_tools else []), args.convertf, '-p', CT_TO_EIGENSTRAT])


def remove_original_dataset():
    global WORKING, IND_CACHE, PREFIX, TYPE

    with open('./{}.ind'.format(PREFIX), 'r') as infile:
        l = infile.readlines()
    
    for line in l:
        if not line.strip():
            continue

        parts = line.strip().split()

        IND_CACHE[parts[0].strip()] = parts[2].strip()
    
    os.remove('./{}.ind'.format(PREFIX))

    if TYPE == 'eigenstrat':
        os.remove('./{}.snp'.format(PREFIX))
        os.remove('./{}.geno'.format(PREFIX))


def prepare_final_ind():
    global IND_CACHE, PREFIX

    with open('./{}.ind'.format(PREFIX), 'r') as infile:
        l = infile.readlines()

    l2 = []
    for line in l:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        l2.append(line)
    
    l = l2

    with open('./{}.ind'.format(PREFIX), 'w') as outfile:
        for i in range(len(l)):
            line = l[i]
            parts = line.strip().split()
            
            if parts[0] in IND_CACHE.keys():
                line = line.replace('Control', IND_CACHE[parts[0]])
            
            elif i == len(l) - 1:
                line = line.replace('Control', args.name)

            outfile.write(line)
            if line[-1] != '\n':
                outfile.write('\n')


def gen_plink_imiss_on_og_set():
    global PREFIX, d3, d4, d5, PLINK_MISS

    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', PREFIX, '--missing'])

    time.sleep(1)

    with open(PLINK_MISS, 'r') as infile:
        l = infile.readlines()

    for line in l:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        d3[parts[1]] = parts[3]
        d4[parts[1]] = parts[4]
        d5[parts[1]] = parts[5]
    
    os.remove(PLINK_MISS)


def check_plink_imiss_on_merged_set():
    global PLINK_MISS, d3, d4, d5

    subprocess.call([*(['wsl'] if args.turn_on_wsl_for_plink else []), args.plink, '--bfile', args.name, '--missing'])

    time.sleep(1)

    with open(PLINK_MISS, 'r') as infile:
        l = infile.readlines()
    
    i = 0
    for line in l:
        line = line.strip()
        if not line:
            continue

        parts = line.split()

        if parts[1] not in d3.keys():
            assert parts[1] not in d4.keys()
            assert parts[1] not in d5.keys()
            continue

        if parts[3] != d3[parts[1]] or parts[4] != d4[parts[1]] or parts[5] != d5[parts[1]]:
            i += 1

    os.remove(PLINK_MISS)
    return i


def rename_plink_files():
    global PREFIX

    try:
        os.remove('./{}.bim'.format(PREFIX))
    except:
        pass

    try:
        os.remove('./{}.bed'.format(PREFIX))
    except:
        pass

    try:
        os.remove('./{}.fam'.format(PREFIX))
    except:
        pass
    
    os.rename('./{}.bim'.format(args.name), './{}.bim'.format(PREFIX))
    os.rename('./{}.bed'.format(args.name), './{}.bed'.format(PREFIX))
    os.rename('./{}.fam'.format(args.name), './{}.fam'.format(PREFIX))


def parse_args():
    global parser, args, PREFIX, DATAFILE, TYPE

    parser.add_argument('-i', '--ind', dest='ind', type=str, default=None, help='Path of the .ind file (e.g "./set.ind")')
    parser.add_argument('-s', '--snp', dest='snp', type=str, default=None, help='Path of the .snp file (e.g "./set.snp")')
    parser.add_argument('-g', '--geno', dest='geno', type=str, default=None, help='Path of the .geno file (e.g "./set.geno")')
    parser.add_argument('-f', '--fam', dest='fam', type=str, default=None, help='Path of the .fam file (e.g "./set.fam")')
    parser.add_argument('-bi', '--bim', dest='bim', type=str, default=None, help='Path of the .bim file (e.g "./set.bim")')
    parser.add_argument('-be', '--bed', dest='bed', type=str, default=None, help='Path of the .bed file (e.g "./set.bed")')
    parser.add_argument('-d', '--data', dest='data', type=str, help='Path of the raw data file (e.g "./23andMe.txt")', required=True)
    parser.add_argument('-p', '--plink', dest='plink', type=str, help='Command used to invoke plink on your machine (e.g. "plink")', required=True)
    parser.add_argument('-n', '--name', dest='name', type=str, help='A name for your sample to be used in the merged dataset (e.g. "tony23andMe")', required=True)
    parser.add_argument('-c', '--convertf', dest='convertf', type=str, help='Command used to invoke convertf on your machine (e.g. "convertf")', required=True)
    parser.add_argument('-cte', '--convert-to-eigenstrat', dest='convert_to_eigenstrat', type=str, default='yes', help='Convert the files to eigenstrat format after merging? (default: yes)')
    parser.add_argument('-se', '--sex', dest='sex', type=str, default=None, help="Sex of the sample ('M', 'F' or 'U')", required=True)
    parser.add_argument('-ft', '--file-type', dest='file_type', type=str, default=None, help="Type of the raw data file ('Ancestry', '23andMe', or 'Mapmygenome')")
    parser.add_argument('--turn-on-wsl-for-plink', default=False, action='store_true')
    parser.add_argument('--turn-on-wsl-for-admix-tools', default=False, action='store_true')

    args, _ = parser.parse_known_args()

    args.sex = args.sex.upper()

    if args.fam is not None and args.bim is not None and args.bed is not None:
        TYPE = 'plink'
    elif args.ind is not None and args.snp is not None and args.geno is not None:
        TYPE = 'eigenstrat'
    else:
        print("[merge] You need to provide either plink style .fam, .bim and .bed files, or eigenstrat style .ind, .snp and .geno files.")
        sys.exit(1)

    if TYPE == 'plink' and args.convert_to_eigenstrat == 'yes' and args.ind is None:
        print("[merge] If you want to convert the merged set to eigenstrat, you need to provide an .ind file in addition to the plink set.")
        

    PREFIX = (args.ind if TYPE == 'eigenstrat' else args.fam).split('/')[-1]
    PREFIX = PREFIX[:PREFIX.index('.')]

    DATAFILE = './' + args.data.split('/')[-1]


def main():
    parse_args()

    global WORKING, TYPE

    create_working_directory()

    copy_eigenstrat_or_plink_files()

    os.chdir(WORKING)

    clean_and_convert_file()

    if TYPE == 'eigenstrat':

        gen_ct_to_plink()

        convert_to_plink()

    gen_plink_imiss_on_og_set()

    call_plink_on_file()

    prune_dataset()

    extract_snp_list()

    replace_content_of_fam()

    res = attempt_merge()

    if res != 0:
        res = flip_snps()
        if res != 0:
            res = skip_snps()
            if res != 0:
                print("[merge] Tried merging, flip-merging, and skip-mering, but it didn't work. Exiting.")
                sys.exit(1)
    
    status = check_plink_imiss_on_merged_set()


    if status != 0:
        print("[merge] The coverage is different in the merged set and the og set. Please check manually. Exiting.")
        sys.exit(1)


    if args.convert_to_eigenstrat == 'yes':

        gen_ct_to_eigenstrat()

        remove_original_dataset()

        convert_to_eigenstrat()

        prepare_final_ind()

    rename_plink_files()


if __name__ == '__main__':
    main()
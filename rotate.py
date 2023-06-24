import subprocess
import itertools
import argparse
import hashlib
import yaml
import os

from concurrent.futures import ThreadPoolExecutor
from queue import Queue

CORE_RIGHT = 'core_right'
TARGET = 'target'
SOURCES = 'sources'

RESULTS_QUEUE = Queue()

parser = argparse.ArgumentParser(
    prog='rotATe',
    description='Run rotating qpAdm models',
    epilog='Copyright (c) 2023 Tushar Rakheja (The MIT License)'
)

parser.add_argument('-i', '--ind', dest='ind', type=str, help='Name of the .ind file', required=True)
parser.add_argument('-s', '--snp', dest='snp', type=str, help='Name of the .snp file', required=True)
parser.add_argument('-g', '--geno', dest='geno', type=str, help='Name of the .geno file', required=True)
parser.add_argument(
    '-c', '--config', dest='config', type=str, default='./config.yml', help='Path to the YAML config file (default: "./config.yml")'
)
parser.add_argument(
    '-n', '--nthreads', dest='nthreads', type=int, default=1, help='The number of models to run in parallel (default: 1)'
)
parser.add_argument('-e', '--error-coefficient', dest='error_coefficient', type=float, default=2.0, help='Error coefficient')
parser.add_argument('-p', '--pmin', dest='pmin', type=float, default=0.01, help='Minimum viable p-value')

args = parser.parse_args()

IND = args.ind
SNP = args.snp
GENO = args.geno

CONFIG_FILE = args.config
MODELS_POOL = ThreadPoolExecutor(args.nthreads)

PID = os.getpid()

tempconfig = open(CONFIG_FILE, 'rb')
SUFFIX = hashlib.md5(tempconfig.read()).hexdigest()
tempconfig.close()

RESULTS = './results_{}.csv'.format(SUFFIX)
CACHE = './cache_{}.txt'.format(SUFFIX)

def is_valid(conf):
    global CORE_RIGHT, TARGET, SOURCES, IND

    if CORE_RIGHT not in conf.keys():
        return False
    if not isinstance(conf[CORE_RIGHT], list):
        return False
    for source in conf[CORE_RIGHT]:
        if not isinstance(source, str):
            return False
    
    if not isinstance(conf[TARGET], str):
        return False
    
    if not isinstance(conf[SOURCES], list):
        return False
    for sources in conf[SOURCES]:
        if not isinstance(sources, list):
            return False
        for source in sources:
            if not isinstance(source, str):
                return False

    with open('./{}'.format(IND), 'r') as infile:
        l = infile.readlines()
    
    samples = set()
    for line in l:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        samples.add(parts[-1])
    
    for source in conf[CORE_RIGHT]:
        if source not in samples:
            print("Source {} not found in the {} file".format(source, IND))
            return False
    
    if conf[TARGET] not in samples:
        print("Source {} not found in the {} file".format(conf[TARGET], IND))
        return False

    for sources in conf[SOURCES]:
        for source in sources:
            if source != "" and source not in samples:
                print("Source {} not found in the {} file".format(source, IND))
                return False

    return True


def run(model_number, target, model, source_sets, core_sources):
    global PID

    try:
        LEFT = './left_{}_{}'.format(PID, model_number)
        RIGHT = './right_{}_{}'.format(PID, model_number)
        OUTPUT = './output_{}_{}'.format(PID, model_number)
        PARQPADM = './parqpadm_{}_{}'.format(PID, model_number)

        generate_parqpadm(PARQPADM, LEFT[2:], RIGHT[2:])

        with open(LEFT, 'w') as outfile:
            outfile.write("{}\n".format(target))
            for source in model:
                source = source.strip()
                if not source:
                    continue

                outfile.write("{}\n".format(source))

        with open(RIGHT, 'w') as outfile:
            for source in core_sources:
                outfile.write("{}\n".format(source))
            for sources in source_sets:
                for source in sources:
                    source = source.strip()
                    if not source:
                        continue

                    if source not in model:
                        outfile.write("{}\n".format(source))


        with open(OUTPUT, 'w') as outfile:
            print("{} - Running model {}".format(model_number, model))
            subprocess.call(['qpAdm', '-p', PARQPADM[2:]], stdout=outfile)

        weights, errors, pvalue = weights_errors_pvalue(OUTPUT)
        return [target, model, weights, errors, pvalue]
    
    except:
        return [target, model, None, None, None]

    finally:
        clean_up_model_files(LEFT, RIGHT, OUTPUT, PARQPADM, model)


def write_results():
    global RESULTS_QUEUE, RESULTS

    while not RESULTS_QUEUE.empty():
        with open(RESULTS, 'a') as outfile:
            target, model, weights, errors, pvalue = RESULTS_QUEUE.get().result()
            if weights is None:
                print("\tFailed model {}. Will be attempted again if you re-run the script".format(model))
                continue

            outfile.write(result_row(target, model, weights, errors, pvalue))
            add_model_to_cache(model)


def generate_parqpadm(parqpadm, left, right):
    global IND, SNP, GENO
    with open(parqpadm, 'w') as outfile:
        outfile.write('indivname:       {}\n'.format(IND))
        outfile.write('snpname:         {}\n'.format(SNP))
        outfile.write('genotypename:    {}\n'.format(GENO))
        outfile.write('popleft:         {}\n'.format(left))
        outfile.write('popright:        {}\n'.format(right))
        outfile.write('details:         YES\n')
        outfile.write('allsnps:         YES\n')
        outfile.write('inbreed:         NO\n')


def clean_up_model_files(left, right, output, parqpadm, model):
    try:
        os.remove(left)
        os.remove(right)
        os.remove(output)
        os.remove(parqpadm)
    except OSError:
        print("Error removing files for model {}. Runs are unaffected though.".format(model))


def weights_errors_pvalue(output):
    with open(output, 'r') as infile:
        l = infile.readlines()
    
    weights = None
    errors = None
    pvalue = None

    read_pvalue = False

    for line in l:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('best coefficients:'):
            weights = []
            for weight in line.split()[2:]:
                weights.append(weight)
            continue

        if line.startswith('std. errors:'):
            errors = []
            for error in line.split()[2:]:
                errors.append(error)
            continue

        if 'tail prob' in line:
            read_pvalue = True
            continue

        if read_pvalue:
            pvalue = line.split()[4]
            break

    assert weights is not None
    assert errors is not None
    assert pvalue is not None
    assert read_pvalue is True

    return [weights, errors, pvalue]


def result_row(target, model, weights, errors, pvalue):
    res = ""
    res += "{},".format(target)
    for source in model:
        res += "{},".format(source if source.strip() != "" else "-")

    j = 0
    for i in range(len(model)):
        if model[i].strip() == "":
            res += "0%,"
        else:
            res += "{},".format(str("%.1f" % (float(weights[j])*100)) + '%')
            j += 1

    j = 0
    for i in range(len(model)):
        if model[i].strip() == "":
            res += "0%,"
        else:
            res += "{},".format(str("%.1f" % (float(errors[j])*100)) + '%')
            j += 1

    res += "{},{},".format(pvalue, len(list(filter(lambda source: source.strip() != "", model))))

    ispass = float(pvalue) >= args.pmin

    for i in range(len(weights)):
        ispass = ispass and ((
            float(weights[i]) - args.error_coefficient * float(errors[i])
        ) >= 0)
        ispass = ispass and ((
            float(weights[i]) + args.error_coefficient * float(errors[i])
        ) <= 1)

    res += "{}\n".format(1 if ispass else 0)

    return res


def write_headers(num_sources):
    global RESULTS

    if os.path.isfile(RESULTS):
        return

    outfile = open(RESULTS, 'w')

    outfile.write('Target,')
    for i in range(num_sources):
        outfile.write('Source {},'.format(i + 1))
    for i in range(num_sources):
        outfile.write('Weight {},'.format(i + 1))
    for i in range(num_sources):
        outfile.write('Error {},'.format(i + 1))
    outfile.write('p-value,Complexity,Pass?\n')

    outfile.close()


def add_model_to_cache(model):
    with open(CACHE, 'a') as outfile:
        outfile.write(','.join(model) + '\n')


def is_model_in_cache(model):
    key = ','.join(model)

    try:
        infile = open(CACHE, 'r')
    except OSError:
        return False

    l = infile.readlines()

    infile.close()
    
    for line in l:
        if line.strip() == key:
            return True
    
    return False


def main():
    global CORE_RIGHT, TARGET, SOURCES, CONFIG_FILE, MODELS_POOL

    with open(CONFIG_FILE, 'r') as infile:
        config = None
        try:
            config = yaml.safe_load(infile)
        except yaml.YAMLError as exc:
            print(exc)

    assert config is not None
    assert is_valid(config)

    source_sets = config[SOURCES]

    models = list(itertools.product(*source_sets))

    write_headers(len(source_sets))
    
    print("Will try {} models".format(len(models)))

    model_number = 1
    for model in models:
        if is_model_in_cache(model):
            print("{} - Skipping model {} because already in cache.".format(model_number, model))
            model_number += 1
            continue

        if len(list(filter(lambda source: source.strip() != "", model))) < 2:
            print("{} - Skipping model {} because we need at least two sources.".format(model_number, model))
            model_number += 1

        task = MODELS_POOL.submit(run, model_number, config[TARGET], model, source_sets, config[CORE_RIGHT])
        RESULTS_QUEUE.put(task)
        model_number += 1

    write_results()


if __name__ == '__main__':
    main()

import subprocess
import itertools
import yaml

CORE_RIGHT = 'core_right'
TARGET = 'target'
SOURCES = 'sources'

def is_valid(conf):
    global CORE_RIGHT, TARGET, SOURCES

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

    return True


def run(target, model, source_sets, core_sources):
    with open('./left', 'w') as outfile:
        outfile.write("{}\n".format(target))
        for source in model:
            outfile.write("{}\n".format(source))

    with open('./right', 'w') as outfile:
        for source in core_sources:
            outfile.write("{}\n".format(source))
        for sources in source_sets:
            for source in sources:
                if source not in model:
                    outfile.write("{}\n".format(source))

    with open('./output', 'w') as outfile:
        subprocess.call(['qpAdm', '-p', 'parqpadm'], stdout=outfile)
    
    with open('./output', 'r') as infile:
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
                weights.append(str("%.2f" % (float(weight)*100)) + '%')
            continue

        if line.startswith('std. errors:'):
            errors = []
            for error in line.split()[2:]:
                errors.append(str("%.2f" % (float(error)*100)) + '%')
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

    write_result_row(target, model, weights, errors, pvalue)


def write_result_row(target, model, weights, errors, pvalue):
    with open('./results.csv', 'a') as outfile:
        outfile.write("{},".format(target))
        for source in model:
            outfile.write("{},".format(source))
        for weight in weights:
            outfile.write("{},".format(weight))
        for error in errors:
            outfile.write("{},".format(error))
        outfile.write("{}\n".format(pvalue))


def write_headers(num_sources):
    try:
        outfile = open('./results.csv', 'a')
    except OSError:
        outfile = open('./results.csv', 'w')

    outfile.write('Target,')
    for i in range(num_sources):
        outfile.write('Source {},'.format(i + 1))
    for i in range(num_sources):
        outfile.write('Weight {},'.format(i + 1))
    for i in range(num_sources):
        outfile.write('Error {},'.format(i + 1))
    outfile.write('p-value\n')

    outfile.close()


def add_model_to_cache(model):
    with open('./cache.txt', 'a') as outfile:
        outfile.write(','.join(model) + '\n')



def is_model_in_cache(model):
    key = ','.join(model)

    try:
        infile = open('./cache.txt', 'r')
    except OSError:
        return False

    l = infile.readlines()

    infile.close()
    
    for line in l:
        if line.strip() == key:
            return True
    
    return False


def main():
    global CORE_RIGHT, TARGET, SOURCES

    with open('./config.yml', 'r') as infile:
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

    i = 1
    for model in models:
        if is_model_in_cache(model):
            print("{} - Skipping model {} because already in cache.".format(i, model))
            i += 1
            continue

        print("{} - Running model {}".format(i, model))
        run(config[TARGET], model, source_sets, config[CORE_RIGHT])
        add_model_to_cache(model)

        i += 1


if __name__ == '__main__':
    main()
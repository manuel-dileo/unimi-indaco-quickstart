#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import os
import os.path

import sys
import logging


def cartesian_product(dicts):
    return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))


def summary(configuration):
    kvs = sorted([(k, v) for k, v in configuration.items()], key=lambda e: e[0])
    return '_'.join([('%s=%s' % (k, v)) for (k, v) in kvs if k not in {'d'}])


def to_cmd(c, _path=None):
    command = f'PYTHONPATH=. python3 main.py ' \
              f'--lr {c["lr"]} --batch_size {c["batch_size"]}'
    return command

def main(argv):
    project_name = "GNN4BioKG" #change with your project name
    hyp_space = dict(
        lr = [1, 1e-1, 1e-2, 1e-3, 1e-4],
        batch_size = [64, 128, 256, 512]
    )

    configurations = list(cartesian_product(hyp_space))

    # If the folder that will contain logs does not exist, create it
    #if not os.path.exists(path):
        #os.makedirs(path)

    command_lines = set()
    for i in range(10): #10 is the number of runs
        for cfg in configurations:
            cmd = to_cmd(cfg)
            if cmd is not None:
                command_line = f'{cmd} > output.txt 2>&1'
                command_lines |= {command_line}

    # Sort command lines and remove duplicates
    sorted_command_lines = sorted(command_lines)

    import random
    rng = random.Random(0)
    rng.shuffle(sorted_command_lines)

    nb_jobs = len(sorted_command_lines)

    header = f"""#!/usr/bin/env bash

#SBATCH --output=/home/users/%u/{project_name}/slogs/example-%A_%a.out
#SBATCH --error=/home/users/%u/{project_name}/slogs/example-%A_%a.err
#SBATCH --partition=light
#SBATCH --mem=8GB # memory
#SBATCH --cpus-per-task=4 # number of cpus to use - there are 32 on each node.
#SBATCH -t 8:00:00 # time requested in hours:minutes:seconds
#SBATCH --array 1-{nb_jobs}

module load intel/parallel_2020

echo "Setting up bash environment"
source ~/.bashrc
set -e # fail fast

conda activate $HOME/{project_name}/folder/pkg/mypt

export LANG="en_US.utf8"
export LANGUAGE="en_US:en"

cd $HOME/{project_name}/scratch/projects/pytorch-examples/mnist

"""

    if header is not None:
        print(header)

    is_slurm = True
    for job_id, command_line in enumerate(sorted_command_lines, 1):
        if is_slurm:
            print(f'test $SLURM_ARRAY_TASK_ID -eq {job_id} && sleep 10 && {command_line}')
        else:
            print(f'{command_line}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
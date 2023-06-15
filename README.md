# Using UNIMI INDACO for Machine Learning: Quick Start
## 15 June 2023
### Manuel Dileo (adapted from Tom Sherborn, University of Edinburgh)

This guide explains how to:
 - Log on to the cluster
 - Set up a conda environment manager
 - Provides examples of
	 - Interactive sessions with and without a GPU (srun)
	 - Running scripts on the cluster non-interactively (batch)
 
 ## Disclaimer
 This quick start is strongly related to running machine learning experiments and it is not official. For official user guides, you can refer to the [INDACO website](https://www.indaco.unimi.it/index.php/documentazione/).

 ## Log on to INDACO
You can SSH into INDACO without using a VPN. To do so, you can use the command
```
ssh -L 5000:127.0.0.1:3389 name.surname@login.indaco.unimi.it
```
For the rest of the guide, we will just use shell commands. If you are not comfortable with shells you can read this [MIT guide](https://missing.csail.mit.edu/).

## Important things to note first

![Cluster Diagram](cdt_cluster_diag.png)
This is an approximate setup of how INDACO is arranged.

- The initial node you log into is called the __head node__ - __do not__ run heavy processes on here. This node is only used for sending jobs to other nodes in the cluster
- The filesystem you have access to when you log in is identical on all the nodes you can access - it is a __distributed__ filesystem. As such, it is very slow (because it must appear the same everywhere)!
    - Avoid reading and writing files frequently on this filesystem
    - Instead, when running a job on a node, use its scratch disk and only move files to the shared filesystem infrequently. The scratch disk is located at `/disk/scratch` normally.
- Please skim-read this for best practice: http://computing.help.inf.ed.ac.uk/cluster-tips

## Project directory organization
The home directory provides a limited space of 10GB. In the home directory, you can not install any new software. To be able to setup a conda environment and install new software, move to the directory of your project with
```
cd projectname
```
On the project directory user have access to three different storage area:
- A scratch area that can be used as a temporary area. Upon request, INDACO staff can delete its content periodically.
- A backup area that holds a replica of the data already present in other systems external to Indaco. Please take a look at the README available in the related folder.
- A project area

## Environment modules
Indaco provides several modules to allow the user to prepare the calculation environment according to the application, library, or development tool s/he intends to use. 

The ```module avail``` command provides the list of all the available modules. The ```module load name``` command allows you to load the specified module. 

To run ML experiments with PyTorch we need to load at least the following modules:
```
module load python3/anaconda/3-2022
module load CUDA/11.7
module load intel/parallel_2020
```

## Setup conda environment
## What's Next? Practical examples!

You can head straight to the cluster-scripts experiments repository here: 
https://github.com/cdt-data-science/cluster-scripts/tree/master/experiments
where you will find templates and practical examples to get you going. 

There are further examples below to try afterwards.


## Further examples

All the examples below expect you have performed the prior setup.

### Setup 
#### Create a conda environment with PyTorch

Make the conda environment. This can take a bit of time (it’s harder for the distributed filesystem to deal with lots of small files than for your local machine’s hard drive) - go get a cup of tea.

1. Check local versions of cuda available - at time of writing cuda 10.1 is available: `ls -d /opt/cu*`. You should use this version for the `cudatoolkit=??.?` argument below.
2. Run the command to create a conda environment called `pt`:
    `conda create -y -n pt python=3 pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch`  (more info about PyTorch installation here if this goes wrong: https://pytorch.org/get-started/locally/)
3. Activate the environment `conda activate pt`

#### Get some code to run mnist experiments.
Get some code to run mnist in pytorch and run it:
 - `mkdir ~/projects`
 - `cd ~/projects` 
 - `git clone https://github.com/pytorch/examples.git`

##### Interactive jobs (without a gpu)
1. Get an interactive session (you shouldn’t do processing on the head node)
     - Find partitions which are used for Interactive sessions (they'll have interactive in the name). For example:
     ```
    $ sinfo -o '%R;%N;%l' | column -s';' -t
    > PARTITION          NODELIST                           TIMELIMIT
    > Teach-Interactive  landonia[01,03,25]                 2:00:00
    > …
    > PGR-Standard       damnii[01-10]                      2:00:00
    > …
     ```
     - Use srun to get an interactive session on that partition. For example: 
     ```
    srun --partition=PGR-Standard --time=08:00:00 --mem=8000 --cpus-per-task=4 --pty bash
    ```
2. Run example MNIST code:
    - `cd ~/cluster-scripts/examples/mnist`
    - `conda activate pt`
    - `python main.py`

Please note: this is going to download data to the Distributed Filesystem (i.e. in your current working directory) and the code will access the data from there: this is not good practice on this cluster (because it will be very slow) and it will be changed in this guide at some point in the future - best practice says to store and access data in the scratch space of the node you’re running on

3. Exit your interactive session by running `exit`

##### Interactive jobs (without a gpu)
1. Launch a similar `srun` command using the `gres` command to request a GPU in your job:
    ```
    srun --partition=PGR-Standard --time=08:00:00 --mem=14000 --cpus-per-task=4 --gres=gpu:1 --pty bash
    ```
2. Run example MNIST code:
    - `cd ~/cluster-scripts/examples/mnist`
    - `conda activate pt`
    - `python main.py`

3. Exit your interactive session by running `exit`

##### Batch Jobs (non-interactive)

Repeat the above but this time using an sbatch script (non-interactive session). The command `sbatch` has many of the same arguments as `srun`, for example, add `--gres=gpu:1` if you would like to use one gpu

- `cd ~/cluster-scripts/examples/mnist`
- create a bash script, `mnist_expt.sh`, for slurm to run:
    ```
    #!/usr/bin/env bash
    conda activate pt
    python main.py
    ```
 - Run this script by running: `sbatch --time=08:00:00 --mem=14000 --cpus-per-task=4 --gres=gpu:1 mnist_expt.sh`
 - Observe your job running with: `squeue` 
 - You can get information about your jobs with `jobinfo -u s1234567` (replace `s1...` with your username)
 - Check out the log file with `cat slurm-*.out`. This will be in the working directory you were inside when you ran the `sbatch` command.

## Useful Documentation and Links

### Computing support
 - Main page: http://computing.help.inf.ed.ac.uk/cluster-computing
 - Explanation of filesystem, and best practice: http://computing.help.inf.ed.ac.uk/cluster-tips
### Slurm docs
 - Quick start: https://slurm.schedmd.com/quickstart.html
 - sbatch: https://slurm.schedmd.com/sbatch.html
 - srun: https://slurm.schedmd.com/srun.html
 - array jobs: https://slurm.schedmd.com/job_array.html
### Other:
 - Setting up VPN for self managed machines/laptops: http://computing.help.inf.ed.ac.uk/openvpn
 - Logging in to the informatics machines remotely: http://computing.help.inf.ed.ac.uk/external-login


## Example `.bashrc` file

You can keep one, `~/.bashrc`, and make an additional` ~/.bash_profile` that just runs the `~/.bashrc` (as we did earlier). This file should get run every time you log in. Different files get run depending on whether you’re logging in interactively, or non interactively to a login or non-login shell. For more information, see: https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html. For more information about bash start-up files for DICE machines, see http://computing.help.inf.ed.ac.uk/dice-bash. 

This is an example `~/.bashrc` you can use as guidance. 

```
# Allow resourcing of this file without continually lengthening path         
# i.e. this resets path to original on every source of this file
if [ -z $orig_path ]; then
  export orig_path=$PATH
else
  export PATH=$orig_path
fi

# This is so jupyter lab doesn't give the permission denied error
export XDG_RUNTIME_DIR=""

# This part is added automatically by the conda installation ================
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/${USER}/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/${USER}/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/${USER}/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/${USER}/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate
# ===========================================================================

# environment variable for your AFS home space
export AFS_HOME=/afs/inf.ed.ac.uk/user/${USER:0:3}/$USER

# Add cluster-scripts to path for easy use (explained in README)
export PATH=/home/${USER}/cluster-scripts:$PATH
source /home/${USER}/cluster-scripts/job-id-completion.sh

# Useful auto args for ls
alias ls='ls --color=auto'
alias ll='ls -alhF'
```

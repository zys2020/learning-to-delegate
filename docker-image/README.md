# 1 How to use Dockerfile
1. Build a image
```sh
docker build -t aghs:v3.0 .
# or load a image from a tar/tar.gz file
# docker load -i aghs_v3.0.tar.gz
docker run -id -p 9906:22 -p 9907:8888 -p 9908:9905 --name aghs_env aghs:v3.0 bash
docker exec -it aghs_env bash
# container
nohup /bin/bash /home/aghs/run.sh >> run.log 2>&1 &
```
2. Remote connection
```sh
ssh root@127.0.0.1 -p 9903
ssh root@118.195.176.251 -p 9903
```
# 2 How to use pretrained models

## 2.1 Python Environment Setup

### Miniconda and JupyterLab
```sh
mkdir /home/aghs/setup -p
cd /home/aghs/setup
wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.11.0-Linux-x86_64.sh
bash Miniconda3-py38_4.11.0-Linux-x86_64.sh -b

source ~/miniconda3/bin/activate
conda create -n vrp python=3.8 -y
conda activate vrp
pip install --upgrade pip
pip install jupyterlab
jupyter-lab --generate-config
cp /home/aghs/jupyter_lab_config.py ~/.jupyter/jupyter_lab_config.py
# run jupyter service
nohup jupyter-lab /home/aghs >> /home/aghs/jupyterlab.log 2>&1 &
```
### PyTorch and Torch Geometric
```sh
nohup pip install pyyaml tensorboard >> pip1.log 2>&1 &
nohup pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html >> pip2.log 2>&1 &
wget https://data.pyg.org/whl/torch-1.8.0%2Bcpu/torch_scatter-2.0.6-cp38-cp38-linux_x86_64.whl
nohup pip install torch_scatter-2.0.6-cp38-cp38-linux_x86_64.whl >> pip3.log 2>&1 &
wget https://data.pyg.org/whl/torch-1.8.0%2Bcpu/torch_sparse-0.6.12-cp38-cp38-linux_x86_64.whl
nohup pip install torch_sparse-0.6.12-cp38-cp38-linux_x86_64.whl >> pip4.log 2>&1 &
# key point
nohup pip install torch-geometric==1.7.2 >> pip5.log 2>&1 &
```

### Git Repo and Other tools
```sh
yum install git -y
cd /home/aghs
git clone git@github.com:zys2020/learning-to-delegate.git
cd learning-to-delegate
cd lkh3/LKH-3.0.4
make
cd ../hgs/HGS-CVRP/Program
make test
```

## 2.2 Execute Python Scripts
```sh
############### Start ###################

#### Generate Original VRP ####
export PTYPE=CVRP
export SPLIT=val # options: [train,val,test]
export N=500 # options: [500,1000,2000,3000]
export SAVE_DIR=generations/uniform_N$N
export N_INSTANCES=1
export N_CPUS=40

python generate_initial.py $SAVE_DIR $SPLIT $N --ptype $PTYPE --service_time 0.2 --max_window_width 1.0 --n_instances $N_INSTANCES --n_process $N_CPUS --n_threads_per_process 1
#### Generate Original VRP ####

#### Generate VRP subproblem ####
export K=5 # options: [5,10]
export DEPTH=40 # for K = 10: use 30 for N = [500,1000]; for K = 5: use [40,80,160] for N = [500,1000,2000]
export DATASET_DIR=$SAVE_DIR/subproblem_selection_lkh

python generate_multiprocess.py $DATASET_DIR $SPLIT --ptype $PTYPE --save_dir $SAVE_DIR --n_lkh_trials 500 --n_cpus $N_CPUS --index_start 0 --index_end $N_INSTANCES --beam_width 1 --n_route_neighbors $K --generate_depth $DEPTH
#### Generate VRP subproblem ####


###### Preprocess Data ######
python preprocess.py $DATASET_DIR val --ptype $PTYPE --beam_width 1 --n_route_neighbors $K --generate_depth $DEPTH --n_cpus $N_CPUS
###### Preprocess Data ######


###### Generate Trajectory Solution ######
export TRAIN_DIR=exps/uniform_N500_routeneighbors10/rotate_flip_augnode0.05_augroute0.005_xfc_ln_lr0.001
export GENERATE_CHECKPOINT_STEP=40000
export GENERATE_SAVE_DIR=$SAVE_DIR # This should be set as described above
export GENERATE_PARTITION=val # options: [val,test]
export GENERATE_SUFFIX=_val # A suffix which helps distinguish between different 

export DEPTH=400 # respectively for N = [500,1000,2000,3000], use [400,600,1200,2000] for K = 10 or [1000,2000,3000,4500] for K = 5
export N_RUNS=1 # use 1 for experimentation to save time

python supervised.py $DATASET_DIR $TRAIN_DIR --ptype $PTYPE --generate --step $GENERATE_CHECKPOINT_STEP --generate_partition $GENERATE_PARTITION --save_dir $GENERATE_SAVE_DIR --save_suffix $GENERATE_SUFFIX --generate_depth $DEPTH --generate_index_start 0 --generate_index_end $N_INSTANCES --n_lkh_trials 500 --n_trajectories $N_RUNS --n_cpus $N_CPUS --device cpu
###### Generate Trajectory Solution ######

############### End ###################
```

## 2.3 AGHS API
```sh
#### Generate Original VRP ####
export PTYPE=CVRPTW
export SPLIT=val # options: [train,val,test]
export N=500 # options: [500,1000,2000,3000]
export SAVE_DIR=generations/cvrptw_uniform_N$N
export N_INSTANCES=1
export N_CPUS=40

python generate_initial.py $SAVE_DIR $SPLIT $N --ptype CVRPTW --service_time 0.2 --max_window_width 1.0 --n_instances $N_INSTANCES --n_process $N_CPUS --n_threads_per_process 1
#### Generate Original VRP ####


#### Generate VRP subproblem ####
export K=5 # options: [5,10]
export DEPTH=40 # for K = 10: use 30 for N = [500,1000]; for K = 5: use [40,80,160] for N = [500,1000,2000]
export DATASET_DIR=$SAVE_DIR/subproblem_selection_lkh

python generate_multiprocess.py $DATASET_DIR $SPLIT --ptype $PTYPE --save_dir $SAVE_DIR --n_lkh_trials 500 --n_cpus $N_CPUS --index_start 0 --index_end $N_INSTANCES --beam_width 1 --n_route_neighbors $K --generate_depth $DEPTH
#### Generate VRP subproblem ####


###### Preprocess Data ######
python preprocess.py $DATASET_DIR val --ptype $PTYPE --beam_width 1 --n_route_neighbors $K --generate_depth $DEPTH --n_cpus $N_CPUS
###### Preprocess Data ######


###### Generate Trajectory Solution ######
export TRAIN_DIR=exps/cvrptw_uniform_N500_routeneighbors5_beam1_depth40/rotate_flip_augnode0.05_augroute0.005_xfc_ln_lr0.001
export GENERATE_CHECKPOINT_STEP=40000
export GENERATE_SAVE_DIR=$SAVE_DIR # This should be set as described above
export GENERATE_PARTITION=val # options: [val,test]
export GENERATE_SUFFIX=_val_ # A suffix which helps distinguish between different 

export DEPTH=400 # respectively for N = [500,1000,2000,3000], use [400,600,1200,2000] for K = 10 or [1000,2000,3000,4500] for K = 5
export N_RUNS=1 # use 1 for experimentation to save time

python supervised.py $DATASET_DIR $TRAIN_DIR --ptype $PTYPE --generate --step $GENERATE_CHECKPOINT_STEP --generate_partition $GENERATE_PARTITION --save_dir $GENERATE_SAVE_DIR --save_suffix $GENERATE_SUFFIX --generate_depth $DEPTH --generate_index_start 0 --generate_index_end $N_INSTANCES --n_lkh_trials 500 --n_trajectories $N_RUNS --n_cpus $N_CPUS --device cpu
###### Generate Trajectory Solution ######

############### End ###################
```

# Http API
- server
```sh
conda activate vrp
conda config --add channels conda-forge
conda install uwsgi -y

uwsgi --ini uwsgi.ini

uwsgi --http-socket :8888 --wsgi-file aghs_api.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191
```
- url: http://118.195.176.251:9904/aghs
- params:
```json
{
    'nodes': [
        {'x':0, 'y':0},
        {'x':0, 'y':0},
        {'x':0, 'y':0},
        {'x':0, 'y':0},
        {'x':0, 'y':0}
        ],
    'demands': [
        0, 1, 1, 1, 1
    ],
    'time_windows': [
        {'st':0, 'et':24*60},
        {'st':8*60, 'et':9*60},
        {'st':8*60, 'et':9*60},
        {'st':8*60, 'et':9*60},
        {'st':8*60, 'et':9*60}
    ],
    'service_time': 20,
    'only_lkh': "True"
}
```
- output:
```json
{
    routes: [0, 1, 2, 3, 4, 0]
}
```

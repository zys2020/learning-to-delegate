#!/bin/bash

nohup /usr/sbin/sshd -D >> /home/aghs/sshd.log 2>&1 &

if [ ! -d ~/.ssh ]; then
  mkdir ~/.ssh
fi
# github repository access authority
cp /home/aghs/id_rsa ~/.ssh/id_rsa
chmod -R 600 ~/.ssh/

# Miniconda and JupyterLab
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

# PyTorch and Torch Geometric
nohup pip install pyyaml tensorboard >> pip1.log 2>&1 &
nohup pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html >> pip2.log 2>&1 &
wget https://data.pyg.org/whl/torch-1.8.0%2Bcpu/torch_scatter-2.0.6-cp38-cp38-linux_x86_64.whl
nohup pip install torch_scatter-2.0.6-cp38-cp38-linux_x86_64.whl >> pip3.log 2>&1 &
wget https://data.pyg.org/whl/torch-1.8.0%2Bcpu/torch_sparse-0.6.12-cp38-cp38-linux_x86_64.whl
nohup pip install torch_sparse-0.6.12-cp38-cp38-linux_x86_64.whl >> pip4.log 2>&1 &
nohup pip install torch-geometric==1.7.2 >> pip5.log 2>&1 &

# Git Repo and Other tools
cd /home/aghs
git clone git@github.com:zys2020/learning-to-delegate.git
cd learning-to-delegate
cd lkh3/LKH-3.0.4
make
cd ../hgs/HGS-CVRP/Program
make test

# aghs api
pip install flask
conda config --add channels conda-forge
conda install uwsgi -y
# run api server
uwsgi --ini uwsgi.ini
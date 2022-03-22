#/bin/bash
cd /home/aghs/learning-to-delegate
mkdir -p log
/root/miniconda3/envs/vrp/bin/uwsgi --ini uwsgi.ini

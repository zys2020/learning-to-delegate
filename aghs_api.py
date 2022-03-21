import os
import shutil
from util import *
from pathlib import Path
from subprocess import check_call
from datetime import datetime
from datetime import timedelta

from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/aghs_api", methods=['POST'])
def aghs_api():
    data = json.loads(request.form['data'])
    now = datetime.utcnow() + timedelta(hours=8)
    path = "./input_data_of_aghs_api"
    print(os.path.curdir)
    if not os.path.exists(path):
        os.makedirs(path)
    filename = now.strftime("%Y-%m-%d_%H-%M-%S") + ".npz"
    filename = os.path.join(path, filename)
    nodes = np.array([(item['x'], item['y']) for item in data['nodes']], dtype=np.float16)
    demands = np.array(data['demands'], dtype=np.int8)
    window = np.array([(item['st'], item['et']) for item in data['time_windows']], dtype=np.float16)
    service_time = np.array(data['service_time'], dtype=np.float16)
    np.savez(filename, nodes=nodes, demands=demands, window=window, service_time=service_time)
    only_lkh = True if data['only_lkh'] == "True" else False
    generate_problem(original_data_path=filename, only_lkh=only_lkh)
    routes = parse_model_output(only_lkh)
    output_json = json.dumps(routes)

    filename = now.strftime("%Y-%m-%d_%H-%M-%S") + "_routes.json"
    filename = os.path.join(path, filename)
    with open(filename, 'w') as f:
        f.write(output_json)
    if not only_lkh:
        filename = "/home/aghs/learning-to-delegate/exps/cvrptw_uniform_N500_routeneighbors5_beam1_depth40/rotate_flip_augnode0.05_augroute0.005_xfc_ln_lr0.001/generations_val_beam1_depth400_lkh500/40000/0.npz"
        shutil.copyfile(filename, os.path.join(path, now.strftime("%Y-%m-%d_%H-%M-%S") + "_0.npz"))
        shutil.rmtree("/home/aghs/learning-to-delegate/exps/cvrptw_uniform_N500_routeneighbors5_beam1_depth40/rotate_flip_augnode0.05_augroute0.005_xfc_ln_lr0.001/generations_val_beam1_depth400_lkh500/")
    return output_json


def load_gens(data_path):
    path = data_path / "0.npz"
    if not path.exists():
        raise RuntimeError(f'File: {path} not exists')
    output_data = np.load(path, allow_pickle=True)

    init_routes = unpack_routes(output_data['routes'])

    subproblem_routes = unpack_routes(output_data['lkh_routes'][-1])

    node_indices = output_data['node_indices'][-1]

    output_routes = []
    for route in subproblem_routes:
        new_route = node_indices[route - 1].tolist()
        output_routes.append(new_route)

    sub_route_set = []
    for node in output_data['node_indices'][-1]:
        for route in init_routes:
            route = route.tolist()
            if node in route:
                if route not in sub_route_set:
                    sub_route_set.append(route)

    for route in init_routes:
        route = route.tolist()
        if route in sub_route_set:
            continue
        output_routes.append(route)

    return output_routes


def parse_model_output(only_lkh=False):
    if only_lkh:
        filename = "generations/cvrptw_uniform_N500/problems_val.npz"
        data = np.load(filename)
        routes = unpack_routes(data['routes'][0])
        return [route.tolist() for route in routes]
    instances = 1
    runs = 1

    exp = Path('.') / 'exps' / \
        'cvrptw_uniform_N500_routeneighbors5_beam1_depth40/rotate_flip_augnode0.05_augroute0.005_xfc_ln_lr0.001'

    routes = load_gens(exp / 'generations_val_beam1_depth400_lkh500/40000')
    return routes


def generate_problem(original_data_path='./sample.npz', only_lkh=False):
    params = dict(
        PTYPE="CVRPTW",
        SPLIT="val",
        N="500",
        SAVE_DIR="generations/cvrptw_uniform_N500",
        N_INSTANCES="1",
        N_CPUS="40"
        )
    cmd = [
        "/root/miniconda3/envs/vrp/bin/python", 
        "generate_initial.py", 
        params["SAVE_DIR"],
        params["SPLIT"],
        params["N"],
        "--ptype", "CVRPTW", 
        "--service_time", "0.0",
        "--max_window_width", "1.0",
        "--n_instances", params["N_INSTANCES"],
        "--n_process", params["N_CPUS"],
        "--n_threads_per_process", "1",
        "--original_data_path", original_data_path
        ]
    cwd = "/home/aghs/learning-to-delegate"
    check_call(cmd, cwd=cwd)
    if only_lkh:
        return

    #### Generate VRP subproblem ####
    params['K'] = '5'
    params['DEPTH'] = '40'
    params['DATASET_DIR'] = params['SAVE_DIR'] + "/subproblem_selection_lkh"

    cmd = [
        "/root/miniconda3/envs/vrp/bin/python", 
        "generate_multiprocess.py", 
        params["DATASET_DIR"],
        params["SPLIT"],
        "--ptype", "CVRPTW", 
        "--save_dir", params['SAVE_DIR'],
        "--n_lkh_trials", "500",
        "--n_cpus", params["N_CPUS"],
        "--index_start", "0",
        "--index_end", params['N_INSTANCES'],
        "--beam_width", '1',
        "--n_route_neighbors", params['K'],
        "--generate_depth", params['DEPTH']
    ]
    check_call(cmd, cwd=cwd)


    # ###### Preprocess Data ######
    cmd = [
        "/root/miniconda3/envs/vrp/bin/python", 
        "preprocess.py", 
        params["DATASET_DIR"],
        params["SPLIT"],
        "--ptype", "CVRPTW", 
        "--beam_width", '1',
        "--n_route_neighbors", params['K'],
        "--generate_depth", params['DEPTH'],
        "--n_cpus", params["N_CPUS"],
    ]
    check_call(cmd, cwd=cwd)
    # ###### Preprocess Data ######


    # ###### Generate Trajectory Solution ######
    params['TRAIN_DIR'] = 'exps/cvrptw_uniform_N500_routeneighbors5_beam1_depth40/rotate_flip_augnode0.05_augroute0.005_xfc_ln_lr0.001'
    params['GENERATE_CHECKPOINT_STEP'] = '40000'
    params['GENERATE_SAVE_DIR'] = params['SAVE_DIR']
    params['GENERATE_PARTITION'] = 'val'
    params['GENERATE_SUFFIX'] = '_val'
    params['DEPTH'] = '400'
    params['N_RUNS'] = '1'

    cmd = [
        "/root/miniconda3/envs/vrp/bin/python", 
        "supervised.py", 
        params["DATASET_DIR"],
        params["TRAIN_DIR"],
        "--ptype", "CVRPTW", 
        "--generate",
        "--step", params['GENERATE_CHECKPOINT_STEP'],
        "--generate_partition", params['GENERATE_PARTITION'],
        "--save_dir", params["GENERATE_SAVE_DIR"],
        "--save_suffix", params['GENERATE_SUFFIX'],
        "--generate_depth", params['DEPTH'],
        "--beam_width", '1',
        "--n_route_neighbors", params['K'],
        "--generate_depth", params['DEPTH'],
        "--generate_index_start", "0",
        "--generate_index_end", params['N_INSTANCES'],
        "--n_lkh_trials", "500",
        "--n_trajectories", params['N_RUNS'],
        "--n_cpus", params["N_CPUS"],
        "--device", "cpu"
    ]
    check_call(cmd, cwd=cwd)


# if __name__ == '__main__':
    # print(aghs_api())
    # app.run(host='0.0.0.0')
    # generate_problem()
    # routes = parse_model_output()
    # print(len(routes), routes)


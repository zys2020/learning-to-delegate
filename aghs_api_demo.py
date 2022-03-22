import json
import requests
import numpy as np

url = "http://118.195.176.251:9908/aghs_api"

data = np.load("./sample.npz")
post_data = {}
post_data['nodes'] = [{"x": str(item[0]), "y": str(item[1])} for item in data['nodes']]
post_data['demands'] = [str(item) for item in data['demands']]
post_data['time_windows'] = [{"st": str(item[0]), "et": str(item[1])} for item in data['window']]
post_data['service_time'] = "20"
# When only_lkh is "True", the pretrained model is invoked and consumes about 5 min. 
# Otherwise, the pure lhk heuristic method is invoked and consumes about 10 s.   
post_data['only_lkh'] = "True"

post_data = json.dumps(post_data)
response = requests.post(url=url, data={'data':post_data})
print(response)
print(response.json())

'''json
post_data = 
{
    # 501个结点，第1个是车库
    'nodes': [
        {'x':0, 'y':0},
        {'x':0, 'y':0},
        {'x':0, 'y':0},
        {'x':0, 'y':0},
        {'x':0, 'y':0}
        ],
    # 501个结点的需求，第1个是车库需求0
    'demands': [
        0, 1, 1, 1, 1
    ],
    # 501个结点的开始和结束服务时间窗，第1个是车库
    'time_windows': [
        {'st':0, 'et':24*60},
        {'st':8*60, 'et':9*60},
        {'st':8*60, 'et':9*60},
        {'st':8*60, 'et':9*60},
        {'st':8*60, 'et':9*60}
    ],
    'service_time': 20,
    # "True" 不使用预训练模型; "False"使用预训练模型
    'only_lkh': "True"
}
```
- output:
```json
{
    # 输出多条路径的索引，例如从0>1>2>0和0>3>4>0两条路径
    routes: [[1, 2], [3, 4]]
}
'''

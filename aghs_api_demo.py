from urllib import response
import requests
import numpy as np

url = "http://118.195.176.251:9904/aghs_api"

data = np.load("./sample.npz")
post_data = {}
post_data['nodes'] = [{"x": str(item[0]), "y": str(item[1])} for item in data['nodes']]
post_data['demands'] = [str(item) for item in data['demands']]
post_data['time_windows'] = [{"st": str(item[0]), "et": str(item[1])} for item in data['window']]
post_data['service_time'] = "20"
post_data['only_lkh'] = "True"
import json
post_data = json.dumps(post_data)
response = requests.post(url=url, data={'data':post_data})
print(response)
print(response.content)
import numpy as np
import json

def json_load(fpath):
    with open(fpath, 'r') as f:
        return json.load(f)
    
def json_save(fpath, data):
    with open(fpath,'w') as f:
        json.dump(data, f, cls=NpEncoder)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
"""
@author: ek675

"""
import os
import warnings

warnings.filterwarnings('ignore')

for dirname, _, filenames in os.walk('/data/raw'):
    for filename in filenames:
        os.path.join(dirname, filename)

base_dir = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR  = os.path.join(base_dir, '..', 'Data', 'Output')
DATA_DIR = os.path.join(base_dir, '..', 'Data', 'Raw')

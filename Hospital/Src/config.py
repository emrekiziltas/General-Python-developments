"""
@author: ek675

"""
import os
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

filenames = [f for f in Path('/data/raw').rglob('*') if f.is_file()]

base_dir = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR  = os.path.join(base_dir, '..', 'Data', 'Output')
DATA_DIR = os.path.join(base_dir, '..', 'Data', 'Raw')

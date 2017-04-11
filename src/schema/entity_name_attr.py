import sys
import os
from .schema import load_entity
from ..IOUtil import result_dir



if __name__ == "__main__":
    e_set = load_entity()
    load(os.path.join(result_dir, 'freebase_merged'))

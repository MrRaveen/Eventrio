import sys
from .hook import Hook 

def execute():
    sys.meta_path.insert(0, Hook())
execute()
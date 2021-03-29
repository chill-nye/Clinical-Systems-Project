#needs this to fix the fact that modINFO74000 module is not in the same directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import modINFO74000
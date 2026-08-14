import runpy
import sys

import numpy as np


if not hasattr(np, "trapezoid"):
    np.trapezoid = np.trapz

sys.argv[0] = sys.argv[1]
runpy.run_path(sys.argv.pop(1), run_name="__main__")

import sys
import torch
import numpy as np
import pandas as pd

print(f"1. Python version: {sys.version}")
print(f"2. PyTorch version: {torch.__version__}")
print(f"3. if there is CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   - CUDA version: {torch.version.cuda}")
    print(f"   - GPU version: {torch.cuda.get_device_name(0)}")
else:
    print("   - Now using CPU")
print(f"4. Numpy version: {np.__version__}")
print(f"5. Pandas version: {pd.__version__}")


